---
name: agents-book
description: Generates comprehensive AGENTS.md documentation system for code projects to enable AI-assisted development. Use when users ask to "generate AGENTS.md", "create AGENTS.md", "create AI documentation for my project", "document my codebase for AI agents", "生成 AGENTS.md", "为项目生成 AI 文档", "generate agents book", or provide a code repository that needs structured documentation for AI collaboration. Creates root-level overview, directory maps, business scenario indexes, and recursive subdirectory documentation following strict quality standards.
---

# AGENTS.md Generator

## Core Objective

Generate a **complete, actionable, maintainable `AGENTS.md` documentation system** for code projects to support **Human-assisted AI Development** mode.

**This is NOT about "explaining code"**. The goal is to:
- Transform implicit engineering knowledge (design intent, constraints, dependencies) into explicit structured documentation
- Enable agents to build a mental model, locate modification entry points, and avoid high-risk side effects **without reading all source code**

## Critical Requirements

**IMPORTANT**: Read the complete specification in [references/AGENTS_MD_GENERATION_PROMPT_v2.md](references/AGENTS_MD_GENERATION_PROMPT_v2.md) before starting. This SKILL.md provides a quick reference; the full prompt contains detailed requirements, templates, and quality criteria that MUST be followed.

## Execution Process

**Strictly follow these phases in order. Do not skip steps.**

### Phase 1: Reconnaissance (全景侦察)

**Goal**: Build **structural-level cognition** of the project, not business details.

**Actions**:
1. Use directory scanning tools (e.g., `tree -L 3`, `ls -R`, or Glob tool) to scan the entire repository
2. Create an internal directory inventory (for analysis, not written to documentation) marking:
   - Business modules (feature-specific directories)
   - Infrastructure layers (utils, common, infra)
   - Configuration/scripts/automation directories
3. Note which directories should be skipped (empty, non-code, <3 files with no logic)

**Important**: All first-level source directories AND their subdirectories must be recursively covered.

### Phase 2: Root Directory Documentation (根目录 AGENTS.md 构建)

**File path**: `{ProjectRoot}/AGENTS.md`

**Must include ALL of the following sections**:

#### 1️⃣ System Overview (系统概述)
- What problem does the project solve?
- Core business boundaries
- Main tech stack (language/framework/storage/messaging)

#### 2️⃣ Directory Map (目录导航)

| Directory | Responsibility | Key Notes | AGENTS.md Link |
|-----------|---------------|-----------|----------------|
| `xxx/` | ... | ... | ./xxx/AGENTS.md |

#### 3️⃣ Critical Business Scenarios Index (核心业务场景索引)

List **5-20 real, existing core business scenarios** (prioritize high-frequency calls, critical paths, or business criticality; adjust quantity based on project size).

For each scenario, provide **specific code entry points**:

```markdown
- **Scenario Name** (e.g., User Registration)
  - Entry: `Controller/Handler` (e.g., UserController.register)
  - Core Logic: `Service/Domain` (e.g., UserService.createUser)
  - Side Effects: `Producer/Consumer/Job` (e.g., EmailProducer.sendWelcome)
```

#### 4️⃣ Global Design Constraints (全局设计约束)
- Transaction/consistency constraints
- Cache usage rules
- Async messaging principles
- **Explicit prohibitions** (e.g., "No direct SQL queries", "No cross-module DB access")

### Phase 3: Subdirectory Documentation (子目录级 AGENTS.md 构建 - 迭代执行)

**Critical**: This phase must be executed **recursively** for each directory AND its subdirectories.

For each directory at all levels, execute this loop:

#### Step 1: Scanning
- List all files and subdirectories (ignore .git, node_modules, etc.)
- Identify if directory should be skipped (<3 files with no business logic/external dependencies)

#### Step 2: Analysis
- **Read all code files** in the directory
- Identify:
  - Core classes (e.g., called >3 times)
  - Key workflows and call chains
  - External dependencies (Redis, Kafka, DB, APIs)

#### Step 3: Writing
- Generate `AGENTS.md` in that directory using appropriate template (see below)
- Ensure documentation is self-contained and actionable

**Coverage requirement**: All directories with code or configuration must have AGENTS.md. Missing documentation for any relevant directory is considered a **defect**.

## Documentation Templates

**Use the exact templates specified in the full prompt**. Quick reference below:

### Template A: Business Modules (业务模块)

Use for: business/, domain/, feature/, service/ directories

