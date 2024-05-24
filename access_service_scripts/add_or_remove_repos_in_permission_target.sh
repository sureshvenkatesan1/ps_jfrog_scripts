#!/bin/bash

# Enable debugging
trap 'echo "Executing: $BASH_COMMAND"' DEBUG

# Usage: ./add_or_remove_repos_in_permission_target.sh <serverid> <permission-target-name> <add|remove> <repo1> [<repo2> ...]

# Check if at least four arguments are passed (serverid, permission target name, operation, and at least one repository)
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <serverid> <permission-target-name> <add|remove> <repo1> [<repo2> ...]"
    exit 1
fi

# Set variables
SERVERID=$1
PERMISSION_TARGET_NAME=$2
OPERATION=$3
shift 3
REPOS=("$@")

echo "Fetching the current configuration of the permission target: ${PERMISSION_TARGET_NAME}"

# Fetch the current configuration of the permission target
CURRENT_PAYLOAD=$(jf rt curl -XGET "api/v2/security/permissions/${PERMISSION_TARGET_NAME}" --server-id=${SERVERID})
echo "Current Payload:"
echo "$CURRENT_PAYLOAD"

# Extract existing repositories
EXISTING_REPOS=$(echo "$CURRENT_PAYLOAD" | jq -r '.repo.repositories | join(" ")')

# Combine existing and new repositories based on the operation
if [ "$OPERATION" == "add" ]; then
    ALL_REPOS=(${EXISTING_REPOS} ${REPOS[@]})
    UNIQUE_REPOS=($(echo "${ALL_REPOS[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
elif [ "$OPERATION" == "remove" ]; then
    ALL_REPOS=(${EXISTING_REPOS})
    for repo in "${REPOS[@]}"; do
        ALL_REPOS=(${ALL_REPOS[@]//*$repo*})
    done
    UNIQUE_REPOS=($(echo "${ALL_REPOS[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
else
    echo "Invalid operation. Use 'add' or 'remove'."
    exit 1
fi

# Create the updated payload
UPDATED_PAYLOAD=$(jq -n --argjson repos "$(echo ${UNIQUE_REPOS[@]} | jq -R 'split(" ")')" \
                  '{ "repo": { "repositories": $repos }}')

echo "Updated Payload:"
echo "$UPDATED_PAYLOAD"

# Update the permission target with the new payload
jf rt curl -XPUT "api/v2/security/permissions/${PERMISSION_TARGET_NAME}" -H "Content-Type: application/json" \
    -d "${UPDATED_PAYLOAD}" --server-id=${SERVERID}

echo "Permission target '${PERMISSION_TARGET_NAME}' updated successfully."
