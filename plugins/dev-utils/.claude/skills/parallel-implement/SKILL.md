---
name: parallel-implement
description: Orchestrate parallel implementation work across multiple subagents. Use when implementing multi-phase features that can be split into independent chunks for concurrent execution.
allowed-tools: Task, Read, Glob, Grep, Bash, TodoWrite, AskUserQuestion
---

# Parallel Implementation Orchestrator

Maximize development velocity by identifying and executing parallelizable work across multiple autonomous subagents.

## When to Use This Skill

Use this skill when:
- Implementing a multi-phase feature with independent components
- Multiple user stories or tasks can be developed simultaneously
- You want to minimize total implementation time through concurrent work
- The project has infrastructure for running parallel tests (e.g., atomic E2E locking)

**Trigger phrases:**
- "implement this in parallel"
- "run parallel implementation"
- "split this work across agents"
- "parallelize development"

## Core Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: ANALYSIS                                          │
│  • Identify what work remains                               │
│  • Break into parallelizable chunks                         │
│  • Identify dependencies between chunks                     │
│  • Verify test infrastructure supports parallelization     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: PARALLEL IMPLEMENTATION                           │
│  • Launch subagents for independent chunks                  │
│  • Each agent: implement + unit tests + E2E tests           │
│  • Agents use project's test infrastructure                 │
│  • Wait for all parallel work to complete                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: VERIFICATION                                      │
│  • Verify all agents completed successfully                 │
│  • Run full test suite to check for regressions            │
│  • Fix any integration issues                               │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Analysis

### 1. Identify Work Source

Determine what needs to be implemented:
- **Speckit features**: Look for `specs/NNN-feature-name/` directory with tasks.md
- **Branch work**: Check git log and modified files
- **Issue/description**: Search codebase for related code

### 2. Assess Remaining Work

Check multiple sources:
- Spec phases that haven't been implemented
- TODO/FIXME comments in code
- Failing tests indicating incomplete work
- Git diff against main branch
- Project-specific task tracking (Jira, GitHub issues, etc.)

### 3. Identify Parallelizable Chunks

Group work by:
- **Independent modules/components**: Different files, no shared state
- **Feature boundaries**: Each chunk delivers a complete mini-feature
- **Test isolation**: Each chunk can test independently

**Anti-patterns to avoid:**
- ❌ Chunks that modify the same files
- ❌ Chunks with circular dependencies
- ❌ Chunks requiring sequential database migrations
- ❌ Chunks sharing global state or singletons

### 4. Verify Test Infrastructure

**CRITICAL**: Check if the project supports parallel testing:

```bash
# Look for project-specific test parallelization scripts
find . -name "*parallel*test*" -o -name "*locked*test*"

# Check for testing documentation
find . -name "*test*.md" | xargs grep -l parallel
```

**Common patterns:**
- **Mobile E2E**: May require atomic locking (single device)
- **Web E2E**: Often supports parallel execution (Playwright, Cypress)
- **Unit tests**: Usually parallel-safe by default
- **Integration tests**: Check for database/service conflicts

### 5. Present Analysis to User

```markdown
## Work Analysis for [FEATURE_NAME]

### Remaining Work
Total estimated: X hours/days

### Parallelizable Chunks
1. **[Chunk A]** - Description
   - Files: file1.ts, file2.ts
   - Tests: chunk-a.spec.ts
   - Time: ~2 hours
   - Dependencies: None

2. **[Chunk B]** - Description
   - Files: file3.ts, file4.ts
   - Tests: chunk-b.spec.ts
   - Time: ~3 hours
   - Dependencies: Chunk A types (can parallelize with interfaces)

3. **[Chunk C]** - Description
   - Files: file5.ts, file6.ts
   - Tests: chunk-c.spec.ts
   - Time: ~2 hours
   - Dependencies: None

### Wave Planning
- **Wave 1** (parallel): Chunks A, C (no dependencies)
- **Wave 2** (parallel): Chunk B (after Wave 1 types exist)

### Test Strategy
- Unit tests: Run in each agent immediately
- E2E tests: [DESCRIBE PROJECT'S E2E STRATEGY]
  - If atomic locking: Reference project docs
  - If parallel-safe: Run concurrently

### Expected Speedup
- Sequential: ~7 hours
- Parallel (2 waves): ~5 hours (29% faster)

Proceed with parallel implementation? (Y/n)
```

## Phase 2: Parallel Implementation

### Subagent Prompt Template

For each chunk, generate a focused prompt:

