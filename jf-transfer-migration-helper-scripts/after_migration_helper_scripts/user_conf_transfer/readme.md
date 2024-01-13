# JFrog User Sync Script

The primary function of this script is to facilitate the synchronization of user-specific configurations, encompassing group memberships and permission target associations, for a specified set of users. This synchronization occurs between a source JFrog Platform instance and a destination JFrog Platform instance.

It's crucial to understand that this script functions specifically at the user level, focusing on identifying and handling permission adjustments from the standpoint of individual users. If you happen to make direct modifications to groups within a permission target, it's important to note that this script may not address such changes. Consequently, it can serve as a valuable reference for customizing the script to accommodate similar scenarios.

**Note:** REST API calls require JFrog Platform version >= 7.49.3.

## Prerequisites

Before running the script, ensure you have the following prerequisites:

- [jq](https://stedolan.github.io/jq/) tool installed. You can install it using your package manager.

## Usage

```bash
./user_conf_transfer.sh <SRC_JPD_URL> <SRC_JPD_AUTH_TOKEN> <DST_JPD_URL> <DST_JPD_AUTH_TOKEN> <USER_LIST_STR> <DRY_RUN>

<SRC_JPD_URL>: URL of the source JFrog Platform instance (e.g., https://srcjpd.jfrog.io).
<SRC_JPD_AUTH_TOKEN>: Authentication token for the admin user in the source JFrog Platform instance.
<DST_JPD_URL>: URL of the destination JFrog Platform instance (e.g., https://dstjpd.jfrog.io).
<DST_JPD_AUTH_TOKEN>: Authentication token for the admin user in the destination JFrog Platform instance.
<USER_LIST_STR>: Comma-separated list of users to sync (e.g., "user1,user2,user3").
<DRY_RUN>: Specify "yes" for a dry run or "no" for a real execution.
```

## Output
The script performs the following actions:

1. Checks if the jq tool is available.
2. Defines a function to hide the Authorization token in the script's output.
3. Validates admin access on source and destination JFrog Platform endpoints.
4. Iterates through the list of users to perform the following actions for each user:
    - Checks if the user exists in the source JFrog Platform instance.
    - If the user does not exist in the destination JFrog Platform instance, it creates a new user.
    - Checks the user's group memberships and adds them to the destination if needed.
    - Checks the user's permission targets and adds them to the destination if needed.

## Example
```
./user_conf_transfer.sh https://srcjpd.jfrog.io <SRC_JPD_AUTH_TOKEN> https://dstjpd.jfrog.io <DST_JPD_AUTH_TOKEN> "user1,user2,user3" yes
```

If a user user1@xyz.com has recently been added to the groups ASD-Conan-Dev and Artifact-ASD-All in the source JFrog Platform instance (e.g., https://srcjpd.jfrog.io) then DRY_RUN shows the curl commands that will be run as below on the target  JFrog Platform instance.

Then for a real execution pass value "no" for  DRY_RUN.

`Sample Output in DRY_RUN mode "yes" :`

```
SRC_JPD_URL: https://srcjpd.jfrog.io
DST_JPD_URL: https://dstjpd.jfrog.io
USER_LIST: user1@xyz.com
DRY_RUN: yes

INFO: Processing user: user1@xyz.com
INFO: User: user1@xyz.com is found in destination JPD. So skipping. API Response: 200
INFO: User user1@xyz.com is member of ASD-Conan-Dev,Artifact-ASD-All group(s).
INFO: Add group ASD-Conan-Dev for user user1@xyz.com
INFO: User group ASD-Conan-Dev is already present in destination JPD.
API CALL: curl --write-out %{http_code} --output /dev/null -k -s -HAuthorization: Bearer *** -H Content-Type: application/json -XPATCH https://dstjpd.jfrog.io/access/api/v2/users/user1@xyz.com/groups --data {"add": ["ASD-Conan-Dev"]}
INFO: Add group Artifact-ASD-All for user user1@xyz.com
INFO: User group Artifact-ASD-All is already present in destination JPD.
API CALL: curl --write-out %{http_code} --output /dev/null -k -s -HAuthorization: Bearer *** -H Content-Type: application/json -XPATCH https://dstjpd.jfrog.io/access/api/v2/users/user1@xyz.com/groups --data {"add": ["Artifact-ASD-All"]}
INFO: User user1@xyz.com is part of ASD-Conan-Dev,ASD-Remote,ASD-All permission target(s).
INFO: Checking permission target: ASD-Conan-Dev for user user1@xyz.com
INFO: Permission target ASD-Conan-Dev is already present in destination JPD.
INFO: No updates needed on existing permission target ASD-Conan-Dev.
INFO: Checking permission target: ASD-Remote for user user1@xyz.com
INFO: Permission target ASD-Remote is already present in destination JPD.
INFO: No updates needed on existing permission target ASD-Remote.
INFO: Checking permission target: ASD-All for user user1@xyz.com
INFO: Permission target ASD-All is already present in destination JPD.
INFO: No updates needed on existing permission target ASD-All.
THE END
```