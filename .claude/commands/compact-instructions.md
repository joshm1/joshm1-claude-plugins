---
description: Compact instruction files (CLAUDE.md, AGENT.md) to reduce tokens while preserving operational meaning
allowed-tools: Read, Write, Glob, Bash
arguments:
  - name: file_path
    description: Path to instruction file to compact (defaults to ./CLAUDE.md)
    required: false
---

# Compact Instruction File

You are compacting an instruction file used by coding agents.

**Goal:** Reduce tokens while preserving ALL operational meaning.

## Target File

Compact this file: `$ARGUMENTS` (if empty, default to `./CLAUDE.md`)

## Hard Rules

1. **NEVER drop or weaken constraints** - Preserve all MUST/SHOULD/NEVER/CRITICAL/IMPORTANT rules exactly
2. **Preserve verbatim:**
   - Required commands, file paths, environment setup
   - Style rules, testing steps, security rules
   - Escalation/approval rules
   - All code blocks (unless they contain purely redundant comments)
3. **Keep all examples** - Dedupe near-duplicates only
4. **Merge repetitive bullets** - Remove filler words, motivational prose
5. **Use terse, unambiguous language** - Prefer imperatives
6. **Preserve headings** - Keep if they improve scanability; collapse redundant sections
7. **Clarify ambiguity** - If any instruction becomes unclear after compaction, add a short clarifying line rather than removing it

## Process

1. Read the target instruction file
2. Analyze for:
   - Redundant explanations (keep rules, drop justifications unless critical)
   - Duplicate examples (keep one representative example)
   - Filler words ("please", "you should consider", "it's important to note")
   - Repeated concepts across sections
   - Verbose bullet lists that can be condensed
3. Compact the content following Hard Rules
4. Write the compacted version to `{original_filename}.compact.md`
5. Generate change log

## Output Format

Create two outputs:

### 1. Compacted File
Write to `{original_filename}.compact.md` with:
- All operational meaning preserved
- Reduced token count
- Same structure (or cleaner structure if sections can be merged)

### 2. Change Log
After writing the file, report:
```
## Compaction Summary
- Original: ~X tokens (estimate)
- Compacted: ~Y tokens (estimate)
- Reduction: ~Z%

## Changes Made (max 10 bullets)
- [What you removed/merged]
- [What you consolidated]
- ...
```

## Begin

Read the target file and perform the compaction now.
