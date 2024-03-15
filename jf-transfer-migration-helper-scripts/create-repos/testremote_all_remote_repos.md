## testremote_all_remote_repos.sh

This script is designed to test remote repositories in JFrog Artifactory. It iterates through a list of remote repositories, tests each repository, and provides feedback on the test results.

### Usage

```bash
bash testremote_all_remote_repos.sh source-serverId [includerepos] [excluderepos]
```

**Arguments:**
- `source-serverId`: The ID of the source server.
- `includerepos` (optional): A semicolon-separated list of repositories to include in the test.
- `excluderepos` (optional): A semicolon-separated list of repositories to exclude from the test.

### Example

```bash
bash testremote_all_remote_repos.sh psemea
```

### Exit Behavior

The script exits upon encountering any failures.

### Script Details

The script retrieves a list of remote repositories from the specified source server and iterates through them. For each repository:

1. It checks if the repository should be excluded based on the provided exclusion list.
2. If the repository is not excluded, it retrieves the configuration and tests the remote repository.
3. The script reports whether the connection to the remote repository was successful or failed, along with any relevant error messages.


### License

This script is provided 'as-is' and without any warranties or conditions. JFrog grants a non-exclusive, non-transferable, non-distributable right to use this code solely in connection with your use of a JFrog product or service.