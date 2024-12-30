
# Fix Property Key Script

This Python script [fix_property_key.py](fix_property_key.py) addresses a known issue (`RTDEV-30673`) in Older Artifactory 6.x version  where property names with underscores (`_`) are incorrectly replicated with double underscores (`__`) during push replication in JFrog Artifactory. The script detects and fixes affected property keys, replacing them with their intended names as defined in the `REPLACEMENTS` dictionary.

## Features

- Detect artifacts with incorrect property keys using an input file (JSON format).
- Optionally update the property keys on Artifactory via API (dry-run mode available).
- Extensible to handle additional property replacements by updating the `REPLACEMENTS` dictionary.

---

## Prerequisites

- Python 3.12 or higher.
- Required Python package: `requests`.

---

## Setup

### Create and Activate a Virtual Environment

#### Linux/Mac:
```bash
python -m venv jfrog
source jfrog/bin/activate
pip install requests
```

#### Windows:
```cmd
python -m venv jfrog
jfrog\Scripts\activate
pip install requests
```

---

## Usage

### Command Syntax
```bash
python fix_property_key.py --jpd-url <ARTIFACTORY_BASE_URL> --access-token <ACCESS_TOKEN> --input <INPUT_FILE> [--commit]
```

### Parameters
- `--jpd-url`: The base URL of your JFrog Artifactory instance.
- `--access-token`: Access token for API authentication.
- `--input`: Path to a JSON file containing a list of affected artifacts.
- `--commit`: Optional flag to commit changes. Without this flag, the script runs in dry-run mode.

### Example
```bash
python fix_property_key.py --jpd-url https://example.jfrog.io --access-token abc123 --input artifacts.json --commit
```

---

## Input File Format

The input file should be in JSON format, containing results from an AQL query. Example query:

```bash
curl -u <user>:<password> -X POST "https://example.jfrog.io/artifactory/api/search/aql" \
    -H "Content-Type: text/plain" \
    -d 'items.find({
        "repo": {"$eq": "your-repo-name"},
        "$or": [
            {"property.key": {"$eq": "git__branch"}},
            {"property.key": {"$eq": "git__commit"}}
        ]
    })'
```

---

## Extending the Script

To add more property replacements, update the `REPLACEMENTS` dictionary in the script:

```python
REPLACEMENTS = {
    "git__commit": "git_commit",
    "git__branch": "git_branch",
    "new_key_with_double_underscore": "new_key_with_single_underscore"
}
```

---

## Logging

The script logs its operations to the console, providing details about:
- Artifacts being processed.
- Property keys being updated (dry-run or actual updates).

---

