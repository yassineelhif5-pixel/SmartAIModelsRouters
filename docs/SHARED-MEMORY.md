# Shared session memory across models and nodes

## Purpose

A multi-provider workflow needs one consistent HIF memory so a researcher, architect, coder, tester and reviewer can reuse approved facts and completed outputs without repeating work.

## Memory layers

1. Session facts: approved goals, constraints, terminology, preferences and decisions.
2. Role registry: specialist role definitions, responsibilities, output schemas and permitted tools.
3. Node outputs: task results, validation status, model/usage metadata and artifact references.
4. Artifact index: file paths, hashes, excerpts, summaries and provenance.
5. Session summary: current state, decisions, open questions and next actions.

## Session identity

All nodes in one run use the same session_id. Records are tagged with session_id, node_id, role, provider/model, timestamp and source. New user requests can start a new session or deliberately resume an existing one.

## Retrieval policy

Do not inject all memory into every model prompt. Retrieve only the required role definition, relevant facts, dependency outputs, artifact excerpts and latest summary. Apply size limits and provenance. Invalidate summaries when source artifact hashes change.

## Cross-provider sharing

HIF passes explicit structured content from one provider to another. This is a task-context handoff, not native-session migration. Never attempt to extract hidden reasoning, private chain-of-thought, undisclosed caches or internal provider state.

## Privacy

Keep local SQLite memory on the user's machine by default. Avoid persisting raw conversations by default. Store secrets separately; never put provider API keys in memory. Apply privacy classification and provider allowlists before sending any content to a remote model. Support per-session deletion and data retention controls before enabling multi-user remote storage.

## Data quality

Distinguish user-approved facts from model-generated suggestions. Store provenance and status. Surface conflicting facts instead of silently overwriting them.
