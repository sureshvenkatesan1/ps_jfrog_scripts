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

permissionslist="permissions_list.txt"

### define variables
curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/permissions" -s | jq -rc '.permissions.[] | .name' | sed 's/ /%20/g' | sort > $permissionslist
gsed -i '/Anything/d' "$permissionslist"
gsed -i '/Any%20Remote/d' "$permissionslist"

### Run the curl API 
while IFS= read -r permission; do
    data="curl -XGET -H \"Authorization: Bearer $JPD_AUTH_TOKEN\" \"${JPD_URL}/access/api/v2/permissions/$permission\" -s | jq -rc '.resources.artifact.actions.groups' | jq -r 'keys[]'"
    group_data=$(eval $data)
    if [ -z "$group_data" ]; then
        echo "$permission has no groups"
    else
        echo "$permission has GROUPS...."
        echo "$permission" >> "perm_with_groups.txt"
    fi
done < "$permissionslist"

while IFS= read -r permission_with_groups; do
    echo -e "Download JSON for ====> $permission_with_groups <===="
    curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/permissions/$permission_with_groups" -s > "$permission_with_groups.json"
    gsed -i "s/@improbable.io/@skyral.io/g" "$permission_with_groups.json"
    echo -e "\nUploading updated Permission ====> ${permission_with_groups} <==== to ${JPD_URL}"
    cat "$permission_with_groups.json"
    curl -XPOST -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/permissions" -d @"$permission_with_groups.json" -s -H 'Content-Type: application/json'
    echo -e "\n"
done < "perm_with_groups.txt"

### sample cmd to run - ./update_permissions_SaaS.sh https://skyralgroup.jfrog.io ****