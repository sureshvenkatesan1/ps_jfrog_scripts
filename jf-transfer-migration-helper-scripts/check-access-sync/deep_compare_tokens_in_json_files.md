## deep_compare_tokens_in_json_files.py

This script compares tokens between two JSON files and reports the differences.

### Usage

```bash
python deep_compare_tokens_in_json_files.py <file1> <file2>
```

### Description

This script takes two arguments:
- `file1`: Path to the first JSON file.
- `file2`: Path to the second JSON file.

The script compares the tokens between the two JSON files. It reads the contents of both files, compares  tokens 
with same ID  individually, and returns a report detailing the differences between tokens with the same ID. If the 
'projectKey' attribute for the token is missing in one file and exists but is null in the other file, it is ignored in 
the comparison.

### Functionality

1. Load JSON data from both files.
2. Group tokens by ID.
3. Compare tokens with the same ID, ignoring differences in the 'projectKey' attribute as specified.
4. Report and print differences between tokens with the same ID, if any.

### Example

Suppose `file1` contains tokens with ID A, B, and C, while `file2` contains tokens B, C, and D. If there are 
differences in the attributes of tokens B and C between the two files, the script will report and print these differences.

### Requirements

- Python 3.x
- argparse (standard library)
- json (standard library)