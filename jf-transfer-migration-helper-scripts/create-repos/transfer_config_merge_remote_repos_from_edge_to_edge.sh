#!/bin/bash

# Parameters
source_server="$1"
target_server="$2"
includerepos="$3"
excluderepos="$4"
username="$5"
remoteurl_cname="$6"
REPO_PASSWORD="${REPO_PASSWORD}"

# Convert the semicolon-separated lists to arrays
IFS=";" read -r -a include_array <<< "$includerepos"
IFS=";" read -r -a exclude_array <<< "$excluderepos"

mkdir -p repository
cd repository

rm -rf *config.json
rm -rf conflicting-repos.txt

# Get all remote repos from the source Artifactory
remote_repos=$(jf rt curl -X GET api/repositories?type=remote --server-id="$source_server" | jq -r '.[].key')

# Helper function to check if repo is in the exclude list
is_in_exclude_list() {
    local repo="$1"
    for item in "${exclude_array[@]}"; do
        if [[ "$repo" == "$item" ]]; then
            return 0
        fi
    done
    return 1
}

# Helper function to check if repo is in the include list
is_in_include_list() {
    local repo="$1"
    for item in "${include_array[@]}"; do
        if [[ "$repo" == "$item" ]]; then
            return 0
        fi
    done
    return 1
}

# Loop through all remote repos
for repo in $remote_repos; do
    # Check if exclude list is non-empty and if the repo is in the exclude list
    if [[ -n "$excluderepos" ]]; then
        if is_in_exclude_list "$repo"; then
            echo "Skipping excluded repo: $repo"
            continue
        fi
    fi

    # Check if include list is non-empty and if the repo is not in the include list
    if [[ -n "$includerepos" ]]; then
        if ! is_in_include_list "$repo"; then
            echo "Skipping repo not in include list: $repo"
            continue
        fi
    fi

    # Export the repo config
    jf rt curl -X GET api/repositories/"$repo" --server-id="$source_server" -o "$repo-config.json"

    # Modify the repo config JSON

    jq --arg username "$username" --arg password "$REPO_PASSWORD" --arg remoteurl_cname "$remoteurl_cname" \
    'if .rclass == "remote" and .url != null then
        # First, capture the scheme (http or https) from the URL
        .scheme = (.url | match("^(https?://)").string) 
        # Second, replace the URL with the new domain but keep the scheme intact
        | .url = (.scheme + $remoteurl_cname + (.url | sub("^(https?://)[^/]+"; "")))
        | .username = $username
        | .password = $password
    else . end' "$repo-config.json" > temp.json
    mv temp.json "$repo-config.json"

    # Push the modified config to the target Artifactory
    data=$(jf rt curl -X PUT api/repositories/"$repo" -H "Content-Type: application/json" \
        -T "$repo-config.json" --server-id="$target_server" -s | grep message | xargs)

    echo $data
    if [[ $data == *"message"* ]]; then
        echo "$repo" >> conflicting-repos.txt
    fi
done

echo "Script execution completed."
