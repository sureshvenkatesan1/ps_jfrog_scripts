#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
JPD_AUTH_TOKEN="${2:?please provide the user pwd or token or API Key . ex - password}"
ACTION="${3:?Mention Share or Unshare Repos with ALL Projects . ex - password}"

### define variables
reposfile="repos_list.txt"

### Run the curl API 
rm -rf *.json
rm -rf *.txt

while IFS= read -r repoadd; do
    if [[ $ACTION == "share" ]]; then
        echo -e "SHARE repository - $repoadd with ALL Projects"
        curl --location --request PUT "$JPD_URL/access/api/v1/projects/_/share/repositories/$repoadd" --header "Authorization: Bearer $JPD_AUTH_TOKEN"
    elif [[ $ACTION == "unshare" ]]; then
        echo -e "UNSHARE repository - $repoadd with ALL Projects"
        curl --location --request DELETE "$JPD_URL/access/api/v1/projects/_/share/repositories/$repoadd" --header "Authorization: Bearer $JPD_AUTH_TOKEN"
    else
        echo "Invalid Action. Mention Only share / unshare"
    fi
        
done < $reposfile

### sample cmd to run - ./repo_share_or_unshare_all_projects.sh https://ramkannan.jfrog.io **** share/unshare