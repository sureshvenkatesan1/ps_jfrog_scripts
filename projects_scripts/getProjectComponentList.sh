#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
JPD_TYPE="${2:?please provide jpd type . ex - source / jpd1 / jpd2}"
data="${3:?please provide the data to be collected . ex - users / groups / roles}"
AUTH_TOKEN="${4:?please provide identity token}"

### define variables
file="${data}.txt"
datafile="${data}_list"
FILE_NAME="project-list.txt"

### Run the curl API 
while IFS= read -r projectname; do
    echo $projectname
    curl -XGET -H "Authorization: Bearer ${AUTH_TOKEN}" "${JPD_URL}/access/api/v1/projects/$projectname/${data}" -s > "$JPD_TYPE"_"$projectname"_"$file"
        while IFS= read -r name; do
            if [[ $data == *"roles"* ]]; then
                jq -r '.[].name' "$JPD_TYPE"_"$projectname"_"$file" | sort > "$datafile"_"$projectname"_"$JPD_TYPE".txt
            else 
                jq '.members[] | .name' -r "$JPD_TYPE"_"$projectname"_"$file" > "$datafile"_"$projectname"_"$JPD_TYPE".txt
            fi
        done < "$JPD_TYPE"_"$projectname"_"$file"
done < $FILE_NAME

### sample cmd to run - ./getProjectComponentList.sh  https://ramkannan.jfrog.io source users/groups/roles ****