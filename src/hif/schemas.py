"""Typed structures used by the HIF planner and node scheduler."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


TaskType = Literal[
    "analysis", "research", "coding", "testing", "review", "documentation", "architecture", "infrastructure", "security", "general"
]


class PlannedNode(BaseModel):
    id: str = Field(min_length=1, max_length=48)
    title: str = Field(min_length=1, max_length=180)
    role: str = Field(min_length=1, max_length=80)
    instructions: str = Field(min_length=1)
    task_type: TaskType = "general"
    depends_on: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    context_keys: list[str] = Field(default_factory=list)
    max_output_tokens: int = Field(default=1600, ge=64, le=8192)

    @field_validator("depends_on", "context_keys")
    @classmethod
    def unique_values(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Duplicate values are not allowed.")
        return values


class ExecutionPlan(BaseModel):
    goal: str
    nodes: list[PlannedNode] = Field(min_length=1, max_length=12)
    final_instructions: str = "Consolidate all specialist outputs into one answer."

    @model_validator(mode="after")
    def validate_graph(self) -> "ExecutionPlan":
        by_id = {node.id: node for node in self.nodes}
        if len(by_id) != len(self.nodes):
            raise ValueError("Node IDs must be unique.")
        for node in self.nodes:
            missing = set(node.depends_on) - set(by_id)
            if missing:
                raise ValueError(f"Node {node.id} has unknown dependencies: {sorted(missing)}")
            if node.id in node.depends_on:
                raise ValueError(f"Node {node.id} cannot depend on itself.")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                raise ValueError("The HIF task graph contains a dependency cycle.")
            if node_id in visited:
                return
            visiting.add(node_id)
            for dependency in by_id[node_id].depends_on:
                visit(dependency)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in by_id:
            visit(node_id)
        return self


class ProviderUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float | None = None


class NodeResult(BaseModel):
    node_id: str
    title: str
    role: str
    model: str
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    fallback_count: int = 0
    status: Literal["completed", "failed"] = "completed"


class HIFRunResult(BaseModel):
    session_id: str
    goal: str
    plan: ExecutionPlan
    nodes: list[NodeResult]
    synthesis: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    elapsed_ms: int = 0
