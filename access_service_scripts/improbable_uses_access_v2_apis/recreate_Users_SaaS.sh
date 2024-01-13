#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
JPD_URL="${1:?please enter JPD URL. ex - https://skyralgroup.jfrog.io}"
JPD_AUTH_TOKEN="${2:?please provide the identity token}"

rm -rf *.txt
rm -rf *.json

userlist="users_oauth_list.txt"

### define variables
curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/users" -s | jq -rc '.users.[] | select( .realm == "oauth" ) | .username' | grep "@improbable.io" | sort > $userlist

### Run the curl API 
while IFS= read -r username; do
    echo -e "Download JSON for ====> $username <===="
    curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/users/$username" -s > "$username.json"
    echo -e "\n"
    user_data="jq '. | .\"$username\"' ../sykrl-users.json | xargs"
    email_data="echo $username | cut -d @ -f1"
    updated_username=$(eval $user_data)
    updated_email=$(eval $email_data)
    echo -e "Uploading user ====> ${updated_username} and email $updated_username@skyral.io <==== to ${JPD_URL}"
    jq --arg user_variable "$updated_username" --arg email_variable "$updated_username@skyral.io" '.username = $user_variable | .email = $email_variable | .internal_password_disabled = false | .password="@World10"' "$username.json" > "updated_$username.json"
    curl -XPATCH -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/users/$updated_username" -d @"updated_$username.json" -s -H 'Content-Type: application/json'
    echo -e "\n"
done < $userlist

### sample cmd to run - ./recreate_Users_SaaS.sh https://skyralgroup.jfrog.io ****