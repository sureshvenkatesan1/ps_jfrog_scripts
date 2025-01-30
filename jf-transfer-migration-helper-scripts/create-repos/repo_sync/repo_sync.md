# Repository Synchronization Tool

This [repo_sync.py](repo_sync.py) script helps synchronize repositories between two Artifactory instances. It can compare repositories, create missing repositories, and manage federation configurations.

## Features

- Compare repositories between two Artifactory instances
- Generate detailed reports of repository differences
- Create missing repositories on target instance
- Handle different repository types:
  - Local repositories
  - Remote repositories
  - Virtual repositories
  - Federated repositories
- Synchronize Xray configurations:
  - Policies
  - Watches
  - Ignore rules
- Generate reports in separate log files for each repository type

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Access to both source and target Artifactory instances
- Valid authentication credentials with admin permissions

## Usage

### Basic Usage

```bash
python repo_sync.py --source-url SOURCE_URL --source-token SOURCE_TOKEN \
                    --target-url TARGET_URL --target-token TARGET_TOKEN \
                    COMMAND
```

### Required Arguments

- `--source-url`: URL of the source Artifactory instance
- `--source-token`: Access token for the source Artifactory
- `--target-url`: URL of the target Artifactory instance
- `--target-token`: Access token for the target Artifactory
- `COMMAND`: Command to execute (see Available Commands below)

### Available Commands

1. Generate Reports:
```bash
# Generate repository comparison report
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    report

# Check source remotes with password
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    remotes_with_password_source

# Check target remotes with password
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    remotes_with_password_target
```

2. Repository Management:
```bash
# Create missing local repositories on target with 8 parallel workers
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_locals_on_target --max-workers 8

# Create missing remote repositories on target with 6 parallel workers
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_remotes_on_target --max-workers 6

# Create missing federated repositories on target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_federated_on_target

# Create missing virtual repositories on target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_virtual_on_target
```

3. Repository Deletion:
```bash
# Delete repositories listed in a file with parallel processing (dry run)
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_from_file --repo-list-file repos_to_delete.txt --max-workers 8 --dry-run

# Delete repositories listed in a file with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_from_file --repo-list-file repos_to_delete.txt --max-workers 8

# Delete all repositories of a specific type with parallel processing (dry run)
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_by_type --repo-type local --max-workers 8 --dry-run

# Delete all repositories of a specific type with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_by_type --repo-type remote --max-workers 8
```

4. Virtual Repository Updates:
```bash
# Update virtual repository members
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_virtual_members

# Dry run of virtual repository member updates
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_virtual_members_dry
```

5. Xray Configuration Sync:
```bash
# Generate Xray configuration report
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    xray_report

# Sync Xray policies
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_xray_policies

# Sync Xray watches
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_xray_watches

# Sync Xray ignore rules
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_xray_ignore_rules
```

## Output Files

The script generates several log files:
- `missing_local_source.log`: Local repositories missing in source
- `missing_local_target.log`: Local repositories missing in target
- `missing_federated_source.log`: Federated repositories missing in source
- `missing_federated_target.log`: Federated repositories missing in target
- `missing_remote_source.log`: Remote repositories missing in source
- `missing_remote_target.log`: Remote repositories missing in target
- `missing_virtual_source.log`: Virtual repositories missing in source
- `missing_virtual_target.log`: Virtual repositories missing in target
- `create_local_errors.log`: Errors when creating local repositories
- `create_local_success.log`: Successful local repository creations
- `delete_repos_errors.log`: Failed repository deletions with error messages
- `delete_repos_success.log`: Successfully deleted repositories

## Additional Arguments

In addition to the required arguments, the following optional arguments are available:

- `--repo-list-file`: Path to a file containing repository keys to delete (one per line)
- `--repo-type`: Type of repositories to delete. Valid values:
  - `local`: Local repositories
  - `remote`: Remote repositories
  - `federated`: Federated repositories
  - `virtual`: Virtual repositories
  - `all`: All repository types
- `--dry-run`: Preview operations without actually executing them
- `--max-workers`: Maximum number of parallel workers for operations (default: 4)
  - Used for both repository creation and deletion
  - Adjust based on system capabilities and API rate limits
  - Example values: 4 (default), 8 (medium), 16 (high)

## System Repositories

The script excludes the following system repositories from synchronization:
- TOTAL
- auto-trashcan
- jfrog-support-bundle
- jfrog-usage-logs

## Error Handling

- The script validates required parameters before execution
- Provides detailed error messages for API failures
- Logs all operations for troubleshooting
- Includes dry-run options for safe testing

## Notes

1. Federation Configuration:
   - Ensures proper member configuration for federated repositories
   - Triggers configuration sync after federation setup
   - Triggers full sync for content synchronization

2. Repository Types:
   - Handles all repository types (local, remote, virtual, federated)
   - Maintains repository configurations and properties
   - Preserves repository relationships in virtual repositories

3. Security:
   - Requires admin-level access token
   - Handles sensitive information like remote repository credentials
   - Supports secure communication over HTTPS
