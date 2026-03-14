---
name: optimize-prompt
description: Iterate on an extraction prompt — create a new version, run extraction, check coverage, and analyze duplicates/noise.
argument-hint: <source-prompt> <description-of-changes>
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Skill, Agent
---

# Optimize Extraction Prompt

You are iterating on an LLM extraction prompt for a scientific property extraction benchmark. Follow this workflow step by step.

## Inputs

- `$1` — path to the source prompt (e.g., `prompts/targeted_extraction_prompt_v6_1.md`)
- `$2` — description of changes to make (e.g., "require experimental validation")

If no arguments are provided, ask the user for:
1. Which prompt to start from
2. What changes to make
3. What to name the new version

## Workflow

### Step 1: Create the new prompt version

1. Read the source prompt
2. Copy it to a new file with the next version name (e.g., `v6` → `v6_1` → `v7`)
3. Apply the requested changes
4. Show the user a summary of what changed (diff-style)

### Step 2: Run extraction

Run the extraction command:
```bash
uv run pbench-extract -dd data-val --server gemini -m gemini-3.1-pro-preview -pp <new-prompt-path> -od out-<date>-<version> --max_concurrent 100
```

Use today's date in MMDD format and the version name for the output directory.

### Step 3: Check coverage

Run the `/check-coverage` skill with the ground truth and output directory:

```
/check-coverage data-val/highlighted_properties.md out-<date>-<version>
```

This compares extracted properties against the highlighted ground truth and reports per-paper coverage.

### Step 4: Analyze noise

Count and categorize extra rows beyond the highlighted properties:

1. **Deduplication failures**: Same (material, property_name, value_string) tuple appearing multiple times. Show the worst offenders with counts.
2. **Legitimate extra properties**: Properties not in the highlighted set but arguably correct (additional compositions, conditions, etc.)
3. **Parsing artifacts**: Malformed rows where evidence text leaked into other columns.

### Step 5: Summary table

Present a comparison table with all prompt versions run in this session:

| Prompt | Total rows | Coverage (X/23) | Dedup failures | Notes |
|--------|-----------|-----------------|----------------|-------|

### Step 6: Recommendation

Based on the results, suggest whether to:
- Keep the new version (if coverage maintained and noise reduced)
- Iterate further (if specific issues were identified)
- Revert (if coverage dropped)