```markdown
You are implementing [CHUNK_NAME] for [TASK_REFERENCE].

**Agent ID**: agent-[UNIQUE_ID]

**Scope:**
[Description of what this chunk covers]

**Files to create/modify:**
- file1.ts
- file2.ts
- tests/file1.spec.ts

**Requirements:**
1. Implement the functionality described
2. Write unit tests for your changes
3. Ensure unit tests pass: [PROJECT_TEST_COMMAND]
4. Write E2E test for your feature (if applicable)
5. Run E2E test using project's test infrastructure
6. Ensure all tests pass before completing

**Test Infrastructure:**
[PROJECT-SPECIFIC TESTING COMMANDS]

**Constraints:**
- Stay within your scope - don't modify files outside your chunk
- Use interfaces/types from shared modules
- Follow existing code patterns in the project
- Coordinate with other agents if dependencies exist

**Completion Criteria:**
- All unit tests pass
- All E2E tests pass (if applicable)
- No type errors
- Code follows project conventions
- No merge conflicts with other chunks
```

### Launch Agents in Parallel

```python
# Pseudocode for agent launching
max_agents = min(len(chunks), user_specified_max or 4)

# Use Task tool with run_in_background=true
for chunk in wave_1_chunks:
    Task(
        subagent_type="general-purpose",
        prompt=generate_chunk_prompt(chunk),
        run_in_background=True,
        description=f"{chunk.name} implementation"
    )

# Monitor completion
# Wait for all Wave 1 agents before starting Wave 2
```

**Important Rules:**
- Each agent runs BOTH unit tests AND E2E tests
- Agents use project-specific test infrastructure
- If an agent fails, collect error for later fixing
- Never block on sequential work that could be parallel

## Phase 3: Verification

### 1. Collect Agent Results

```bash
# Check all background tasks completed
/tasks

# Review any failures
# For each failed agent:
#   - Read error output
#   - Identify root cause
#   - Fix or re-run
```

### 2. Run Full Test Suite

```bash
# Project-agnostic pattern: run all tests
# Specific command depends on project setup

# Examples:
# mise run test:all
# npm test && npm run test:e2e
# pytest && playwright test
```

### 3. Fix Integration Issues

After parallel work, check for:
- **Type conflicts**: Overlapping type definitions
- **Import issues**: Circular dependencies introduced
- **Test conflicts**: Shared test fixtures or state
- **Merge conflicts**: Unexpected file overlaps

### 4. Final Verification

Checklist:
- ✅ All unit tests pass
- ✅ All E2E tests pass
- ✅ All integration tests pass
- ✅ No type errors (TypeScript, Pyright, etc.)
- ✅ No linting issues
- ✅ No merge conflicts
- ✅ Code review ready (if applicable)

## Project-Specific Adaptations

This skill is framework-agnostic. Adapt the following based on the project:

### Test Commands
Replace `[PROJECT_TEST_COMMAND]` with actual commands:
- TypeScript: `pnpm test` or `npm test`
- Python: `pytest` or `uv run pytest`
- Mobile: Check for atomic locking scripts

### E2E Test Strategy
Determine project's approach:
- **Web (Playwright/Cypress)**: Usually parallel-safe
- **Mobile (Appium/Expo)**: Often requires atomic locking
- **API**: Usually parallel-safe with database isolation

### Merge Strategy
Consider project workflow:
- Feature branches per chunk
- Single feature branch with coordinated merges
- Trunk-based with feature flags

## Options Handling

Support flexible invocation:

| Option | Effect |
|--------|--------|
| `--no-e2e` | Skip E2E tests in agents, run only in verification |
| `--dry-run` | Analysis only, don't launch agents |
| `--max-agents N` | Limit concurrent agents (default: 4) |
| `--wave-by-wave` | Wait for each wave before starting next |

## Error Handling

| Scenario | Action |
|----------|--------|
| Analysis finds no remaining work | Report completion, exit gracefully |
| Chunk has unresolved dependencies | Move to later wave or flag for user |
| Agent fails implementation | Collect error, continue others, fix after |
| Agent fails tests | Agent should fix before completing |
| Circular dependencies detected | Alert user, suggest manual intervention |
| Test infrastructure missing | Alert user, suggest sequential approach |

## Best Practices

### Do:
- ✅ Start with thorough analysis before launching agents
- ✅ Verify test infrastructure supports parallelization
- ✅ Use wave-based execution for dependent chunks
- ✅ Monitor agent progress and collect failures
- ✅ Run full test suite after all agents complete
- ✅ Document any project-specific testing requirements

### Don't:
- ❌ Launch agents without dependency analysis
- ❌ Assume tests can run in parallel (verify first)
- ❌ Ignore agent failures and merge anyway
- ❌ Skip integration testing after parallel work
- ❌ Parallelize work with high merge conflict risk

## Example Session

```
User: Implement the user management feature in parallel