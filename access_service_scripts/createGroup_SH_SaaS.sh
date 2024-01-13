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
TARGET_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082}"
USER_NAME="${3:?please provide the username in JPD . ex - admin}"
SOURCE_JPD_AUTH_TOKEN="${4:?please provide the identity token}"
TARGET_JPD_AUTH_TOKEN="${5:?please provide the identity token}"

rm -rf *.txt
rm -rf *.json

grouplist="group_internal_list.txt"

### define variables
curl -XGET -u $USER_NAME:$SOURCE_JPD_AUTH_TOKEN "${SOURCE_JPD_URL}/artifactory/api/security/groups" -s | jq -rc '.[] | select( .realm == "internal" ) | .name' | sort > $grouplist

### Run the curl API 
while IFS= read -r groupname; do
    echo -e "Download JSON for ====> $groupname <===="
    curl -XGET -u $USER_NAME:$SOURCE_JPD_AUTH_TOKEN "${SOURCE_JPD_URL}/artifactory/api/security/groups/$groupname" -s > "$groupname.json"
    echo -e "\n"
    echo -e "Uploading group ====> $groupname <==== to ${TARGET_JPD_URL}"
    curl -XPUT -u $USER_NAME:$TARGET_JPD_AUTH_TOKEN "${TARGET_JPD_URL}/artifactory/api/security/groups/$groupname" -d @"$groupname.json" -s -H 'Content-Type: application/json'
    echo -e "\n"
done < $grouplist

### sample cmd to run - ./createGroup_SH_SaaS.sh https://ramkannan.jfrog.io http://35.208.222.60:8082 admin **** ****