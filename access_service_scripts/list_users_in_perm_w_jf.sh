#!/bin/bash
# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right
# to use this  code   solely in connection with your use of a JFrog product or service.
# This  code is provided 'as-is' and without any warranties or conditions, either
# express or implied including, without limitation, any warranties or conditions of
# title, non-infringement, merchantability or fitness for a particular cause.
# Nothing herein shall convey to you any right or title in the code, other than
# for the limited use right set forth herein. For the purposes hereof "you" shall
# mean you as an individual as well as the organization on behalf of which you
# are using the software and the JFrog product or service.

SERVER_ID="${1:?please provide the JFrog server-id}"
PERMISSIONS_TARGET_LIST="permissions_target_list.txt"
USERLIST_FILE="userlist.txt"

# Clean up previous files
rm -rf *.txt
rm -rf *.json*

# Get a list of permissions targets
jf rt curl /api/security/permissions -s --server-id $SERVER_ID | jq -rc '.[] | .name' | grep -v "INTERNAL" | sort | sed 's/ /%20/g' > $PERMISSIONS_TARGET_LIST

echo -e "USERS LIST"
while IFS= read -r permissions; do
    echo -e "\nGetting User List for == $permissions =="
    echo -e "\nPermission Name == $permissions ==" >> $USERLIST_FILE
    jf rt curl "/api/security/permissions/$permissions" -s --server-id $SERVER_ID | jq -rcS .principals.users | jq -r 'keys[]' >> $USERLIST_FILE
done < $PERMISSIONS_TARGET_LIST
