#!/bin/bash
##########
# Usage: bash ./copy_to_cached_locals_for_all_remotes.sh your-target-RT_server_id --dry-run
##########

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_artifactory>  [--dry-run]"
    exit 1
fi

target="$1"
dry_run=0

if [ "$2" = "--dry-run" ]; then
    dry_run=1
fi

export JFROG_CLI_LOG_LEVEL=DEBUG

response=$(jf rt curl "/api/repositories?type=remote" --server-id="$target")

keys=$(echo "$response" | jq -r '.[].key')

# Split keys and packageTypes into arrays
IFS=$'\n' read -rd '' -a keys_array <<< "$keys"

for ((index=0; index<${#keys_array[@]}; index++)); do
    key="${keys_array[$index]}"
    local_repo_name="cached-$key"

    echo "jf rt curl -XPOST \"/api/copy/$key-cache?to=$local_repo_name\"  --server-id=\"$target\""

    if [ "$dry_run" -eq 0 ]; then
        jf rt curl -XPOST "/api/copy/$key-cache?to=$local_repo_name" --server-id="$target"
    fi
done

