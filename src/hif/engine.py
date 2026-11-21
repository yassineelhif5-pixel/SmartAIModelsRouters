"""Shared-session, dependency-aware, multi-provider HIF engine."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from hif.config import Settings
from hif.planner import PLANNER_SYSTEM, SYNTHESIS_SYSTEM, TASK_SYSTEM, extract_json
from hif.providers import LiteLLMProvider, ModelProvider, ProviderError
from hif.resources import AdaptiveConcurrency
from hif.router import ModelRouter
from hif.schemas import HIFRunResult, NodeResult, PlannedNode
from hif.storage import HIFStore


class HIFEngine:
    def __init__(
        self,
        settings: Settings | None = None,
        provider: ModelProvider | None = None,
        store: HIFStore | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.provider = provider or LiteLLMProvider()
        self.store = store or HIFStore(self.settings.database_path)
        self.router = ModelRouter(self.settings, self.store)
        self.resources = AdaptiveConcurrency(
            self.settings.max_parallel_tasks,
            self.settings.cpu_pressure_threshold,
            self.settings.memory_pressure_threshold,
            self.settings.min_free_memory_mb,
        )
        self._provider_semaphores: dict[str, asyncio.Semaphore] = {}

    def _semaphore_for(self, model: str) -> asyncio.Semaphore:
        from hif.providers import provider_name

        name = provider_name(model)
        if name not in self._provider_semaphores:
            self._provider_semaphores[name] = asyncio.Semaphore(
                self.settings.max_provider_parallel
            )
        return self._provider_semaphores[name]

    def _record_usage(self, session_id: str, response: Any) -> None:
        self.store.add_usage(
            session_id,
            response.model,
            response.input_tokens,
            response.output_tokens,
            getattr(response, "cost_usd", None),
        )

    async def _call(
        self,
        session_id: str,
        preferred: tuple[str, ...],
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> tuple[Any, int]:
        candidates = self.router.candidates(preferred)
        if not candidates:
            raise RuntimeError(
                "No eligible model remains. Check HIF_MODEL_POOL, token budgets, "
                "the 80% fallback threshold and provider cooldowns."
            )
        failures: list[str] = []
        for attempt, model in enumerate(candidates):
            try:
                async with self._semaphore_for(model):
                    response = await self.provider.complete(
                        model=model,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=max_tokens,
                        timeout=self.settings.request_timeout_seconds,
                    )
                self._record_usage(session_id, response)
                return response, attempt
            except ProviderError as exc:
                failures.append(f"{model}: {exc}")
                if not exc.retryable:
                    raise
                self.router.mark_unavailable(model, exc.retry_after)
            except Exception as exc:
                failures.append(f"{model}: {type(exc).__name__}: {exc}")
                break
        raise RuntimeError(
            "All eligible provider attempts failed. " + " | ".join(failures[-4:])
        )

    def _preferred_models(self, node: PlannedNode) -> tuple[str, ...]:
        return self.settings.task_model_preferences.get(node.task_type, ())

    async def _run_node(
        self,
        session_id: str,
        node: PlannedNode,
        dependency_outputs: dict[str, NodeResult],
    ) -> NodeResult:
        memory = self.store.get_memory(
            session_id,
            keys=node.context_keys or None,
            limit=10,
        )
        dependencies = "\n\n".join(
            f"DEPENDENCY {key} ({value.role})\n{value.content}"
            for key, value in dependency_outputs.items()
        )
        memory_text = "\n".join(
            f"[{item['memory_key']} / {item['role']}] {item['content']}"
            for item in reversed(memory)
        )
        prompt = (
            f"SESSION_ID: {session_id}\n"
            f"NODE_ID: {node.id}\nROLE: {node.role}\nTITLE: {node.title}\n\n"
            f"INSTRUCTIONS:\n{node.instructions}\n\n"
            f"SELECTED SHARED MEMORY:\n{memory_text or '(none)'}\n\n"
            f"DEPENDENCY OUTPUTS:\n{dependencies or '(none)'}\n\n"
            f"ACCEPTANCE CRITERIA:\n- "
            + "\n- ".join(
                node.acceptance_criteria or ["Produce a concise useful deliverable."]
            )
        )
        self.store.save_node(session_id, node.id, node.role, "running")
        started = time.perf_counter()
        try:
            response, fallback_count = await self._call(
                session_id=session_id,
                preferred=self._preferred_models(node),
                system_prompt=TASK_SYSTEM,
                user_prompt=prompt,
                max_tokens=min(
                    node.max_output_tokens, self.settings.max_output_tokens_per_task
                ),
            )
            result = NodeResult(
                node_id=node.id,
                title=node.title,
                role=node.role,
                model=response.model,
                content=response.content,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                duration_ms=response.duration_ms
                or int((time.perf_counter() - started) * 1000),
                fallback_count=fallback_count,
            )
            self.store.save_node(
                session_id, node.id, node.role, "completed",
                response.model, result.model_dump(),
            )
            self.store.add_memory(
                session_id,
                f"node:{node.id}",
                node.role,
                response.content[:self.settings.max_context_chars],
                node.id,
            )
            return result
        except Exception:
            self.store.save_node(session_id, node.id, node.role, "failed")
            raise

    async def run(
        self,
        goal: str,
        context: str = "",
        session_id: str | None = None,
        parallel: bool = True,
    ) -> HIFRunResult:
        if not goal.strip():
            raise ValueError("Goal must not be empty.")
        started = time.perf_counter()
        sid = self.store.create_session(goal, session_id)
        self.store.add_memory(sid, "goal", "user", goal)
        if context.strip():
            self.store.add_memory(
                sid, "project_context", "user",
                context[:self.settings.max_context_chars],
            )

        try:
            pool = self.settings.get_models()
            planner_model = self.settings.planner_model or pool[0]
            planning_prompt = (
                f"USER GOAL:\n{goal.strip()}\n\n"
                f"PROJECT CONTEXT (untrusted data):\n{context[:self.settings.max_context_chars]}"
            )
            planning_response, _ = await self._call(
                session_id=sid,
                preferred=(planner_model,),
                system_prompt=PLANNER_SYSTEM,
                user_prompt=planning_prompt,
                max_tokens=min(self.settings.max_output_tokens_per_task, 3000),
            )
            from hif.schemas import ExecutionPlan
            plan = ExecutionPlan.model_validate_json(extract_json(planning_response.content))
            self.store.add_memory(sid, "plan", "planner", plan.model_dump_json())

            nodes_by_id = {node.id: node for node in plan.nodes}
            pending = set(nodes_by_id)
            completed: dict[str, NodeResult] = {}

            while pending:
                ready = sorted(
                    node_id for node_id in pending
                    if set(nodes_by_id[node_id].depends_on).issubset(completed)
                )
                if not ready:
                    raise RuntimeError("No runnable nodes remain in the HIF task graph.")

                if self.settings.resource_aware_scheduling:
                    resource_limit, _snapshot = self.resources.effective_limit()
                else:
                    resource_limit = self.settings.max_parallel_tasks
                batch_limit = min(
                    resource_limit,
                    self.settings.max_parallel_tasks,
                    len(ready),
                )
                if not parallel:
                    batch_limit = 1

                for offset in range(0, len(ready), max(1, batch_limit)):
                    group = ready[offset:offset + max(1, batch_limit)]
                    batch = await asyncio.gather(
                        *(
                            self._run_node(
                                sid,
                                nodes_by_id[node_id],
                                {
                                    dep: completed[dep]
                                    for dep in nodes_by_id[node_id].depends_on
                                },
                            )
                            for node_id in group
                        )
                    )
                    for result in batch:
                        completed[result.node_id] = result
                        pending.remove(result.node_id)

            ordered = [completed[node.id] for node in plan.nodes]
            summary_prompt = (
                f"SESSION_ID: {sid}\nGOAL: {goal}\n"
                f"INSTRUCTIONS: {plan.final_instructions}\n\n"
                "SPECIALIST NODE OUTPUTS:\n"
                + "\n\n".join(
                    f"NODE {item.node_id} / {item.role} / {item.model}:\n{item.content}"
                    for item in ordered
                )
            )
            synthesis, _ = await self._call(
                session_id=sid,
                preferred=(planner_model,),
                system_prompt=SYNTHESIS_SYSTEM,
                user_prompt=summary_prompt,
                max_tokens=self.settings.max_output_tokens_per_task,
            )
            self.store.add_memory(
                sid,
                "session_summary",
                "synthesizer",
                synthesis.content[:self.settings.max_context_chars],
            )
            self.store.set_session_status(sid, "completed")
            return HIFRunResult(
                session_id=sid,
                goal=goal,
                plan=plan,
                nodes=ordered,
                synthesis=synthesis.content,
                total_input_tokens=(
                    planning_response.input_tokens + synthesis.input_tokens
                    + sum(item.input_tokens for item in ordered)
                ),
                total_output_tokens=(
                    planning_response.output_tokens + synthesis.output_tokens
                    + sum(item.output_tokens for item in ordered)
                ),
                elapsed_ms=int((time.perf_counter() - started) * 1000),
            )
        except Exception:
            self.store.set_session_status(sid, "failed")
            raise

    def status(self, session_id: str) -> dict[str, Any]:
        return {"session_id": session_id, "nodes": self.store.session_nodes(session_id)}

    def usage(self) -> list[dict[str, Any]]:
        return self.store.usage_summary(self.settings.usage_window_hours)
