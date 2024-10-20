# Transfer and Merge Remote Repositories Configuration Script

This [transfer_config_merge_remote_repos_from_edge_to_edge.sh](transfer_config_merge_remote_repos_from_edge_to_edge.sh)] is designed to fetch remote repository configurations from a source JFrog Artifactory/Edge, modify the configuration (such as updating credentials and remote URL), and push the updated configuration to a target JFrog Artifactory/Edge during migration.

## Features

- Fetches all remote repositories from the source Artifactory instance.
- Allows inclusion or exclusion of specific repositories using semicolon-separated lists.
- Modifies repository configuration JSON, including updating the `username`, `password`, and `remote URL`.
- Pushes the modified configuration to the target Artifactory instance.
- Logs conflicting repositories if any errors occur during the configuration push.

## Requirements

- [JFrog CLI](https://jfrog.com/getcli/)
- [jq](https://stedolan.github.io/jq/) for JSON manipulation
- Bash shell

## Usage

```bash
./transfer_config_merge_remote_repos_from_edge_to_edge.sh <source_server> <target_server> <includerepos> <excluderepos> <username> <remoteurl_cname>
```

## Parameters

- `source_server`: The JFrog server ID of the source Artifactory instance.
- `target_server`: The JFrog server ID of the target Artifactory instance.
- `includerepos`: A semicolon-separated list of repositories to include in the migration (optional).
- `excluderepos`: A semicolon-separated list of repositories to exclude from the migration (optional).
- `username`: The username to set in the remote repository configuration.
- `remoteurl_cname`: The new remote URL CNAME to replace the existing remote URL in the configuration.
- `REPO_PASSWORD`: The password to set for the remote repository configuration (retrieved from the environment variable).

## Example
```
export REPO_PASSWORD="your_password"
./transfer_config_merge_remote_repos_from_edge_to_edge.sh \
  "source-artifactory" \
  "target-artifactory" \
  "repo1;repo2" \
  "repo3;repo4" \
  "user1" \
  example.jfrog.io
```

## Log Output

- Logs repositories that encounter conflicts during the configuration push to `conflicting-repos.txt`.

## Notes

- The script supports both inclusion and exclusion lists. If both are provided, the inclusion list takes precedence.
- Ensure that `REPO_PASSWORD` is set as an environment variable before running the script.



