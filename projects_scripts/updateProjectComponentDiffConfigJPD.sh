#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
FILE_NAME="${1:?please provide the file name to parse. ex - diffFile.txt}"
SOURCE_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082}"
TARGET_JPD_URL="${3:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
SOURCE_AUTH_TOKEN="${4:?please provide auth bearer token . ex - access token}"  ### diffes across 3 JPD's
TARGET_AUTH_TOKEN="${5:?please provide auth bearer token . ex - access token}"  ### diffes across 3 JPD's
data="${6:?please provide the data to be collected . ex - users / groups / roles}"
projectname="${7:?please provide the project id . ex - dp1}"

rm -rf *.json

### parse file
while IFS= read -r line; do
    if [[ $line == *"+"* ]]; then
        dataadd=$(echo $line | cut -d "+" -f2 | xargs | sed 's/ /%20/g')
        createdata=$data"_"$dataadd
        echo -e "\nAdd $createdata ==> $dataadd"
        echo -e "Exporting JSON for $data"add" from $SOURCE_JPD_URL"
        echo "curl -XGET -H "Authorization: Bearer ${SOURCE_AUTH_TOKEN}" "$SOURCE_JPD_URL/access/api/v1/projects/$projectname/$data/$dataadd" -s > "$createdata.json""
        curl -XGET -H "Authorization: Bearer ${SOURCE_AUTH_TOKEN}" "$SOURCE_JPD_URL/access/api/v1/projects/$projectname/$data/$dataadd" -s > "$createdata.json"
        echo -e "Importing JSON $createdata.json to $TARGET_JPD_URL"
        if [[ $data == "roles" ]]; then
            curl -XPOST -H "Authorization: Bearer ${TARGET_AUTH_TOKEN}" "$TARGET_JPD_URL/access/api/v1/projects/$projectname/$data" -d @"$createdata.json" -s -H 'Content-Type: application/json'
        else
            curl -XPUT -H "Authorization: Bearer ${TARGET_AUTH_TOKEN}" "$TARGET_JPD_URL/access/api/v1/projects/$projectname/$data/$dataadd" -d @"$createdata.json" -s -H 'Content-Type: application/json'
        fi
        echo -e "\n"
    elif [[ $line == *"-"* ]]; then
        datadelete=$(echo $line | cut -d "-" -f2- | xargs)
        deletedata=$data"_"$datadelete
        echo -e "\nDelete $data"delete" ==> $datadelete"
        curl -XDELETE -H "Authorization: Bearer ${TARGET_AUTH_TOKEN}" "$TARGET_JPD_URL/access/api/v1/projects/$projectname/$data/$datadelete"
        echo -e ""
    else 
        echo -e "\nInvalid Input\n"
    fi
done < $FILE_NAME

### sample cmd to run - ./getProjectComponentDiffConfigJPD.sh diffFile.txt https://ramkannan.jfrog.io http://35.208.78.203:8082 **** **** users/groups/roles <project_name>