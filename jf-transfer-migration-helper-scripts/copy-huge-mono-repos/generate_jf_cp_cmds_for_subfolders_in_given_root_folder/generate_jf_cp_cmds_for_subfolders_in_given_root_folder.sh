#!/bin/bash

# Check if at least the first four required parameters are provided
if [ $# -lt 4 ]; then
    echo "Usage: $0 <source-artifactory> <source-repo> <target-repo> <target-artifactory> [root-folder]"
    exit 1
fi

# Assign the input parameters to variables
source_artifactory="$1"
source_repo="$2"

target_artifactory="$3"
target_repo="$4"


# Check if the fifth parameter (root-folder) is provided
if [ $# -ge 5 ]; then
    root_folder="$5"
else
    root_folder=""
fi

# Run the jf rt curl command and capture the output into a variable
if [ -z "$root_folder" ]; then
    #echo jf rt curl  -k -XGET "/api/storage/$source_repo?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory
    output=$(jf rt curl  -k -XGET "/api/storage/$source_repo?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
else
    #echo jf rt curl  -k -XGET "/api/storage/$source_repo/$root_folder?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory
    output=$(jf rt curl  -k -XGET "/api/storage/$source_repo/$root_folder?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
fi

# Parse the JSON output using jq and get the "uri" values for folders
folders=$(echo "$output" | jq -r '.files[] | select(.folder) | .uri')

# Split folders into an array
IFS=$'\n' read -rd '' -a folders_array <<< "$folders"

# Loop through the folders and generate the jf rt cp commands
for folder in "${folders_array[@]}"; do

    # Check if the folder name is ".conan" and skip it
    if [ "$folder" = "/.conan" ]; then
        continue  # Skip this iteration of the loop
    fi

    #echo "jf rt cp $source_repo$folder/ $target_repo/ --flat=false --threads=8 --dry-run=false --server-id $target_artifactory"
    if [ -z "$root_folder" ]; then
        cp_command="jf rt cp $source_repo$folder/ $target_repo/ --flat=false --threads=8 --dry-run=false --server-id $target_artifactory"
    else
        cp_command="jf rt cp $source_repo/$root_folder$folder/ $target_repo/ --flat=false --threads=8 --dry-run=false --server-id $target_artifactory"
    fi
    echo $cp_command
done
