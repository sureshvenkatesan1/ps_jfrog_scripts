#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
TARGET_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082}"
AUTH_TOKEN_JPD_1="${3:?please provide the user pwd or token or API Key . ex - password}"
AUTH_TOKEN_JPD_2="${4:?please provide access token to move project}"

### define variables
projectfile="projects_list.txt"
reposfile="repos_list.txt"

### Run the curl API 
rm -rf *.json
rm -rf *.txt

curl -XGET -H "Authorization: Bearer ${AUTH_TOKEN_JPD_1}" "${SOURCE_JPD_URL}/access/api/v1/projects" -s | jq -r '.[].project_key' > $projectfile
cat $projectfile

while IFS= read -r proj; do
    echo -e "\nGet repositories for project --> $proj from $SOURCE_JPD_URL"
    while IFS= read -r repo; do
      echo -e "Reponame name ==> $repo"
      echo -e "UnShare $repo to $proj in $TARGET_JPD_URL"
      curl --location --request DELETE "$TARGET_JPD_URL/access/api/v1/projects/_/share/repositories/$repo/$proj" --header "Authorization: Bearer $AUTH_TOKEN_JPD_2"
    done < "$reposfile"
done < $projectfile

### sample cmd to run - ./repo_unshare_project_sync.sh https://ramkannan.jfrog.io http://35.209.109.173:8082 **** ****