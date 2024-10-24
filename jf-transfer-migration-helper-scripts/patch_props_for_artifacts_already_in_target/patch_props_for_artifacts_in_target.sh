#!/bin/bash
# ./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test

# Check if at least the first four required parameters are provided
if [ $# -lt 4 ]; then
    echo "Usage: $0 <source-artifactory> <source-repo> <target-artifactory> <target-repo> [root-folder]"
    exit 1
fi

# Assign the input parameters to variables
source_artifactory="$1"
source_repo="$2"
target_artifactory="$3"
target_repo="$4"
jq_sed_command="| jq '.results[]|(.path +\"/\"+ .name+\",\"+(.sha256|tostring))'  | sed  's/\.\///'"

# Log failed, successful, and all commands to separate files
failed_commands_file="failed_commands.txt"
# successful_commands_file="successful_commands.txt"
all_commands_file="all_commands.txt"
# skipped_commands_file="skipped_commands.txt"

#####################################
# Can be deleted later.
# Function to generate props patch command
# generate_props_patch_command1() {
#    #  generate_props_patch_command  "$target_list_in_subfolders_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

#     target_list_command="$1"
#     folder_to_migrate="$2"
#     folder_position="$3"  # Pass the folder position as an argument
#     sibling_folder_count="$4"


#     eval "$target_list_command  >> a"
#     target_exit_status=$?

#     if [ $target_exit_status -ne 0 ]; then
#         echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $target_list_command"
#         echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $target_list_command" >> "$failed_commands_file"
#     fi
#     # Disable debugging when no longer needed
# #  set +x
#     if  [ $target_exit_status -eq 0 ]; then
#           cat a |  sed -re 's/,[[:alnum:]]+"$/"/g' |sed 's/"//g' > b
#         #   cat b

#            while IFS= read -r line
#             do

#                 # Does the artifact have properties
#                 get_item_properties_cmd="jf rt  curl -s -k -XGET \"/api/storage/$source_repo/$line?properties\" --server-id $source_artifactory"
#                 # echo $get_item_properties_cmd
#                 prop_output=$(eval "$get_item_properties_cmd")
#                 prop_exit_status=$?


#                 if [ $prop_exit_status -ne 0 ]; then
#                     echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $get_item_properties_cmd"
#                     echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $get_item_properties_cmd" >> "$failed_commands_file"
#                 else
#                     # echo $prop_output
#                     # Check the status code and process the JSON data
#                     http_status=$(echo "$prop_output" | jq -r '.errors[0].status')
#                     if [ "$http_status" != "404" ]; then
#                        # The artifact has properties
#                         json_data=$(echo "$prop_output" | jq -c '.properties')
#                         # Check if the JSON data is not null before further processing
#                         if [ -n "$json_data" ]; then

#                             modified_json="{\"props\": $json_data}"
#                             escaped_modified_json=$(echo "$modified_json" | sed 's/"/\\"/g')
#                             target_props_output=$(jf rt curl -k -sL -XGET "/api/storage/$target_repo/$line?properties" --server-id $target_artifactory)
#                             # echo "*********>$target_props_output"
#                             if [ -n "$target_props_output" ]; then
#                                 target_json_data=$(echo "$target_props_output" | jq -c '.properties')
#                                 if [ -n "$target_json_data" ]; then
#                                     target_modified_json="{\"props\": $target_json_data}"
#                                     target_escaped_modified_json=$(echo "$target_modified_json" | sed 's/"/\\"/g')
#                                 fi
#                             fi

#                             # echo "~~~~~~~~~~>$target_escaped_modified_json"

#                             if [ "$target_escaped_modified_json" == "$escaped_modified_json" ]; then
#                                 echo "Properties are identical, skipping patching for artifact: $line"
#                             else
#                                 # Run the PATCH request using the modified JSON data to set the properties for the artifact in the target
#                                 # ( artifact already exists in the target)

#                                 echo " jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$target_repo/$line?atomicProperties=1\" --server-id $target_artifactory -d \"$escaped_modified_json\" "$'\n'
#                             fi
#                         else
#                             echo "No properties found for artifact: $line"
#                         fi

#                    fi

#                 fi

#             done < "b"

#         rm -f a b
#     fi
# }
#####################################

####################
# Function to execute a command and log failures
execute_command() {
    local command="$1"
    local folder="$2"

    eval "$command >> a"
    local exit_status=$?

    if [ $exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder - Run Command: $command"
        echo "Error: Command failed for folder: $folder - Run Command: $command" >> "$failed_commands_file"
    fi

    return $exit_status
}

# Function to process properties for an artifact
process_artifact_properties() {
    local line="$1"
    local folder="$2"
    local artifactory_id="$3"
    local repo="$4"

    # Check if the artifact has properties
    local get_item_properties_cmd="jf rt  curl -s -k -XGET \"/api/storage/$repo/$line?properties\" --server-id $artifactory_id"
    local prop_output=$(eval "$get_item_properties_cmd")
    local prop_exit_status=$?

    if [ $prop_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder - Run Command: $get_item_properties_cmd"
        echo "Error: Command failed for folder: $folder - Run Command: $get_item_properties_cmd" >> "$failed_commands_file"
        return 1
    fi

    # Check if the artifact has properties
    local http_status=$(echo "$prop_output" | jq -r '.errors[0].status')
    if [ "$http_status" != "404" ]; then
        local json_data=$(echo "$prop_output" | jq -c '.properties')
        if [ -n "$json_data" ]; then
            echo "$json_data"
            return 0
        fi
    fi

    return 1
}

# Function to generate props patch command for an artifact
generate_patch_command() {
    local line="$1"
    local folder="$2"
    local escaped_modified_json="$3"

    local target_json_data=$(process_artifact_properties "$line" "$folder_to_migrate" "$target_artifactory" "$target_repo")


    if [ $? -eq 0 ] && [ -n "$target_json_data" ]; then
        local target_modified_json="{\"props\": $target_json_data}"
        local target_escaped_modified_json=$(echo "$target_modified_json" | sed 's/"/\\"/g')

        if [ "$target_escaped_modified_json" == "$escaped_modified_json" ]; then
            echo "Properties are identical, skipping patching for artifact: $line"
        else
            echo "jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$target_repo/$line?atomicProperties=1\" --server-id $target_artifactory -d \"$escaped_modified_json\" "
        fi
    fi


}

# Function to generate props patch command
generate_props_patch_command() {
    local target_list_command="$1"
    local folder_to_migrate="$2"
    local folder_position="$3"
    local sibling_folder_count="$4"

    execute_command "$target_list_command" "$folder_to_migrate"
    local exit_status=$?

    if [ $exit_status -eq 0 ]; then
        cat a | sed -re 's/,[[:alnum:]]+"$/"/g' | sed 's/"//g' > b

        while IFS= read -r line; do
            local json_data=$(process_artifact_properties "$line" "$folder_to_migrate" "$source_artifactory" "$source_repo")
            if [ $? -eq 0 ] && [ -n "$json_data" ]; then
                local modified_json="{\"props\": $json_data}"
                local escaped_modified_json=$(echo "$modified_json" | sed 's/"/\\"/g')
                generate_patch_command "$line" "$folder_to_migrate" "$escaped_modified_json"
            else
                echo "No properties found for artifact: $line"
            fi
        done < "b"

        rm -f a b
    fi
}
######################
# Check if the fifth parameter (root-folder) is provided
if [ $# -ge 5 ]; then
    root_folder="$5"



    target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$root_folder\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands
    target_list_in_dot_folder_command="$target_command1 $jq_sed_command"


    #Call the migrate command without the trailing * in $folder_to_migrate
    generate_props_patch_command "$target_list_in_dot_folder_command"  "$root_folder" "0" "0"
else
    root_folder=""
    # check for files in the root folder:

    target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \".\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands
    target_list_in_dot_folder_command="$target_command1 $jq_sed_command"

    #Call the migrate command without the trailing * in $folder_to_migrate
    generate_props_patch_command  "$target_list_in_dot_folder_command" "." "0" "0"

fi

# Run the jf rt curl command and capture the output into a variable
if [ -z "$root_folder" ]; then
    output=$(jf rt curl -s -k -XGET "/api/storage/$target_repo?list&deep=1&depth=1&listFolders=1" --server-id $target_artifactory)
else
    output=$(jf rt curl -s -k -XGET "/api/storage/$target_repo/$root_folder?list&deep=1&depth=1&listFolders=1" --server-id $target_artifactory)
fi

# Parse the JSON output using jq and get the "uri" values for folders
folders=$(echo "$output" | jq -r '.files[] | select(.folder) | .uri')

# Split folders into an array
IFS=$'\n' read -rd '' -a folders_array <<< "$folders"

# Calculate the total number of folders
total_folders="$(expr "${#folders_array[@]}" + 1)"




    # Loop through the folders and generate the jf rt  commands
    for folder_position in "${!folders_array[@]}"; do
        folder="${folders_array[$folder_position]}"
        #Remove the leading slash i.e if folder is "/abc" it becomes "abc"
        folder="${folder#/}"

        # Now check if the folder_name starts with a dot like ".conan" , ".npm" or if it's "_uploads" skip it
        #  as it will be generated
        if [[ "$folder" == .* ]] || [ "$folder" = "_uploads" ]; then
            echo "============excluding=====>${folder}"
            continue  # Skip this iteration of the loop
        fi

        src_list_command=""
        target_list_command=""


        if [ -z "$root_folder" ]; then
        folder_to_migrate="$folder"
        else
            folder_to_migrate="$root_folder/$folder"
        fi


        target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

            # Concatenate the two commands
        target_list_in_this_folder_command="$target_command1 $jq_sed_command"


    #    echo $target_list_command

        #Call the migrate command without the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        generate_props_patch_command  "$target_list_in_this_folder_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

    # Now check in the subfolders:



        target_command2="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate/*\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands

        target_list_in_subfolders_command="$target_command2 $jq_sed_command"
        # echo $target_list_in_subfolders_command

    #Call the migrate command with the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        generate_props_patch_command  "$target_list_in_subfolders_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

        # Limit to 5 parallel commands
        # if [[ $(jobs | wc -l) -ge 5 ]]; then
        #     wait -n
        # fi
    done #| parallel -j 8
