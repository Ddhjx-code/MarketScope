# Three-Agent Pipeline Design

## Requirements Restatement

Build a three-stage analysis pipeline for MarketScope that:
1. Collects market data via search and statistics tools (Research)
2. Performs multi-dimensional analysis on collected data (Analysis)
3. Generates a structured JSON report (Report)

Each stage is a separate LLM conversation with focused context and clear data handoff.

## Architecture

### Directory Structure

```
src/agent/
├── executor.py              # Single reusable Executor
├── pipeline.py              # Three-stage orchestrator (NEW)
├── prompts/                 # System prompts (NEW)
│   ├── __init__.py
│   ├── researcher.py        # Research Agent system prompt
│   ├── analyst.py           # Analysis Agent system prompt
│   └── reporter.py          # Report Agent system prompt
├── skills/                  # Skill definitions (NEW)
│   ├── __init__.py
│   ├── loader.py            # YAML skill loader
│   └── definitions/         # Skill YAML files
│       ├── market_analysis.yaml
│       ├── competitor_analysis.yaml
│       ├── trend_analysis.yaml
│       ├── demand_analysis.yaml
│       └── report_generation.yaml
└── tools/                   # Tool implementations (existing)
    ├── registry.py
    ├── search_tools.py
    └── national_stats_tools.py
```

### Three-Layer Prompt System

| Layer | Content | Location | Loaded By |
|-------|---------|----------|-----------|
| **System Prompt** | Agent role, goal, output format | `prompts/*.py` | Executor (fixed per stage) |
| **Skill Prompt** | Specific analysis instructions | `skills/definitions/*.yaml` | Pipeline (injected per stage) |
| **Meta Prompt** | Workflow orchestration, stage transitions | `pipeline.py` code | IndustryAnalyzer |

### Agent Responsibilities

**Research Agent** (Phase 1):
- System: "You are an industry research assistant. Collect market data by calling available tools."
- Skills: market_analysis, competitor_analysis, trend_analysis, demand_analysis
- Tools: 4 search tools + 6 national stats tools
- Output: `raw_data` dict with search results per dimension

**Analysis Agent** (Phase 2):
- System: "You are an industry analyst. Analyze the provided research data across multiple dimensions."
- Skills: analysis evaluation skills (defined in YAML)
- Tools: none (pure reasoning on provided data)
- Input: user_input + raw_data
- Output: `structured_analysis` dict with evaluations, opportunities, risks

**Report Agent** (Phase 3):
- System: "You are a report writing expert. Format the analysis into a structured JSON report."
- Skills: report_generation
- Tools: none
- Input: structured_analysis
- Output: final_report matching the JSON schema in AGENTS.md

### Data Flow

```
user_input ("社交类APP，兴趣小组聊天")
    │
    ▼
┌─ Research Agent ──────────────────────────────┐
│ system_prompt: prompts/researcher.py          │
│ skills: market + competitor + trend + demand  │
│ tools: all 10 tools                           │
│ output: raw_data {                            │
│   market_size: [...],                         │
│   competitors: [...],                         │
│   trends: [...],                              │
│   user_demand: [...]                          │
│ }                                             │
└───────────────────┬───────────────────────────┘
                    │ raw_data
                    ▼
┌─ Analysis Agent ──────────────────────────────┐
│ system_prompt: prompts/analyst.py             │
│ skills: analysis evaluation                   │
│ tools: none                                   │
│ output: structured_analysis {                 │
│   market_analysis: {...},                     │
│   competitor_analysis: {...},                 │
│   trend_analysis: {...},                      │
│   opportunity_assessment: {...}               │
│ }                                             │
└───────────────────┬───────────────────────────┘
                    │ structured_analysis
                    ▼
┌─ Report Agent ────────────────────────────────┐
│ system_prompt: prompts/reporter.py            │
│ skills: report_generation                     │
│ tools: none                                   │
│ output: final_report {                        │
│   app_type, market_analysis,                  │
│   competitor_analysis, trend_analysis,        │
│   opportunity_assessment, recommendations     │
│ }                                             │
└───────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Single reusable Executor** — receives `system_prompt + skills + tools + input`, not bound to any specific role
2. **Skills are YAML configs** — declarative with `name`, `description`, `prompt`, `required_tools`
3. **Meta-prompt in pipeline code** — `IndustryAnalyzer.analyze()` hardcodes stage transition logic
4. **No RAG/vectorization** — data volume (~35K tokens) is well within context limits
5. **3 LLM conversations** — focused context per stage, easier debugging, parallelizable

### Executor Changes

- Remove duplicate `execute` method
- Accept `system_prompt` parameter
- Accept optional `skills` list to inject into prompt
- Accept optional `tools` override (default: all from registry)

### Pipeline Orchestration

`IndustryAnalyzer.analyze()` becomes the orchestrator:
1. Create Research Agent → execute → get raw_data
2. Create Analysis Agent → execute with raw_data → get structured_analysis
3. Create Report Agent → execute with structured_analysis → return final_report

## Risks

- **MEDIUM**: LLM may not call all expected tools in Research phase — mitigate with skill prompts that explicitly guide tool usage
- **MEDIUM**: National stats tools are stubs (return MCP_CALL_REQUESTED) — real execution depends on MCP runtime
- **LOW**: Executor changes are small and focused
