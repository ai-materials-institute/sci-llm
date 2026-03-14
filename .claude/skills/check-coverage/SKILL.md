---
name: check-coverage
description: Check extraction coverage against ground truth highlighted properties. Use after running pbench-eval to verify that key properties were extracted.
allowed-tools: Read, Glob, Grep, Bash, Agent
argument-hint: [ground_truth_path] [output_dir]
---

# Check Coverage

Check the coverage of extracted properties against a ground truth highlighted properties file.

## Arguments

- `$0`: Path to the ground truth highlighted properties markdown file (default: `data-val/highlighted_properties.md`)
- `$1`: Path to the output directory containing predictions (default: `out`). The predictions CSVs are in `<output_dir>/preds/`.

## Instructions

1. **Read the ground truth file** at `$0` (default `data-val/highlighted_properties.md`). This file has sections per paper (## refno.pdf) with numbered highlighted evidence snippets from the paper. Each snippet is a passage that contains or relates to an extractable property.

2. **Read all prediction CSVs** from `$1/preds/` (default `out/preds/`). Each CSV has columns including: `material_or_system`, `property_name`, `value_string`, `location.page`, `location.evidence`, etc.

3. **For each paper**, compare the extracted predictions against the highlighted ground truth:

   - Parse each highlighted snippet to identify what extractable property it refers to (q-vector value, commensurability type, space group symbol, material formula, etc.)
   - Note: many highlighted snippets are contextual (crystal structure descriptions, material mentions) — not every snippet maps to a standalone extracted property. Focus on snippets that contain target property values.
   - Check whether the prediction CSV for that paper contains a matching extraction. A "match" means the key property value was captured (e.g., the q-vector tuple, the space group symbol, the commensurability label).
   - Be flexible with formatting differences (e.g., `(0.23, 0, 0.5)` vs `(0.230, 0, 0.500)`, `I4/mmm` exact match, `commensurate` vs `CCDW`).

4. **Report results** in a markdown table with:
   - Per-paper breakdown: paper ID, number of key extractable properties highlighted, number matched, coverage %
   - Overall summary row
   - List any specific misses (highlighted property not found in predictions)

5. **Also report basic statistics**:
   - Total rows extracted
   - Unique (material, property_name, value_string) tuples
   - Property distribution (count per property_name)
