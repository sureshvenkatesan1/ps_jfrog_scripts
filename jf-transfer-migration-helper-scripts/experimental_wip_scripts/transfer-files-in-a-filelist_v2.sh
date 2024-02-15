#! /bin/bash

#Get Arguments
SOURCE_ID="${1:?Enter source artifactory server ID}"
TARGET_ID="${2:?Enter target artifactory server ID}"
REPO_NAME="${3:?Enter the repo name you wish to transfer}"
TRANSFERONLY="${4:?Transfer or View, valid options 'yes' or 'no'}"
case "$TRANSFERONLY" in
    yes)
        ;;
    no)
        ;;
    *)
        echo "Wrong 3rd Parameter, 3rd parameter value should be yes or no"
        exit 1
        ;;
esac
sed 's/^\///' filepaths_nometadatafiles.txt > filepaths_nometadatafiles-no-slash.txt

#jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $SOURCE_ID --data "items.find({\"repo\": \"$1\"}).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | sed  's/\.\///' > a
#jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $TARGET_ID --data "items.find({\"repo\": \"$1\"}).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | sed  's/\.\///' > b
#join -v1  <(sort a) <(sort b) | sed -re 's/,[[:alnum:]]+"$/"/g' |sed 's/"//g' > c
#cat c | xargs -I {} echo "jf rt dl \"$1/{}\" . --server-id local ; jf rt u \"{}\" \"$1/{}\" --server-id local1 ; rm -f \"{}\" "
if [ "${TRANSFERONLY}" == "no" ]; then
        echo "-------------------------------------------------"
        echo "Files diff from source - Repo [$1]"
        echo "-------------------------------------------------"
        cat -b c
elif [ "${TRANSFERONLY}" == "yes" ]; then
while IFS= read -r line
do
 echo "jf rt dl \"$REPO_NAME/$line\" . --server-id $SOURCE_ID ; jf rt u \"$line\" \"$REPO_NAME/$line\" --server-id $TARGET_ID ; rm -rf \"$REPO_NAME/$line\" "
 #jf rt dl \"$1/$line\" . --server-id $SOURCE_ID ; jf rt u \"$line\" \"$1/$line\" --server-id $TARGET_ID ; rm -f \"$line\"
done < "filepaths_nometadatafiles-no-slash.txt"
else
  echo "Wrong 3rd Parameter, 3rd parameter value should be yes or no"
fi


#===========

while IFS= read -r line
do

    # Does the artifact have properties
    get_item_properties_cmd="jf rt  curl -s -k -XGET \"/api/storage/$source_repo/$line?properties\" --server-id $source_artifactory"
    # echo $get_item_properties_cmd
    prop_output=$(eval "$get_item_properties_cmd")
    prop_exit_status=$?
    # echo $prop_output

    if [ $prop_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $get_item_properties_cmd"
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $get_item_properties_cmd" >> "$failed_commands_file"
    else
        # Check the status code and process the JSON data
        echo "In run_migrate_command - 5 - b4 calling jq"
        http_status=$(echo "$prop_output" | jq -r '.errors[0].status')
        echo "In run_migrate_command - 6 - after calling jq"
        # placeholder for artifact properties
        escaped_modified_json=""
        if [ "$http_status" != "404" ]; then
            echo "In run_migrate_command - 7 - b4 calling jq"
            # The artifact has properties
            json_data=$(echo "$prop_output" | jq -c '.properties')
            echo "In run_migrate_command - 8 - b4 calling jq"
            # Construct the modified JSON data dynamically
            #  escaped_modified_json=$(echo "$modified_json" | sed 's/"/\\"/g')
            escaped_modified_json="{\"props\": $json_data}"
            # Run the PATCH request using the modified JSON data to set the properties for the artifact after upload

        fi
        # Execute the migration commands for a single file in the background
        execute_artifact_migration "workdir" "$source_repo" "$line" "$source_artifactory" \
        "$target_repo" "$target_artifactory" "$escaped_modified_json" &

        # Limit the number of concurrent background execute_artifact_migration jobs
        job_count=$(jobs -p | wc -l)
        if [ "$job_count" -ge "$parallel_count" ]; then
            wait
        fi

# Function to execute the migration commands for a single file
execute_artifact_migration() {
    local workdir = "$1"
    local source_repo="$2"
    local line="$3"
    local source_artifactory="$4"
    local target_repo="$5"
    local target_artifactory="$6"
    local escaped_modified_json="$7"
    # Save the current directory to a variable
    local current_dir="$(pwd)"

    mkdir -p "$1"

    # Check if the length of the trimmed $escaped_modified_json is greater than 1 , i.e artifact has a property
    if [ ${#escaped_modified_json} -gt 1 ]; then
        cd "$1" && \
        # Execute the commands for a single artifact
        jf rt dl "$source_repo/$line" . --threads=8 --server-id "$source_artifactory" && \
        jf rt u "$line" "$target_repo/$line" --threads=8 --server-id "$target_artifactory" && \
        jf rt curl -k -sL -XPATCH -H "Content-Type: application/json" "/api/metadata/$target_repo/$line?atomicProperties=1" \
         --server-id "$target_artifactory" -d "$escaped_modified_json" && \
        #echo "In $(pwd). Now removing $line ----------------->" && \
        rm -rf "$line" && \
        cd "$current_dir" # Return to the saved directory i.e "$OLDPWD"
        if [ $? -ne 0 ]; then
            echo "At least one command failed for: $source_repo/$line" >> "$current_dir/$failed_commands_file"
        else
            echo "All commands succeeded for: $source_repo/$line" >> "$current_dir/$successful_commands_file"
        fi
    else
        # Execute the commands for a single artifact
        cd "$1" && \
        jf rt dl "$source_repo/$line" . --threads=8 --server-id "$source_artifactory" && \
        jf rt u "$line" "$target_repo/$line" --threads=8 --server-id "$target_artifactory" && \
        #echo "In $(pwd). Now removing $line ----------------->" && \
        rm -rf "$line" && \
        cd "$current_dir" # Return to the saved directory i.e "$OLDPWD"
        if [ $? -ne 0 ]; then
            echo "At least one command failed for: $source_repo/$line" >> "$current_dir/$failed_commands_file"
        else
            echo "All commands succeeded for: $source_repo/$line" >> "$current_dir/$successful_commands_file"
        fi
    fi

}
