---
description: Orchestrate parallel implementation work with smart test sequencing
allowed-tools: Task, Read, Glob, Grep, Bash, TodoWrite, AskUserQuestion
arguments:
  - name: task_reference
    description: Reference to the task/feature to implement (branch name, spec path, or description)
    required: true
  - name: options
    description: "Options: --no-e2e (skip e2e tests), --dry-run (analyze only), --max-agents N (default 4)"
    required: false
---

# Parallel Implementation Orchestrator

Maximize parallelism for multi-phase implementations while being smart about test ordering.

## Task Reference

`$ARGUMENTS`

## Core Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: ANALYSIS                                          │
│  • Identify what work remains                               │
│  • Break into parallelizable chunks                         │
│  • Identify dependencies between chunks                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: PARALLEL IMPLEMENTATION                           │
│  • Launch subagents for independent chunks                  │
│  • Each agent: implement + unit tests                       │
│  • EXCLUDE e2e tests (they conflict)                        │
│  • Wait for all parallel work to complete                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: SEQUENTIAL E2E                                    │
│  • Run e2e tests for each phase IN SEQUENCE                 │
│  • Fix issues as they arise                                 │
│  • Continue until all e2e tests pass                        │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Analysis

First, analyze the task to understand remaining work:

1. **Identify the spec/task source:**
   - If it's a speckit feature: look for `specs/NNN-feature-name/` directory
   - If it's a branch name: check git log and related files
   - If it's a description: search codebase for related code

2. **Determine remaining work by checking:**
   - Spec phases that haven't been implemented
   - TODO comments in existing implementation
   - Failing tests that indicate incomplete work
   - Git diff against main branch

3. **Break work into parallelizable chunks:**
   - Group by independent modules/components
   - Ensure no shared state between chunks
   - Each chunk should be self-contained

4. **Present analysis to user:**
   ```
   ## Work Analysis

   ### Remaining Chunks (can parallelize)
   1. [Chunk A] - Description, files involved
   2. [Chunk B] - Description, files involved
   3. [Chunk C] - Description, files involved

   ### Dependencies
   - Chunk B depends on Chunk A's types (but can still parallelize with interfaces)

   ### E2E Tests to Run After
   - test_feature_a.py
   - test_feature_b.py

   Proceed with parallel implementation? (Y/n)
   ```

## Phase 2: Parallel Implementation

For each independent chunk, launch a subagent:

```markdown
### Subagent Prompt Template

You are implementing [CHUNK_NAME] for [TASK_REFERENCE].

**Scope:**
[Description of what this chunk covers]

**Files to create/modify:**
[List of files]

**Requirements:**
1. Implement the functionality described
2. Write unit tests for your changes
3. Ensure unit tests pass before completing
4. DO NOT run e2e tests - they will be run separately

**Constraints:**
- Stay within your scope - don't modify files outside your chunk
- Use interfaces/types from shared modules
- Follow existing code patterns

**Completion Criteria:**
- All unit tests pass
- No type errors
- Code follows project conventions
```

**Parallel Launch:**
```python
# Launch N agents in parallel (default: 4, or all chunks if fewer)
max_agents = min(len(chunks), max_agents_option or 4)

# Use Task tool with run_in_background=true for each chunk
for chunk in chunks[:max_agents]:
    Task(
        subagent_type="general-purpose",
        prompt=generate_chunk_prompt(chunk),
        run_in_background=True
    )

# Monitor and collect results
```

**Important Rules:**
- Never include e2e test execution in parallel work
- Each agent runs unit tests for ITS changes only
- If an agent fails, collect the error for later fixing

## Phase 3: Sequential E2E Testing

After all parallel work completes:

1. **Verify parallel work succeeded:**
   - Check all background tasks completed
   - Collect any failures

2. **Run full unit test suite:**
   ```bash
   # Ensure nothing broke during parallel work
   pytest tests/unit/ -v  # or equivalent
   ```

3. **Run e2e tests IN SEQUENCE:**
   ```
   For each e2e test file/suite:
     1. Run the test
     2. If it fails:
        - Analyze the failure
        - Fix the issue
        - Re-run until it passes
     3. Move to next e2e test
   ```

4. **Final verification:**
   - All e2e tests pass
   - No regressions in unit tests

## Options Handling

Parse `$ARGUMENTS` for options:

| Option | Effect |
|--------|--------|
| `--no-e2e` | Skip Phase 3 entirely |
| `--dry-run` | Only do Phase 1 analysis, don't implement |
| `--max-agents N` | Limit concurrent agents (default: 4) |

## Error Handling

| Scenario | Action |
|----------|--------|
| Analysis finds no remaining work | Report completion, exit |
| Chunk implementation fails | Collect error, continue others, fix after |
| Unit tests fail in chunk | Agent should fix before completing |
| E2e test fails | Fix sequentially, re-run affected tests |
| Circular dependencies detected | Alert user, suggest manual intervention |

## Example Session

```
User: /parallel-implement continue 015-react-native-mobile

Claude: Analyzing task 015-react-native-mobile...

## Work Analysis

Found spec at: specs/015-react-native-mobile/

### Remaining Phases
1. **Phase 3: Gesture handlers** - gesture.ts, gesture.test.ts
2. **Phase 4: Screen transitions** - transitions.ts, transitions.test.ts
3. **Phase 5: Deep linking** - deeplink.ts, deeplink.test.ts

### E2E Tests
- e2e/mobile_navigation.spec.ts
- e2e/mobile_gestures.spec.ts

All 3 phases are independent. Launching 3 parallel agents...

[Agent 1] Working on Phase 3: Gesture handlers
[Agent 2] Working on Phase 4: Screen transitions
[Agent 3] Working on Phase 5: Deep linking

... (waiting for completion) ...

All parallel work complete. Running e2e tests sequentially:

[1/2] e2e/mobile_navigation.spec.ts - PASSED
[2/2] e2e/mobile_gestures.spec.ts - FAILED

Fixing gesture test failure...
[Fix applied]
Re-running e2e/mobile_gestures.spec.ts - PASSED

All done! 015-react-native-mobile implementation complete.
```

## Begin

Parse the arguments and start with Phase 1 analysis now.