**Required sections**:
1. Module Overview (must explain **business problem**, not just technical responsibility)
2. Core Code Structure (table with File/Directory, Responsibility, Key Classes/Methods)
3. Core Business Workflows (with arrow notation showing flow and class names)
4. Key Resources & Side Effects (Redis keys with TTL/structure, Kafka topics, DB tables)
5. Common Modification Scenarios (specific entry points for typical changes)
6. Maintenance & Risk Notes (downstream impacts, high-risk points with risk matrix)

See [references/AGENTS_MD_GENERATION_PROMPT_v2.md](references/AGENTS_MD_GENERATION_PROMPT_v2.md) Section 4 for complete template.

### Template B: Infrastructure/Utility Layers (通用/基础设施层)

Use for: utils/, common/, config/, infra/ directories

**Required sections**:
1. Overview (positioning and boundaries in the system)
2. Core Components (with usage constraints and common misuses)
3. Design Conventions (stateful/stateless, thread safety, prohibited dependencies)
4. Usage Examples (typical calling patterns with code snippets or pseudocode)

See [references/AGENTS_MD_GENERATION_PROMPT_v2.md](references/AGENTS_MD_GENERATION_PROMPT_v2.md) Section 4 for complete template.

## Definition of Done (交付标准)

**All of the following must be satisfied, otherwise the task is incomplete**:

### 1. Coverage (覆盖性)
- ✅ AGENTS.md exists in project root directory
- ✅ AGENTS.md exists in all first-level source directories (e.g., src/, app/)
- ✅ AGENTS.md exists in all subdirectories recursively (skip only if <3 files with no logic/dependencies)
- ✅ AGENTS.md exists in key config/scripts/jobs/migration/infra directories
- ❌ Missing AGENTS.md for any relevant directory = **DEFECT**

### 2. Groundedness (真实性)
- ✅ All content based on real code scanning
- ✅ Contains actual class/function/file names that exist in the codebase
- ✅ Shows real call relationships and workflows
- ✅ References specific external resources (actual Redis keys, Kafka topics, DB tables)
- ❌ NO fabricated class names
- ❌ NO generic vague descriptions (e.g., "handles related logic", "provides common capabilities")

### 3. Self-Contained (自包含)
- ✅ Each AGENTS.md is independently readable
- ✅ Does not assume reader already understands other modules
- ✅ Agent should not need to frequently jump to source code to understand responsibilities

### 4. Actionability (可操作性)
- ✅ Answers: "For this requirement, where do I start?"
- ✅ Answers: "If I change this, what else will be affected?"

## Anti-Patterns (明确禁止的反模式)

**If any of the following appears, the corresponding documentation must be rewritten**:

- ❌ Using vague expressions without listing specific classes/methods
- ❌ Only describing "directory responsibility" without "code structure"
- ❌ Assuming reader already knows upstream/downstream systems
- ❌ Avoiding side effects (cache, async, idempotency, compensation, eventual consistency)
- ❌ Documentation looks "correct" but cannot guide actual modifications
- ❌ Exposing sensitive information (API keys, credentials, passwords)

## Self-Correction Checklist (质量校验)

**Before submission, verify each item. If any fails, return to the corresponding phase and redo**:

- [ ] Does any module description lack specific class names? (Need at least 5 concrete references per module)
- [ ] Is there any relevant directory missing AGENTS.md? (Verify recursive coverage)
- [ ] Can the root directory index accurately navigate to all submodules?
- [ ] Are side effects and risk points clearly marked? (Need at least 2 quantified risks per business module)
- [ ] Can the documentation actually guide a real modification? (Simulate a change scenario to verify)
- [ ] Have multi-language/hybrid repository considerations been addressed? (If applicable, annotate)

## Output Requirements (输出要求)

- Use **Markdown** format
- Do not output intermediate analysis process (optional: if debug mode, output logs)
- Do not skip any relevant directories
- Maintain rigor equivalent to **engineer handoff documentation**
- Optional: Add flowcharts (e.g., Mermaid) to visualize core workflows if tools support it

## Implementation Notes

**Before starting work**:
1. **Read the complete specification**: [references/AGENTS_MD_GENERATION_PROMPT_v2.md](references/AGENTS_MD_GENERATION_PROMPT_v2.md)
2. Ask user for the project path if not already provided
3. Confirm with user if there are any specific directories to prioritize or skip

**During execution**:
- Follow phases strictly in order (Phase 1 → Phase 2 → Phase 3)
- For Phase 3, process directories recursively from top to bottom
- Use Read tool extensively to scan actual code - do not make assumptions
- Generate AGENTS.md files progressively using Write tool

**Quality over speed**: It's better to generate fewer but higher-quality AGENTS.md files than to rush through and produce generic documentation.

---

> **Remember**: The quality of `AGENTS.md` determines whether the Agent can become a "qualified collaborator" rather than a "noise-making tool".
