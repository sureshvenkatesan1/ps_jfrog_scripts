#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
TARGET_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082}"
TYPE="${3:?please enter type of repo. ex - local, remote, virtual, federated, all}"
USER_NAME="${4:?please provide the username in JPD . ex - admin}"
AUTH_TOKEN_JPD_1="${5:?please provide the user pwd or token or API Key . ex - password}"
AUTH_TOKEN_JPD_2="${6:?please provide access token to move project}"

### define variables
reposfile="repos_list_${TYPE}.txt"

### Run the curl API 
rm -rf *.json
rm -rf *.txt

if [[ $TYPE == "all" ]]; then
    curl -X GET -H 'Content-Type: application/json' -u "${USER_NAME}":"${AUTH_TOKEN_JPD_1}" "${SOURCE_JPD_URL}/artifactory/api/repositories" -s | jq -rc '.[] | .key' > $reposfile
else
    curl -X GET -H 'Content-Type: application/json' -u "${USER_NAME}":"${AUTH_TOKEN_JPD_1}" "${SOURCE_JPD_URL}/artifactory/api/repositories?type=${TYPE}" -s | jq -rc '.[] | .key' > $reposfile
fi
cat "repos_list_${TYPE}.txt"

while IFS= read -r repoadd; do
    echo -e "\nExporting JSON for $repoadd from $SOURCE_JPD_URL"
    curl -X GET -u "${USER_NAME}":"${AUTH_TOKEN_JPD_1}" "$SOURCE_JPD_URL/artifactory/api/repositories/$repoadd" -s > "$repoadd.json"
    projectkey=$(cat "$repoadd.json" | jq .projectKey | xargs)
    echo -e "Project Key = $projectkey"
    if [[ "$projectkey" == "null" ]]; then
      echo -e "Skipping for Repo - $repoadd as it is not attached to any project."
      echo -e "Unassign $projectkey from $repoadd in $TARGET_JPD_URL"
      curl --location --request DELETE "$TARGET_JPD_URL/access/api/v1/projects/_/attach/repositories/$repoadd" --header "Authorization: Bearer $AUTH_TOKEN_JPD_2"
    else 
      echo -e "Project Key $projectkey is present in $repoadd"
      echo -e "Unassign $projectkey from $repoadd in $TARGET_JPD_URL"
      curl --location --request DELETE "$TARGET_JPD_URL/access/api/v1/projects/_/attach/repositories/$repoadd" --header "Authorization: Bearer $AUTH_TOKEN_JPD_2"
      echo -e "\nMove $repoadd to $projectkey in $TARGET_JPD_URL"
      curl --location --request PUT "$TARGET_JPD_URL/access/api/v1/projects/_/attach/repositories/$repoadd/$projectkey" --header "Authorization: Bearer $AUTH_TOKEN_JPD_2"
      echo -e "Completed $repoadd !!\n"
    fi
done < $reposfile

### sample cmd to run - ./repo_attach_project_sync.sh https://ramkannan.jfrog.io http://35.209.109.173:8082 local admin **** ****