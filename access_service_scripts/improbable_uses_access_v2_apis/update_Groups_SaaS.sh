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

groupslist="groups_list.txt"

### define variables
curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/groups" -s  | jq -rc '.groups.[] | .group_name' > $groupslist
gsed -i '/readers/d' "$groupslist"

### Run the curl API 
while IFS= read -r groupsname; do
    echo -e "Download JSON for ====> $groupsname <===="
    curl -XGET -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/groups/$groupsname" -s > "$groupsname.json"
    data=$(echo $groupsname | cut -d '@' -f1)
    updated_groupsname="$data@skyral.io"
    echo -e "\n$updated_groupsname"
    gsed -i "s/$groupsname/$updated_groupsname/g" "$groupsname.json"
    echo -e "\nUploading update GroupName ====> ${updated_groupsname} <==== to ${JPD_URL}"
    curl -XPOST -H "Authorization: Bearer $JPD_AUTH_TOKEN" "${JPD_URL}/access/api/v2/groups" -d @"$groupsname.json" -s -H 'Content-Type: application/json'
    echo -e "\n"
done < $groupslist

### sample cmd to run - ./update_Groups_SaaS.sh https://skyralgroup.jfrog.io ****