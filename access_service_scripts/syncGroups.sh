#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
TARGET_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082}"

SOURCE_JPD_AUTH_TOKEN="${4:?please provide the identity token}"
TARGET_JPD_AUTH_TOKEN="${5:?please provide the identity token}"

rm -rf *.txt
rm -rf *.json

groupListSource="group_list_source.txt"
groupListTarget="group_list_target.txt"
addGroupsList="group_list_to_add.txt"
deleteGroupsList="group_list_to_delete.txt"

### define variables
curl -XGET -H "Authorization: Bearer $SOURCE_JPD_AUTH_TOKEN" "${SOURCE_JPD_URL}/access/api/v2/groups" -s  |  jq -rc '.groups.[] | .group_name' | sort > $groupListSource
curl -XGET -H "Authorization: Bearer $TARGET_JPD_AUTH_TOKEN" "${TARGET_JPD_URL}/access/api/v2/groups" -s  |  jq -rc '.groups.[] | .group_name' | sort > $groupListTarget

diff -u <(sort $groupListTarget) <(sort $groupListSource) --suppress-common-lines | grep '^+' | sed 1d | sed 's/^.//' > $addGroupsList || true
diff -u <(sort $groupListTarget) <(sort $groupListSource) --suppress-common-lines | grep '^-' | sed 1d | sed 's/^.//' > $deleteGroupsList || true

### Run the curl API 
while IFS= read -r groupname; do
    echo -e "Download JSON for group ====> $groupname <===="
    curl -XGET -H "Authorization: Bearer $SOURCE_JPD_AUTH_TOKEN" "${SOURCE_JPD_URL}/access/api/v2/groups/$groupname" -s > "$groupname.json"
    echo -e "\n"
    echo -e "Uploading group ====> $groupname <==== to ${TARGET_JPD_URL}"
    curl -XPOST -H "Authorization: Bearer $TARGET_JPD_AUTH_TOKEN" "${TARGET_JPD_URL}/access/api/v2/groups/$groupname" -d @"$groupname.json" -s -H 'Content-Type: application/json'
    echo -e "\n"
done < $addGroupsList

while IFS= read -r groupname; do
    echo -e "Deleting group ====> $groupname <==== in ${TARGET_JPD_URL}"
    curl -XDELETE -H "Authorization: Bearer $TARGET_JPD_AUTH_TOKEN" "${TARGET_JPD_URL}/access/api/v2/groups/$groupname" -s
    echo -e "\n"
done < $deleteGroupsList

### sample cmd to run - ./syncUser.sh https://ramkannan.jfrog.io http://35.208.78.203:8082  **** ****