# Repository Synchronization Tool

This [repo_sync.py](repo_sync.py) script helps synchronize repositories and configurations between two Artifactory instances. It can compare repositories, create missing repositories, manage federation configurations, and sync various platform configurations.

## Features

- Compare repositories between two Artifactory instances
- Generate detailed reports of repository differences
- Create missing repositories on target instance
- Update existing repository configurations
- Handle different repository types:
  - Local repositories
  - Remote repositories
  - Virtual repositories
  - Federated repositories
- Synchronize Xray configurations:
  - Policies
  - Watches
  - Ignore rules
- Synchronize platform configurations:
  - Projects
  - Environments (Global and Project-specific)
  - Property Sets
- Generate reports in separate log files for each operation type

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

# List remote repositories with passwords missing in target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    remotes_with_password_source

# List all remote repositories with passwords in target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    remotes_with_password_target

# Generate Xray configuration report
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    xray_report

# List projects missing in target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    list_missing_projects_source

# List projects missing in source
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    list_missing_projects_target
```

2. Repository Management:
```bash
# Create missing local repositories on target with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_locals_on_target --max-workers 8

# Create missing remote repositories on target with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_remotes_on_target --max-workers 8

# Create missing federated repositories on target with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_federated_on_target --max-workers 8

# Create missing virtual repositories on target with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    create_missing_virtuals_on_target --max-workers 8

# Refresh storage summary
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    refresh_storage_summary
```

3. Repository Updates:
```bash
# Update local repository configurations (dry run) with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_locals_on_target_dry --max-workers 8

# Update local repository configurations with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_locals_on_target --max-workers 8

# Update remote repository configurations (dry run) with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_remotes_on_target_dry --max-workers 8

# Update remote repository configurations with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_remotes_on_target --max-workers 8

# Update federated repository configurations (dry run) with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_federated_repos_on_target_dry --max-workers 8

# Update federated repository configurations with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_federated_repos_on_target --max-workers 8

# Update virtual repository configurations (dry run) with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_virtuals_on_target_dry --max-workers 8

# Update virtual repository configurations with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    update_virtuals_on_target --max-workers 8
```

4. Configuration Synchronization:
```bash
# Sync projects from source to target
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_projects

# Sync environments (global and project-specific)
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_environments

# Sync property sets
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    sync_property_sets

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

5. Repository Deletion:
```bash
# Delete repositories listed in a file with parallel processing (dry run)
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_from_file --repo-list-file repos_to_delete.txt --max-workers 8 --dry-run

# Delete all repositories of a specific type with parallel processing
python repo_sync.py --source-url https://source.artifactory --source-token TOKEN1 \
                    --target-url https://target.artifactory --target-token TOKEN2 \
                    delete_repos_by_type --repo-type remote --max-workers 8
```

### Environment Management:
```bash
# Assign environment to a specific repository in source Artifactory
python repo_sync.py --source-url SOURCE --source-token TOKEN1 \
                    --target-url TARGET --target-token TOKEN2 \
                    assign_environment --environment DEV --repo-name my-repo --artifactory source

# Assign environment to all repositories of a specific type in source Artifactory
python repo_sync.py --source-url SOURCE --source-token TOKEN1 \
                    --target-url TARGET --target-token TOKEN2 \
                    assign_environment --environment TEST --repo-type remote --artifactory source

# Assign environment to all repositories in target Artifactory
python repo_sync.py --source-url SOURCE --source-token TOKEN1 \
                    --target-url TARGET --target-token TOKEN2 \
                    assign_environment --environment DEV --artifactory target

# Assign environment to specific repository type in target Artifactory
python repo_sync.py --source-url SOURCE --source-token TOKEN1 \
                    --target-url TARGET --target-token TOKEN2 \
                    assign_environment --environment PROD --repo-type local --artifactory target
```

## Output Files

The script generates several log files:
- Repository Reports:
  - `missing_local_source.log`: Local repositories missing in source
  - `missing_local_target.log`: Local repositories missing in target
  - `missing_federated_source.log`: Federated repositories missing in source
  - `missing_federated_target.log`: Federated repositories missing in target
  - `missing_remote_source.log`: Remote repositories missing in source
  - `missing_remote_target.log`: Remote repositories missing in target
  - `missing_virtual_source.log`: Virtual repositories missing in source
  - `missing_virtual_target.log`: Virtual repositories missing in target
  - `missing_remotes_with_password_source.log`: Remote repositories with passwords missing in target

