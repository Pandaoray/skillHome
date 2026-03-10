---
name: my-god
description: Human-assisted AI programming workflow for medium-to-large projects. Orchestrate an Agent Team to transform a PM's one-line requirement into a full development pipeline, from requirement clarification to code delivery and PR creation. Use when user says "/myGod", "my-god", "启动大神模式", "召唤大仙", "大神显灵", or wants to start an automated dev workflow. Supports three modes - full (default, 7-step pipeline), quick ("/myGod quick", skip architecture), hotfix ("/myGod hotfix", minimal flow for urgent fixes).
---

# myGod - AI Dev Workflow

Transform a one-line requirement into a complete development pipeline via Agent Team collaboration.

## Command Parsing

| Input | Mode | Description |
|-------|------|-------------|
| `/myGod {requirement}` | full | Complete 7-step pipeline |
| `/myGod quick {requirement}` | quick | Skip architecture, simplified flow |
| `/myGod hotfix {requirement}` | hotfix | Minimal flow for urgent bug fixes |
| `/myGod status` | - | Read workflow-state.json |
| `/myGod report` | - | Read latest workflow-summary.md |

## Phase Overview

| Phase | Full | Quick | Hotfix |
|-------|:----:|:-----:|:------:|
| 1. Requirement Clarification | Multi-round | 1 round | 1 round |
| 2. Architecture Design | Yes | Skip | Skip |
| 3. Task Decomposition | Yes | Simplified | Skip |
| 4. Development | Parallel team | Single agent | Single agent |
| 5. Unit Validation | Yes | Yes | Skip |
| 6. Integration | Yes | Skip | Skip |
| 7. Code Review | Yes | Simplified | Skip |
| 8. Final Validation | Full | Related tests | Smoke test |
| 9. Git Integration | Yes | Yes | Yes |

## Execution Steps

### Step 0: Initialize

1. Generate workflow ID: `workflow-{YYYYMMDD}-{HHMMSS}`
2. Create working directory: `.ai/myGod/workflow-{timestamp}/` with subdirs `04-development/`, `context-summaries/`
3. Save original requirement to `00-initial-requirement.md`
4. Initialize `workflow-state.json` (see [design-spec](references/design-spec.md) section 七 for schema)
5. If git repo, create branch: `feature/myGod-{short-desc}-{timestamp}`
6. Update symlink: `.ai/myGod/latest` -> current workflow dir

### Step 1: Requirement Clarification (Human interaction required)

Use AskUserQuestion to clarify requirements:
- **Full mode**: Up to 4 rounds, 3-8 questions each
- **Quick/Hotfix**: 1 round, 3-5 key questions

Cover: functional boundaries, user scenarios, technical constraints, acceptance criteria (SMART), priorities.

**Output**: `01-clarification.md`, `context-summaries/after-clarification.md`

Context summary uses three levels:
- **Must Know**: Key decisions and hard constraints
- **Should Know**: Important background info
- **Reference**: Links to detailed docs

### Step 2: Architecture Design (Full mode only)

Launch architect agent via Task tool (subagent_type: "general-purpose"):
- Read clarification docs + scan project structure (AGENTS.md, README, directory tree)
- If no project architecture docs exist, auto-generate `.ai/myGod/auto-agents.md`

**Output**: `02-architecture.md`, `context-summaries/after-architecture.md`

For document templates, see [design-spec](references/design-spec.md) sections 四 and 七.

### Step 3: Task Decomposition (Skip in hotfix)

Launch decomposer agent:
- Split by module/feature/layer with clear input/output per task
- Map dependencies, identify parallelizable tasks

**Output**: `03-task-decomposition.md`

### Step 4: Development

**Full mode** — Use Agent Team for parallel development:
1. TeamCreate: `myGod-{workflow_id}`
2. TaskCreate for each dev task from decomposition
3. Launch developer agents (subagent_type: "general-purpose", one per parallel track)
   - Each receives: assigned task, relevant context summary, project code style
4. Monitor via TaskList and team messages

**Quick/Hotfix** — Single agent, sequential execution.

**Output per task**: `04-development/task-{nn}-{name}.md`

### Step 5: Unit Validation (Skip in hotfix)

After each dev task completes:
- Run related unit tests (Bash tool)
- Run lint checks
- Verify task acceptance criteria
- On failure: feed back to developer for fix

Append results to corresponding task doc.

### Step 6: Integration (Full mode only)

After all dev tasks complete:
- Check for conflicts in dependency order
- Run integration tests
- Auto-resolve simple conflicts, flag complex ones

**Output**: `05-integration.md`

### Step 7: Code Review (Skip in hotfix)

Launch reviewer agent:
- Check code style, security (OWASP Top 10), performance, test coverage
- Issues graded: blocking / warning / suggestion
- Blocking issues loop back to developer (max 3 retries)

**Output**: `06-code-review.md`

### Step 8: Final Validation

Launch validator agent:
- **Full**: Full test suite + verify each acceptance criterion + generate supplementary tests
- **Quick**: Related tests + verify acceptance criteria
- **Hotfix**: Smoke test only

Max 3 retries on failure. Beyond that, request human intervention.

**Output**: `07-validation.md`, `08-final-checklist.md`

### Step 9: Confirmation and Git (Human interaction required)

1. Present `08-final-checklist.md` to user via AskUserQuestion
2. On confirmation:
   - Commit: `[myGod] {requirement summary}`
   - Create PR via `gh pr create` with auto-generated body (requirement summary, change list, test results)
3. Generate `workflow-summary.md`

## Degradation Strategy

When a phase times out or fails:

```
Full capability -> Simplified -> Minimum -> Human takeover
```

- Test generation fails -> Run existing tests only -> Lint only -> Request human verification
- Code review timeout -> Basic lint check -> Skip review (flagged) -> Human review
- Integration conflict -> Sequential merge -> Human resolution

## Context Compression

Each phase produces a context summary for downstream agents. See [design-spec](references/design-spec.md) section 六 for the full compression mechanism and routing rules.

| Current Role | Receives Summary From |
|-------------|----------------------|
| Architect | Clarifier |
| Decomposer | Clarifier + Architect |
| Developer | Decomposer (relevant task only) |
| Integrator | Decomposer (dependencies) |
| Reviewer | Architect (constraints) |
| Validator | Clarifier (acceptance criteria) |

## Project Adaptation

- **With AGENTS.md**: Read and reuse existing role definitions
- **Without AGENTS.md**: Auto-analyze project structure (scan dirs, identify tech stack), generate `.ai/myGod/auto-agents.md`. See [design-spec](references/design-spec.md) section 十一.
