# JFrog List Users in Permissions 

[list_users_in_perm_w_jf.sh](list_users_in_perm_w_jf.sh) script is designed to fetch a list of permissions targets and their associated user lists from a JFrog Artifactory instance using the JFrog CLI. It simplifies the process of querying permissions and user information, helping you manage access control efficiently.

## Prerequisites

Before using this script, ensure the following prerequisites are met:

1. **JFrog CLI**: Make sure you have the JFrog CLI installed and configured with the necessary server credentials. You can download it from the official JFrog website and configure it using `jf rt c` command.

## Usage

To use the script, follow these steps:

1. Make the script executable if it's not already:

   ```bash
   chmod +x list_users_in_perm_w_jf.sh
   ```

2. Run the script with the JFrog server-id as an argument:

   ```bash
   ./list_users_in_perm_w_jf.sh <server-id>
   ```

   Replace `<server-id>` with the server-id of your JFrog Artifactory instance.

## Script Overview

The script performs the following actions:

1. Retrieves a list of permissions targets from the specified JFrog Artifactory instance.
2. Filters out permissions with "INTERNAL" in their names.
3. Sorts and sanitizes the permissions target list and saves it to `permissions_target_list.txt`.

For each permissions target, the script:

1. Retrieves the user list associated with the permissions target.
2. Writes the permission name and associated users to `userlist.txt`.

Both the permissions target list and userlist files are created in the script's directory.

## Disclaimer

This script is provided by JFrog "as-is" and without any warranties or conditions. It is intended to be used in connection with your use of a JFrog product or service. JFrog grants you a non-exclusive, non-transferable, non-distributable right to use this code for the limited use right set forth herein.

