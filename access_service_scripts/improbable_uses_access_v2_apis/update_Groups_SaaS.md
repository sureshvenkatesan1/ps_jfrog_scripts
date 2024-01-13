# Update_Groups_SaaS.sh

## Overview

The `update_Groups_SaaS.sh` script is designed to automate the update of groups in a JFrog Artifactory instance, especially focusing on groups with a specific name pattern. This script is intended for use in a JFrog SaaS (Software as a Service) environment.

Before running the script, please note the following:

- This script is provided by JFrog and is subject to specific terms and conditions mentioned in the script header.

- It uses the JFrog Platform Deployment (JPD) API to interact with your Artifactory instance.

- The script expects two command-line arguments: the JPD URL and an Identity token for authentication.

- The groups to be updated are filtered based on their names, and certain groups (e.g., "readers") are excluded from the update.

- The group names are modified to use the "@skyral.io" domain.

## Usage

To run the script, use the following command:

```bash
./update_Groups_SaaS.sh <JPD_URL> <JPD_AUTH_TOKEN>
```

Replace `<JPD_URL>` with the URL of your JPD instance and `<JPD_AUTH_TOKEN>` with your Identity token.

**Note**: Ensure that you have appropriate permissions and have backed up any group data or configurations before running this script, as it will update group names.

## Script Workflow

The script follows these main steps:

1. Set up error handling to exit the script on any failures.

2. Get the JPD URL and Identity token as command-line arguments.

3. Clean up any existing JSON and text files used for temporary storage.

4. Define a variable for the group list file (`groups_list.txt`).

5. Use the JPD API to retrieve a list of groups and save their names in `groups_list.txt`. Some groups (e.g., "readers") are filtered out from the list.

6. Loop through the list of group names in `groups_list.txt`.

7. For each group name, download the group's information in JSON format using the JPD API. This information includes the group's data, which is then parsed.

8. Update the group's name to include the "@skyral.io" domain.

9. Save the updated group information in a new JSON file (`$groupsname.json`).

10. Use the JPD API to create a new group with the updated information in Artifactory.

11. The script repeats this process for all group names in the list.

12. The script is now complete, and the groups have been updated with the specified modifications.

## Sample Command

Here is a sample command to run the script:

```bash
./update_Groups_SaaS.sh https://skyralgroup.jfrog.io ****
```

Replace `"https://skyralgroup.jfrog.io"` with your JPD URL, and `"****"` with your Identity token.

## Disclaimer

Please use this script with caution, as it can modify group data in your JFrog Artifactory instance. Ensure that you have appropriate backups and permissions in place before running the script in a production environment.