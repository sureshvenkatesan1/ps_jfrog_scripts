
# Add or Remove Repositories in Artifactory Permission Target

This script updates an existing Artifactory permission target by either adding or removing repositories from it. The script fetches the current configuration of the specified permission target, modifies the repository list as specified, and updates the permission target.

## Prerequisites

- JFrog CLI must be installed and configured.
- `jq` must be installed to parse and manipulate JSON.

## Usage

```bash
./add_or_remove_repos_in_permission_target.sh <serverid> <permission-target-name> <add|remove> <repo1> [<repo2> ...]
```

- `<serverid>`: The ID of the JFrog server configuration.
- `<permission-target-name>`: The name of the permission target to update.
- `<add|remove>`: Operation to perform - either `add` to add repositories or `remove` to remove repositories.
- `<repo1>`, `<repo2>`, ...: The repositories to add to or remove from the permission target.

## Examples

### Add Repositories

```bash
./add_or_remove_repos_in_permission_target.sh my-server my-permission-target add repo1 repo2 repo3
```

This command updates the `my-permission-target` permission target on the `my-server` JFrog server, adding `repo1`, `repo2`, and `repo3` to its list of repositories.

### Remove Repositories

```bash
./add_or_remove_repos_in_permission_target.sh my-server my-permission-target remove repo1 repo2
```

This command updates the `my-permission-target` permission target on the `my-server` JFrog server, removing `repo1` and `repo2` from its list of repositories.

## Notes

- The script uses the JFrog CLI to interact with Artifactory.
- It uses `jq` to handle JSON parsing and manipulation.
- Debugging is enabled to show each command executed by the script, which can help with troubleshooting.

## Troubleshooting

If you encounter any issues:
- Ensure JFrog CLI and `jq` are installed and configured correctly.
- Verify the server ID and permission target name are correct.
- Check the script output for debugging information.

