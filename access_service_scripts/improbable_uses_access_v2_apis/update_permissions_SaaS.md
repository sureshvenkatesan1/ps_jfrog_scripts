# Update_Permissions_SaaS.sh

## Overview

The `update_permissions_SaaS.sh` script is designed to automate the update of permissions in a JFrog Artifactory instance, specifically focusing on permissions that involve groups. This script is intended for use in a JFrog SaaS (Software as a Service) environment.

Before running the script, please note the following:

- This script is provided by JFrog and is subject to specific terms and conditions mentioned in the script header.

- It uses the JFrog Platform Deployment (JPD) API to interact with your Artifactory instance.

- The script expects two command-line arguments: the JPD URL and an Identity token for authentication.

- The permissions to be updated are retrieved from the Artifactory instance and are filtered to exclude specific permissions (e.g., "Anything" and "Any Remote").

- The script then checks if each permission has associated groups and proceeds to update them.

- The permissions are updated by changing the domain from "@improbable.io" to "@skyral.io."

## Usage

To run the script, use the following command:

```bash
./update_permissions_SaaS.sh <JPD_URL> <JPD_AUTH_TOKEN>
```

Replace `<JPD_URL>` with the URL of your JPD instance and `<JPD_AUTH_TOKEN>` with your Identity token.

**Note**: Ensure that you have appropriate permissions and have backed up any permission data or configurations before running this script, as it will update permissions.

## Script Workflow

The script follows these main steps:

1. Set up error handling to exit the script on any failures.

2. Get the JPD URL and Identity token as command-line arguments.

3. Clean up any existing JSON and text files used for temporary storage.

4. Define a variable for the permission list file (`permissions_list.txt`).

5. Use the JPD API to retrieve a list of permissions and save their names in `permissions_list.txt`. Some permissions (e.g., "Anything" and "Any Remote") are filtered out from the list.

6. Loop through the list of permission names in `permissions_list.txt`.

7. For each permission, run a series of `curl` and `jq` commands to check if the permission has associated groups. If groups are found, the permission name is added to a list called `perm_with_groups.txt`.

8. Loop through the list of permissions with associated groups (`perm_with_groups.txt`).

9. For each permission, download the permission's information in JSON format using the JPD API. This information includes the permission's data, which is then parsed.

10. Update the permission by changing the domain in group names from "@improbable.io" to "@skyral.io."

11. Save the updated permission information in a new JSON file (`$permission_with_groups.json`).

12. Use the JPD API to create a new permission with the updated information in Artifactory.

13. The script is now complete, and the permissions have been updated with the specified modifications.

## Sample Command

Here is a sample command to run the script:

```bash
./update_permissions_SaaS.sh https://skyralgroup.jfrog.io ****
```

Replace `"https://skyralgroup.jfrog.io"` with your JPD URL, and `"****"` with your Identity token.

## Disclaimer

Please use this script with caution, as it can modify permission data in your JFrog Artifactory instance. Ensure that you have appropriate backups and permissions in place before running the script in a production environment.