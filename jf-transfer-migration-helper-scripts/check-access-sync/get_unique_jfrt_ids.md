## get_unique_jfrt_ids.py

This script extracts unique IDs from JSON data based on specified patterns and prints them to the console.

### Usage

```bash
python get_unique_jfrt_ids.py <json_file>
```

### Description

This script takes one argument:
- `json_file`: Path to the JSON file containing the data.

The script extracts unique IDs for two patterns, `'jf-artifactory@'` and `'jfrt@'`, from the JSON data and prints them to the console.

### Functionality

The script reads JSON data from the specified file and extracts unique IDs based on the patterns `'jf-artifactory@'` and `'jfrt@'`. It uses regular expressions to search for these patterns in specific fields of the JSON data. The unique IDs are then printed to the console.

### Example

Suppose the JSON data contains tokens with various subject strings, some of which contain IDs following the patterns `'jf-artifactory@'` and `'jfrt@'`. Running the script on this JSON file will extract and print the unique IDs for each pattern.

### Requirements

- Python 3.x
- argparse (standard library)
- json (standard library)
- re (standard library)