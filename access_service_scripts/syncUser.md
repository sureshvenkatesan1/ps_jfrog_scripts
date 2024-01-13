# User Synchronization Script

This Bash script is designed to synchronize user accounts between two JFrog Artifactory instances. It is useful when you want to replicate user accounts from a source Artifactory instance to a target Artifactory instance. The script performs the following tasks:

1. Retrieves a list of users from the source and target Artifactory instances.
2. Compares the user lists to identify users that need to be added or deleted on the target instance.
3. Downloads user details for new users from the source instance and uploads them to the target instance.
4. Delete users from the target instance if it was deleted from the source instance.

## Prerequisites

Before using this script, ensure you have the following prerequisites:

1. Bash shell environment.
2. `curl` and `jq` command-line tools installed.
3. Access to both the source and target JFrog Artifactory instances.
4. Valid credentials and identity tokens for authentication on both instances.

## Usage

To use this script, follow these steps:

1. Make the script executable by running the following command:

   ```bash
   chmod +x syncUser.sh
   ```

2. Execute the script with the required arguments:

   ```bash
   ./syncUser.sh SOURCE_JPD_URL TARGET_JPD_URL USER_NAME SOURCE_JPD_AUTH_TOKEN TARGET_JPD_AUTH_TOKEN
   ```

   Replace the placeholders with the following values:

    - `SOURCE_JPD_URL`: The URL of the source JFrog Artifactory instance (e.g., `https://ramkannan.jfrog.io`).
    - `TARGET_JPD_URL`: The URL of the target JFrog Artifactory instance (e.g., `http://35.208.78.203:8082`).
    - `USER_NAME`: The username used for authentication on both instances (e.g., `admin`).
    - `SOURCE_JPD_AUTH_TOKEN`: The identity token for the source JFrog Artifactory instance.
    - `TARGET_JPD_AUTH_TOKEN`: The identity token for the target JFrog Artifactory instance.

3. The script will perform the following tasks:
    - Retrieve user lists from both instances.
    - Compare user lists to identify new users to add and users to delete on the target instance.
    - Download user details for new users and upload them to the target instance.
    - Delete users from the target instance if it was deleted from the source instance.

## Disclaimer

This script is provided as-is and without any warranties or conditions. It is intended for use in connection with JFrog products or services and may require customization for your specific environment. JFrog does not convey any rights or titles in the code other than for the limited use right set forth in the provided license.

Please ensure that you have appropriate permissions and test the script in a safe environment before using it in production.