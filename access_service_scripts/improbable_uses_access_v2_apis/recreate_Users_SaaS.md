# Recreate_Users_SaaS.sh

## Overview

The `recreate_Users_SaaS.sh` script is designed to automate the recreation of users in a JFrog Artifactory instance, particularly focusing on users using OAuth authentication from a specific domain (e.g., "@improbable.io"). This script is intended for use in a JFrog SaaS (Software as a Service) environment.

Before running the script, please note the following:

- This script is provided by JFrog and is subject to specific terms and conditions mentioned in the script header.

- It uses the JFrog Platform Deployment (JPD) API to interact with your Artifactory instance.

- The script expects two command-line arguments: the JPD URL and an Identity token for authentication.

- The users to be recreated are filtered based on their realm ("oauth") and domain ("@improbable.io"). You can adjust this filter as needed.

- The recreated users will have their email addresses updated to use the "@skyral.io" domain and will have their internal password enabled with the default password "@World10".

## Usage

To run the script, use the following command:

```bash
./recreate_Users_SaaS.sh <JPD_URL> <JPD_AUTH_TOKEN>
```

Replace `<JPD_URL>` with the URL of your JPD instance and `<JPD_AUTH_TOKEN>` with your Identity token.

**Note**: Ensure that you have appropriate permissions and have backed up any user data or configurations before running this script, as it will recreate users.

## Script Workflow

The script follows these main steps:

1. Set up error handling to exit the script on any failures.

2. Get the JPD URL and Identity token as command-line arguments.

3. Clean up any existing JSON and text files used for temporary storage.

4. Define a variable for the user list file (`users_oauth_list.txt`).

5. Use the JPD API to retrieve a list of users with the realm "oauth" and filter them by domain ("@improbable.io"). The list of filtered usernames is saved in `users_oauth_list.txt`.

6. Loop through the list of usernames in `users_oauth_list.txt`.

7. For each username, download their user information in JSON format using the JPD API. This information includes the user's data, which is then parsed.

8. Update the user's email address to use the "@skyral.io" domain, enable the internal password, and set a default password.

9. Save the updated user information in a new JSON file (`updated_$username.json`).

10. Use the JPD API to patch (update) the user's information in Artifactory using the updated JSON file.

11. Repeat this process for all usernames in the list.

12. The script is now complete, and the users have been recreated with the specified modifications.

## Sample Command

Here is a sample command to run the script:

```bash
./recreate_Users_SaaS.sh https://skyralgroup.jfrog.io ****
```

Replace `"https://skyralgroup.jfrog.io"` with your JPD URL, and `"****"` with your Identity token.

## Disclaimer

Please use this script with caution, as it can modify user data in your JFrog Artifactory instance. Ensure that you have appropriate backups and permissions in place before running the script in a production environment.