- Operation Logs:
  - `create_local_errors.log`: Errors when creating local repositories
  - `create_local_success.log`: Successful local repository creations
  - `delete_repos_errors.log`: Failed repository deletions
  - `delete_repos_success.log`: Successful repository deletions
  - `sync_projects_errors.log`: Failed project operations
  - `sync_projects_success.log`: Successful project operations
  - `sync_environments_errors.log`: Failed environment operations
  - `sync_environments_success.log`: Successful environment operations
  - `sync_propertysets_errors.log`: Failed property set operations
  - `sync_propertysets_success.log`: Successful property set operations
  - `update_local_errors.log`: Failed local repository updates
  - `update_local_success.log`: Successful local repository updates
  - `update_remote_errors.log`: Failed remote repository updates
  - `update_remote_success.log`: Successful remote repository updates
  - `update_federated_errors.log`: Failed federated repository updates
  - `update_federated_success.log`: Successful federated repository updates

## Additional Arguments

- `--repo-list-file`: Path to a file containing repository keys to delete (one per line)
- `--repo-type`: Type of repositories to delete (`local`, `remote`, `federated`, `virtual`, `all`)
- `--dry-run`: Preview operations without executing them
- `--max-workers`: Maximum number of parallel workers (default: 4)
- `--debug`: Enable debug output including curl commands
- `--environment`: Environment to assign to created repositories (optional)

## System Repositories

The script excludes these system repositories from operations:
- TOTAL
- auto-trashcan
- jfrog-support-bundle
- jfrog-usage-logs

## Notes

1. Configuration Sync:
   - Projects: Creates missing projects and updates existing ones if different
   - Environments: Syncs both global and project-specific environments
   - Property Sets: Creates missing property sets in target

2. Repository Updates:
   - Supports dry-run mode to preview changes
   - Handles passwords securely for remote repositories
   - Preserves existing configurations where appropriate
   - Generates detailed logs of all operations

3. Security:
   - Requires admin-level access token
   - Handles sensitive information securely
   - Supports secure communication over HTTPS

4. Error Handling:
   - Validates required parameters
   - Provides detailed error messages
   - Logs all operations for troubleshooting
   - Includes dry-run options for testing

## Recommended Flow.

1. Optional:  Find the projects that are missing in the target Artifactory.
```bash
python repo_sync.py  --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    list_missing_projects_target
```
Note: Additional --debug flag is available if you want to get the exact curl commands printed.

2. Create any missing projects in the target Artifactory or update existing projects to reflect any changes, ensuring synchronization with the source Artifactory.
```
jf rt transfer-config-merge SOURCEID TARGETID   --include-repos="" --include-projects="*"
```
or 
```
python repo_sync.py  --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    sync_projects
```
3. Create the missing Global and project environments in the target.
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    sync_environments
```
4. Create the missing Propertyset in the target.. 
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    sync_property_sets
```
5. Create missing local repositories on target
```bash
# Create repositories without environment
python repo_sync.py --source-url $SOURCE --source-token TOKEN1 \
                    --target-url $TARGET --target-token TOKEN2 \
                    create_missing_locals_on_target --max-workers 4

# Create repositories and assign them to an environment
python repo_sync.py --source-url $SOURCE --source-token TOKEN1 \
                    --target-url $TARGET --target-token TOKEN2 \
                    create_missing_locals_on_target --max-workers 4 --environment DEV
```
6. If it fails to create the repos with below message for some repos:

   `"message" : "The repository key '<repokey>' should start with the project key and a dash: 'doc8-'\n"`

