#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
FILE_NAME="${1:?please provide the file name to parse. ex - diffFile.txt}"
SOURCE_JPD_URL="${2:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
TARGET_JPD_URL="${3:?please enter JPD URL. ex - http://35.209.109.173:8082}"
USER_NAME="${4:?please provide the username in JPD . ex - admin}"
AUTH_TOKEN_JPD_1="${5:?please provide the user identity token for source}"
METHOD="${6:?please provide method to perform . ex - PUT to create or POST for update}"
AUTH_TOKEN_JPD_2="${7:?please provide the user identity token for target}"

rm -rf *.json
oldprojectkey="int"
newprojectkey="cpein"

### parse file
while IFS= read -r line; do
    if [[ $line == *"+"* ]]; then
        repoadd=$(echo $line | cut -d "+" -f2 | xargs)
        echo -e "\nAdd Repo ==> $repoadd"
        echo -e "Exporting JSON for $repoadd from $SOURCE_JPD_URL"
        curl -X GET -u "${USER_NAME}":"${AUTH_TOKEN_JPD_1}" "$SOURCE_JPD_URL/artifactory/api/repositories/$repoadd" -s > "$repoadd.json"

        sed -i '' "s/$oldprojectkey/$newprojectkey/g" "$repoadd.json"

        sleep 10

        projectkey=$(cat "$repoadd.json" | jq .projectKey | xargs)
        key=$(cat "$repoadd.json" | jq .key | xargs)
        echo "Project Key = $projectkey"
        if [[ "$projectkey" == "null" ]]; then
            echo "projectkey not replaced properly"
        else 
            echo "Project Key $projectkey with reponame as $key is present in $repoadd"
            echo -e "Importing JSON $repoadd.json to $TARGET_JPD_URL"
            if [[ $METHOD == "create" ]]; then
                curl -X PUT -u "${USER_NAME}":"${AUTH_TOKEN_JPD_2}" "$TARGET_JPD_URL/artifactory/api/repositories/$key" -d @"$repoadd.json" -s -H 'Content-Type: application/json'
            else
                echo -e "\nInvalid Method given in arguments"
            fi
            sleep 5
        fi
        echo -e "\n"
    elif [[ $line == *"-"* ]]; then
        repodelete=$(echo $line | cut -d "-" -f2- | xargs)
        echo -e "\nDelete Repo ==> $repodelete"
        #curl -X DELETE -u "${USER_NAME}":"${AUTH_TOKEN_JPD_2}" "$TARGET_JPD_URL/artifactory/api/repositories/$repodelete"
    else 
        echo -e "\nInvalid Input"
    fi
done < $FILE_NAME

### sample cmd to run - ./updateRepoDiffConfigJPD.sh diffFile.txt https://ramkannan.jfrog.io http://35.209.109.173:8082 admin **** create ****