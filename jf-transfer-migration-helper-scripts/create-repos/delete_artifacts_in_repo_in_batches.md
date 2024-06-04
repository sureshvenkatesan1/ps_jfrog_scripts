
# delete_artifacts_in_repo_in_batches.sh

This [delete_artifacts_in_repo_in_batches.sh](delete_artifacts_in_repo_in_batches.sh) script deletes artifacts from a specified repository in batches to avoid 
the "504 Gateway Time-out" error when working with large repositories.

## Features

- Deletes artifacts from a repository in batches.
- Handles time-out issues by performing deletions in a loop.
- Uses the JFrog CLI (`jf`) to interact with the repository.
- Provides multi-threaded deletion to improve efficiency.

## Requirements

- JFrog CLI (`jf`) installed and configured.
- `jq` installed for JSON parsing (optional if using `grep` and `awk`).

## Usage

1. Make sure you have the necessary tools installed:
    - [JFrog CLI](https://jfrog.com/getcli/)
    - `jq` (optional)

2. Clone this repository or download the script.

3. Make the script executable:

    ```bash
    chmod +x delete_artifacts_in_repo_in_batches.sh
    ```

4. Run the script with the required parameters:

    ```bash
    ./delete_artifacts_in_repo_in_batches.sh <repository-name> <limit-value> <server-id>
    ```

    Replace `<repository-name>`, `<limit-value>`, and `<server-id>` with your desired repository name, limit value, and server ID.

    Example:

    ```bash
    ./delete_artifacts_in_repo_in_batches.sh example-repo-local 1000 mill
    ```

## Notes

- This script is useful for avoiding time-out errors during large-scale deletions.
- Adjust the `<limit-value>` parameter based on your requirements to balance between performance and avoiding time-outs.
- Ensure that you have appropriate permissions and configurations set up in JFrog Artifactory to perform deletions.

