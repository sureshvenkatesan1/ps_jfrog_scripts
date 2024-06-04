#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 <serverid> <packageType>"
    exit 1
}

# Check if the correct number of arguments are provided
if [ $# -ne 2 ]; then
    usage
fi

# Assign input arguments to variables
SERVER_ID=$1
PACKAGE_TYPE=$2

# Invoke JFrog CLI to get repositories and parse the JSON to get the "key" values
REPO_KEYS=$(jf rt curl -s -XGET "/api/repositories?packageType=${PACKAGE_TYPE}" --server-id=${SERVER_ID} | jq -r '[.[] | .key]')

# Print the parsed "key" values in list format
echo ${REPO_KEYS}

# Exit the script
exit 0
