

# Transfer the delta files after a full Sync

## Overview
This Python script facilitates the migration of the delta artifacts from one repository to another between the SOURCE and TARGET Artifactory instance.
It also handles the transfer of associated metadata properties.
The delta is generated from the `cleanpaths.txt` generated from the  [repodiff.py](../repoDiff/repodiff.py)

## Usage
### Prerequisites
- Ensure that the `jf` command-line tool for Artifactory is installed and configured properly.
- Python 3.x is required to execute the script.


### Execution
Run the script with the following command:

```
python transfer_cleanpaths_delta_from_repoDiff.py <input_file> <source_artifactory> <source_repo> <target_artifactory> <target_repo>
```

Replace `<input_file>`, `<source_artifactory>`, `<source_repo>`, `<target_artifactory>`, and `<target_repo>` with appropriate values.

### Example
```
python transfer_cleanpaths_delta_from_repoDiff.py /tmp/test/output/cleanpaths.txt soleng app1-docker-dev-local proservicesone test-docker
```

## Parameters
- **input_file**: Path to the input file containing file paths i.e the `cleanpaths.txt` generated from the  [repodiff.py](../repoDiff/repodiff.py).
- **source_artifactory**: Source Artifactory ID.
- **source_repo**: Source repository name.
- **target_artifactory**: Target Artifactory ID.
- **target_repo**: Target repository name.

## Notes
- This script assumes the availability of the `jf` command-line tool for interacting with Artifactory. Ensure that the `jf` tool is installed and configured properly before executing this script.