then migrate those repo using the semicolon seperated list :
```
jf rt transfer-config-merge SOURCEID TARGETID   --include-repos="repo1;repo2" --include-projects=""
```
**Note:** If you want to avoid running the `/api/system/decrypt` i.e [Deactivate Artifactory Key Encryption](https://jfrog.com/help/r/jfrog-rest-apis/deactivate-artifactory-key-encryption) API you can use the  [Tool to decrypt Artifactory encrypted secrets](https://github.com/sureshvenkatesan/ArtifactoryDecryptor)

---
7. If the repo creation fails with HTTP 400 error
`"message" : "Cannot assign multiple environments to a repository\n"` :

There are 2 options:
a) If you do not want to reassign the environments for the source repos ,
but assign them to a specific environment in target , before creating the missing repos in target use:
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    create_missing_remotes_on_target --max-workers 4 --environment DEV
or
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    create_missing_locals_on_target --max-workers 4 --environment DEV
```

b) If you want to assign the environment to repos in source before running the "create_missing_*" commands ( without the `--environment` optional parameter)
then do:
- Assign environment to one repo in Source:
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    assign_environment --environment DEV --repo-name sv-env-test --artifactory source
```
---
### Assign environment
8. Assign environment to one repo already in  Target Artifactory:
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    assign_environment --environment DEV --repo-name sv-env-test --artifactory target
```
Assign environment to one type of repos or all repos in source or target as:


```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    assign_environment --environment DEV \
                    --repo-type [local | remote | federated | virtual| all] \
                     --artifactory [source | target]
```

---

9. If local repos creation fail with below error:

```
"message" : "HTTP response status 500:Failed to execute add project resource with error UNKNOWN: HTTP status code 500\ninvalid content-type: text/plain; charset=utf-8\nheaders: Metadata(:status=500,content-type=text/plain; charset=utf-8,date=Fri, 31 Jan 2025 16:50:14 GMT,strict-transport-security=max-age=31536000,content-length=21)\nDATA-----------------------------\nInternal Server Error\n"
```
try the "create_missing_*" command repeatedly with `--max-workers 1` or with the  `jf rt transfer-config-merge` command for just one repo that failed and see if it works.

---
10. If some repos still fail the we can exclude them as below and investigate the cause:
```
jf rt transfer-config-merge SOURCEID TARGETID   --include-repos="repo1;repo2"  --exclude-repos "repo3;repo4" --include-projects=""
```
Some of the possible errors could be because the target Artifactory does not have the keypair 
which some Debian or RPM type repos need.

```
{
  "errors": [
    {
      "status": 400,
      "message": "Unable to find KeyPair 'default-gpg-key'\n"
    }
  ]
}
```
---

11. If you have the groups or users then to Sync these  to project roles try:
```
jf proj-sync replicate --dry-run --include-projects "br" \
  SOURCEID TARGETID addroles


jf proj-sync replicate  --include-projects "br" \
  SOURCEID TARGETID addroles
```

12. Sync the  members to role in target based on the source artifactory using:
```
jf proj-sync replicate --dry-run --include-projects "br" \
 SOURCEID TARGETID addmembers

jf proj-sync replicate --include-projects "br" \
 SOURCEID TARGETID addmembers

```
13. If  you want to update existing local repos to reflect any changes, ensuring synchronization with the source Artifactory you can run:
```
python repo_sync.py --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    update_local_repos --max-workers 4
```
14. Similarly create the remote repos in target using:
Note: the remote repos in the target will be created with empty i.e "" passwword.
```bash
# Create repositories without environment
python repo_sync.py --source-url $SOURCE --source-token TOKEN1 \
                    --target-url $TARGET --target-token TOKEN2 \
                    create_missing_remotes_on_target --max-workers 4

# Create repositories and assign them to an environment
python repo_sync.py --source-url $SOURCE --source-token TOKEN1 \
                    --target-url $TARGET --target-token TOKEN2 \
                    create_missing_remotes_on_target --max-workers 4 --environment PROD
```
Similarly update the remote repos in target using:
```
python repo_sync.py  --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    update_remotes_on_target --max-workers 4
```
15. Similarly create or update the virtual repos in target using:
```
python repo_sync.py  --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    create_missing_virtuals_on_target --max-workers 4
```
```
python repo_sync.py  --source-url $SOURCE --source-token $TOKEN1 \
                    --target-url $TARGET --target-token $TOKEN2 \
                    update_virtuals_on_target --max-workers 4
```