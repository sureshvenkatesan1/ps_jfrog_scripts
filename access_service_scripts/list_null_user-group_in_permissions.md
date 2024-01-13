# List_Null_User_Group_in_Permissions

## Overview

The `list_null_user-group_in_permissions.sh` script is designed to list permissions in a JFrog Artifactory instance where either user or group information is missing. Specifically, it identifies permissions that have null or empty user/group lists. This script is intended for use in a JFrog SaaS (Software as a Service) environment.

Before running the script, please note the following:

- This script is provided by JFrog and is subject to specific terms and conditions mentioned in the script header.

- It uses the JFrog Platform Deployment (JPD) API to interact with your Artifactory instance.

- The script expects three command-line arguments: the JPD URL, a username in JPD, and an Identity token for authentication.

- The script retrieves a list of permissions from the Artifactory instance and checks for permissions with null or empty user or group lists.

- Permissions with null or empty user or group lists are listed in separate text files (`perm_delete_users.txt` and `perm_delete_groups.txt`).

## Usage

To run the script, use the following command:

```bash
./list_null_user-group_in_permissions.sh <JPD_URL> <USER_NAME> <USER_TOKEN>
```

Replace `<JPD_URL>` with the URL of your JPD instance, `<USER_NAME>` with your JPD username, and `<USER_TOKEN>` with your Identity token.

**Note**: Ensure that you have appropriate permissions and have backed up any permission data or configurations before running this script, as it identifies permissions for potential deletion.

## Script Workflow

The script follows these main steps:

1. Set up error handling to exit the script on any failures.

2. Get the JPD URL, username, and Identity token as command-line arguments.

3. Clean up any existing JSON, log, and text files used for temporary storage.

4. Define a variable for the permission target list file (`permissions_target_list.txt`).

5. Use the JPD API to retrieve a list of permissions and save their names in `permissions_target_list.txt`. Permissions with specific names (e.g., "INTERNAL") are filtered out from the list.

6. Loop through the list of permission names in `permissions_target_list.txt`.

7. For each permission, download the permission's information in JSON format using the JPD API. This information includes the permission's data, including user and group information.

8. Check if the permission has null or empty user lists. If so, add the permission name to `perm_delete_users.txt`.

9. Check if the permission has null or empty group lists. If so, add the permission name to `perm_delete_groups.txt`.

10. Combine the two lists (`perm_delete_users.txt` and `perm_delete_groups.txt`) to identify permissions with null or empty user or group lists and save them to `perm_delete.txt`.

## Sample Command

Here is a sample command to run the script:

```bash
./list_null_user-group_in_permissions.sh https://ramkannan.jfrog.io admin ****
```

Replace `"https://ramkannan.jfrog.io"` with your JPD URL, `"admin"` with your JPD username, and `"****"` with your Identity token.

## Disclaimer

Please use this script with caution, as it identifies permissions for potential deletion in your JFrog Artifactory instance. Ensure that you have appropriate backups and permissions in place before running the script in a production environment.