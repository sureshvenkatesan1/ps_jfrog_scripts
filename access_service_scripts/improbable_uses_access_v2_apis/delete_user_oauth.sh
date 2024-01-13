#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

### Exit the script on any failures
set -eo pipefail
set -e
set -u

rm -rf *.txt
rm -rf *.json

### Get Arguments
JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
JPD_AUTH_TOKEN="${2:?please provide the identity token}"

### define variables
userlist="delete_users.txt"
curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/users" -s | jq -rc '.users.[] | select( .realm == "internal" ) | .username' | grep "@skyral.io" | sort > $userlist

### Run the curl API 
while IFS= read -r username; do
    echo -e "Deleting user == $username =="
    curl -XDELETE -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/users/${username}" -s
    echo -e ""
done < $userlist

### sample cmd to run - ./delete_user_oauth.sh https://ramkannan.jfrog.io ****