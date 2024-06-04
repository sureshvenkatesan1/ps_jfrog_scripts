
# delete_artifacts_in_repo_in_batches.sh

This [delete_artifacts_in_repo_in_batches.sh](delete_artifacts_in_repo_in_batches.sh) script deletes artifacts from 
a specified repository in batches , in a multi-threaded fashion  to avoid 
the "504 Gateway Time-out" error when working with large repositories , 


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
4. Run it:
```bash
bash ./delete_artifacts_in_repo_in_batches.sh <repository-name> <limit-value> <server-id> [threads]
```

- `<repository-name>`: The name of the repository from which to delete artifacts.
- `<limit-value>`: The number of artifacts to delete in each batch.
- `<server-id>`: The server ID to use for the deletion.
- `[threads]` (optional): The number of threads to use for the deletion. Defaults to 8 if not specified.

## Examples

### Example 1: Using default threads (8)

```bash
bash ./delete_artifacts_in_repo_in_batches.sh example-repo-local 1000 mill
```

This command deletes artifacts from the `example-repo-local` repository in batches of 1000, using the server ID `mill` and the default 8 threads.

### Example 2: Specifying number of threads

```bash
bash ./delete_artifacts_in_repo_in_batches.sh example-repo-local 1000 mill 10
```

This command deletes artifacts from the `example-repo-local` repository in batches of 1000, using the server ID `mill` and 10 threads.

## Description

The script performs the following steps in a loop:

1. Executes the `jf rt del` command to delete artifacts from the specified repository in batches.
2. Checks if the command encountered an error. If an error occurs, it logs the error and continues to the next batch.
3. Continues the deletion process until no more artifacts are successfully deleted, indicating that the deletion is 
   complete.


## Notes

- This script is useful for avoiding time-out errors during large-scale deletions.
- Adjust the `<limit-value>` parameter based on your requirements to balance between performance and avoiding time-outs.
- Ensure that you have appropriate permissions and configurations set up in JFrog Artifactory to perform deletions.
- If the command errors out, the script will continue to the next batch instead of exiting.
- The default number of threads is set to 8, but this can be customized by providing a different value as the fourth parameter.






