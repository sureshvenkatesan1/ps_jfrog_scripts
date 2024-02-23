## compare_token_ids_in_json_files.py

This script compares token IDs between two JSON files and determines whether they are the same.

### Usage

```bash
python compare_token_ids_in_json_files.py <file1> <file2>
```

### Description

This script takes two arguments:
- `file1`: Path to the first JSON file.
- `file2`: Path to the second JSON file.

The script compares the token IDs between the two JSON files. It extracts the token IDs from both files and checks if they are identical. It then prints a message indicating whether the token IDs in the two files are the same or different.

### Functionality

1. Load JSON data from both files.
2. Extract token IDs from each JSON file.
3. Compare the sets of token IDs extracted from both files.
4. Print a message indicating whether the token IDs in the two files are the same or different.

### Example

Suppose `file1` contains tokens with ids A, B, and C, while `file2` contains tokens with ids  C, B, and A. The script 
will compare the token IDs between the two files. Since the token IDs are the same  , it will print "Both JSON 
files have the same token IDs." 

Suppose `file1` contains tokens with ids A, B, and C, while `file2` contains tokens with ids  C, D, and E. The script
will compare the token IDs between the two files. Since the token IDs are different , it will print "JSON files have different token IDs."

### Requirements

- Python 3.x
- argparse (standard library)
- json (standard library)