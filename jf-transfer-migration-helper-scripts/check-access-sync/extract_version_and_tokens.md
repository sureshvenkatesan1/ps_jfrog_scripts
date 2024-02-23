## extract_version_and_tokens.py

This script extracts the "version" and "tokens" fields from a JSON file and saves them to a new JSON file.

### Usage

```bash
python extract_version_and_tokens.py <json_file>
```

### Description

This script takes one argument:
- `json_file`: Path to the JSON file containing the data.

The script loads JSON data from the specified file and creates a new dictionary containing only the "version" and "tokens" fields. It then saves this extracted data to a new JSON file with the suffix "_modified" added to the original filename.

### Functionality

1. Load JSON data from the specified file.
2. Create a new dictionary containing only the "version" and "tokens" fields.
3. Save the extracted data to a new JSON file with the suffix "_modified" added to the original filename.
4. Print a message indicating that the extracted data has been saved.

### Example

Suppose the JSON file contains additional fields besides "version" and "tokens". Running the script on this JSON file will create a new JSON file containing only the "version" and "tokens" fields, with the original data preserved.

### Requirements

- Python 3.x
- argparse (standard library)
- json (standard library)
- os (standard library)