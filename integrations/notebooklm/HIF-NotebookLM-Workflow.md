# HIF + NotebookLM — Companion Workflow

> This is a workflow guide, not a native NotebookLM Agent Skill, plugin or API integration. NotebookLM controls its own notebooks, source imports, account limits and interface.

## Purpose

Use HIF to prepare a well-structured, source-grounded research package. Use NotebookLM to explore and synthesize the sources the user has imported. Return important claims to HIF for verification and final delivery.

## Workflow

### 1. Define the research mission in HIF

Ask HIF to identify:
- the main research question;
- sub-questions and scope boundaries;
- required source types and date range;
- evidence quality requirements;
- output format and definition of done.

### 2. Prepare a compact source pack

Where the user has provided source files or enabled authorized research tools, HIF may prepare:
- source index with title, publisher/author, date and URL/path;
- short description of why each source is relevant;
- glossary and entity list;
- timeline or comparison matrix;
- research questions to ask NotebookLM;
- known gaps, contradictions and source limitations.

Do not include secrets or confidential documents unless the user explicitly authorizes their use and the destination is appropriate.

### 3. Import sources into NotebookLM

The user manually adds the source files/URLs using NotebookLM's supported interface. HIF must not claim to have created a notebook or imported sources unless a supported Google integration actually performs and confirms the action.

### 4. Ask NotebookLM source-grounded questions

Suggested prompt:

    Using only the sources in this notebook:
    1. Answer the research questions in the attached HIF brief.
    2. Cite the source(s) supporting each important claim.
    3. Distinguish direct evidence, inference and uncertainty.
    4. Identify contradictions between sources.
    5. List questions that cannot be answered from the available sources.
    Do not invent missing facts.

### 5. Return results to HIF

The user exports, copies or attaches NotebookLM notes/output to HIF. HIF then:
- checks claims against the original source pack where available;
- verifies dates, quotations and references;
- resolves or reports contradictions;
- updates the evidence map;
- prepares the final answer with validated conclusions and remaining work.

## Data and integration boundary

- NotebookLM is not treated as a general-purpose HIF agent runtime.
- No direct notebook API, MCP server, autonomous source upload or cross-account subscription access is assumed.
- NotebookLM's native source grounding remains authoritative for its notebook; HIF performs additional validation only against sources it can actually inspect.
- User action is required for notebook/source import unless a future official Google integration is implemented and enabled.

## Completion checklist

- [ ] Research objective and scope confirmed
- [ ] Source pack prepared by HIF
- [ ] User imported sources into NotebookLM
- [ ] NotebookLM answers exported or returned to HIF
- [ ] Key claims checked against source evidence
- [ ] Contradictions and evidence gaps documented
- [ ] Final deliverable and remaining actions provided
