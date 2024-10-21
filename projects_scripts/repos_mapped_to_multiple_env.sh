#!/bin/bash
#
# bash ./repos_mapped_to_multiple_env.sh mill remote DEV
#
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <server_id> <repo_type> <ENV DEV/PROD>"
    exit 1
fi

server_id="$1"
repo_type="$2"
env="$3"

# Function to URL-encode a string
url_encode() {
    local string="$1"
    printf "%s" "$string" | jq -s -R -r @uri
}

# Usage example
server_id_encoded=$(url_encode "$server_id")


# Step 1: Get the list of repositories
repositories=$(jf rt curl -k -sL "/api/repositories?type=${repo_type}" --server-id="${server_id_encoded}" | jq -r '.[]|.key')

# Step 2: Loop through the repositories and invoke the API
for repo_name in $repositories; do
    repo_name_encoded=$(url_encode "$repo_name")

    api_url="/api/repositories/${repo_name_encoded}"

    echo "Executing curl command: curl ${api_url}"

    repo_config_json=$(jf rt curl -k -sL "${api_url}" --server-id="${server_id_encoded}")
    repo_config=$(echo "$repo_config_json" | jq -c '.')

    # Step 3: Check for multiple values in "environments" list
    environments=$(echo "$repo_config_json" | jq -r '.environments | length')
    if [ -n "$environments" ] && [ "$environments" -gt 1 ]; then
      # Step 4: Print repository name and "environments" list
      echo "Repository with multiple environments: ${repo_name}"
      echo "Environments: $(echo "$repo_config_json" | jq -r '.environments')"
      echo "Update the Repository Env to DEV"

        jf rt curl -k -sL -X POST "/api/repositories/${repo_name}" \
        -H "Content-Type: application/json" \
        -d "{\"environments\":[\"${env}\"]}" --server-id="${server_id_encoded}"

    fi


done




