## merge_tokens.py

This script merges tokens from two JSON files into a single output JSON file.

### Usage

```bash
python merge_tokens.py access.backup.20240221223922.json UA-DOQ-BELLCA-combined-tokens-022124.json final_tokens.json
```

### Description

This script takes three arguments:
- `file1`: Path to the first JSON file containing tokens.
- `file2`: Path to the second JSON file containing tokens.
- `output_file`: Path to the output merged JSON file.

### Functionality

The script reads tokens from `file1` and `file2`, and then merges them into a single list of tokens. It ensures that duplicate tokens (based on their IDs) are not included in the output. The merged tokens are then written to the `output_file`.

### Example

Suppose `file1` contains tokens A, B, and C, while `file2` contains tokens B, C, and D. The output JSON file will contain tokens A, B, C, and D, with duplicate tokens (B and C) removed.

### Requirements

- Python 3.x
- argparse (standard library)
- json (standard library)