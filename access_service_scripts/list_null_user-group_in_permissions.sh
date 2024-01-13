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

SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
USER_NAME="${2:?please provide the username in JPD . ex - admin}"  
USER_TOKEN="${3:?please provide the identity token}" 

permissions_target_list="permissions_target_list.txt"

#rm -rf *.txt
rm -rf *.json*
rm -rf *.log

#curl -XGET -u $USER_NAME:$USER_TOKEN $SOURCE_JPD_URL/artifactory/api/security/users -s | jq -rc '.[] | select( .realm == "ldap" ) | .name' > ldap_users.txt

curl -XGET -u $USER_NAME:$USER_TOKEN $SOURCE_JPD_URL/artifactory/api/security/permissions -s | jq -rc '.[] | .name' | grep -v "INTERNAL" | sort | sed 's/ /%20/g' > $permissions_target_list

echo -e "USERS LIST"
while IFS= read -r permissions; do
    echo -e "\nGetting JSON for Permission Target ==> $permissions"
    curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/permissions/$permissions" -s > $permissions.json
    curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/permissions/$permissions" -s | jq -rcS .principals.users | jq -r 'keys[]' > "$permissions"_UserList.txt
    if [[ $? != 0 ]]; then
        echo "$permissions" >> perm_delete_users.txt
    fi
done < $permissions_target_list

echo -e "\nGROUPS LIST"
while IFS= read -r permissions; do
    echo -e "\nGetting JSON for Permission Target ==> $permissions"
    curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/permissions/$permissions" -s > $permissions.json
    curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/permissions/$permissions" -s | jq -rcS .principals.groups | jq -r 'keys[]' > "$permissions"_UserList.txt
    if [[ $? != 0 ]]; then
        echo "$permissions" >> perm_delete_groups.txt
    fi
done < $permissions_target_list

sort perm_delete_users.txt perm_delete_groups.txt | awk 'dup[$0]++ == 1' > perm_delete.txt

### sample cmd to run - ./list_null_user-group_in_permissions.sh https://ramkannan.jfrog.io admin ****