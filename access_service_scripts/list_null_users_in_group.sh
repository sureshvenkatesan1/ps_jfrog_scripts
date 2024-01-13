#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right 
# to use this  code   solely in connection with your use of a JFrog product or service. 
# This  code is provided 'as-is' and without any warranties or conditions, either 
# express or implied including, without limitation, any warranties or conditions of 
# title, non-infringement, merchantability or fitness for a particular cause. 
# Nothing herein shall convey to you any right or title in the code, other than 
# for the limited use right set forth herein. For the purposes hereof "you" shall
# mean you as an individual as well as the organization on behalf of which you
# are using the software and the JFrog product or service. 

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
USER_NAME="${2:?please provide the username in JPD . ex - admin}"
USER_TOKEN="${3:?please provide the identity token}"

groups_target_list="groups_target_list.txt"

rm -rf *.txt
rm -rf *.json*

curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/groups" -s | jq -rc '.[] | .name' > $groups_target_list

echo -e "\nGROUPS LIST"
while IFS= read -r groups; do
    echo -e "\nGetting JSON for Group ==> $groups"\
    curl -XGET -u $USER_NAME:$USER_TOKEN "$SOURCE_JPD_URL/artifactory/api/security/groups/$groups?includeUsers=true" -s | jq -rcS .userNames | jq -r ''
done < $groups_target_list


### sample cmd to run - ./list_null_users_in_group.sh https://ramkannan.jfrog.io admin ****