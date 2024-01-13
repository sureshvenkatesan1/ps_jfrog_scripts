#!/bin/bash
##########
# Usage: bash ./create_cached_locals_for_all_remotes.sh your-target-RT_server_id template.json [--dry-run]
##########

if [ $# -lt 2 ]; then
    echo "Usage: $0 <target> <template_file> [--dry-run]"
    exit 1
fi

target="$1"
template_file="$2"
dry_run=0

if [ "$3" = "--dry-run" ]; then
    dry_run=1
fi

response=$(jf rt curl "/api/repositories?type=remote" --server-id="$target")

keys=$(echo "$response" | jq -r '.[].key')
packageTypes=$(echo "$response" | jq -r '.[].packageType')

# Split keys and packageTypes into arrays
IFS=$'\n' read -rd '' -a keys_array <<< "$keys"
IFS=$'\n' read -rd '' -a packageTypes_array <<< "$packageTypes"

for ((index=0; index<${#keys_array[@]}; index++)); do
    key="${keys_array[$index]}"
    packageType="${packageTypes_array[$index]}"
    packageType_lower=$(echo "$packageType" | tr '[:upper:]' '[:lower:]')
    repo_name="cached-$key"

    echo "jf rt repo-create \"$template_file\" --vars \"repo-name=$repo_name;package-type=$packageType_lower\" --server-id=\"$target\""

    if [ "$dry_run" -eq 0 ]; then
        jf rt repo-create "$template_file" --vars "repo-name=$repo_name;package-type=$packageType_lower" --server-id="$target"
    fi
done

