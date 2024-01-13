#!/bin/bash

# Check if at least the first four required parameters are provided
if [ $# -lt 4 ]; then
    echo "Usage: $0 <source-artifactory> <source-repo> <target-repo> <target-artifactory> <transfer yes/no> [root-folder]"
    exit 1
fi

# Assign the input parameters to variables
source_artifactory="$1"
source_repo="$2"
target_artifactory="$3"
target_repo="$4"
TRANSFERONLY="$5"
jq_sed_command="| jq '.results[]|(.path +\"/\"+ .name+\",\"+(.sha256|tostring))'  | sed  's/\.\///'"


# Log failed, successful, and all commands to separate files
failed_commands_file="failed_commands.txt"
# successful_commands_file="successful_commands.txt"
all_commands_file="all_commands.txt"
# skipped_commands_file="skipped_commands.txt"



run_migrate_command() {
   
    src_list_command="$1" 
    target_list_command="$2"
    folder_to_migrate="$3"
    folder_position="$4"  # Pass the folder position as an argument
    sibling_folder_count="$5"
    # Check if the folder has already been successfully copied

    # if grep -q "$folder_to_migrate" "$successful_commands_file"; then
    #     # Note: we just echo it. No need to log it to  "$all_commands_file"
    #     echo "Skipping folder: $folder_to_migrate (already copied)" >> "$skipped_commands_file"
    #     return
    # fi

    # Log what is currently running only if we did not log it earlier.
    # If you stopped the script, no need to log it again , we can always check waht is running using 
    # ps -ef | grep "jf rt cp"
    # if ! grep -q "$folder_to_copy" "$all_commands_file"; then
        echo "Running command: $src_list_command [Progress: $folder_position out of $sibling_folder_count sub folders]" >> "$all_commands_file"
    # fi
    

    # Run the command
    # echo $src_list_command
    # Enable debugging
    #  set -x
    eval "$src_list_command >> a" 
    src_exit_status=$?

    if [ $src_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $src_list_command"
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $src_list_command" >> "$failed_commands_file"
    fi

    eval "$target_list_command  >> b"
    target_exit_status=$?
   
    if [ $target_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $target_list_command"
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $target_list_command" >> "$failed_commands_file"
    fi
    # Disable debugging when no longer needed
    #  set +x
    if [ $src_exit_status -eq 0 ] && [ $target_exit_status -eq 0 ]; then

        join -v1  <(sort a) <(sort b) | sed -re 's/,[[:alnum:]]+"$/"/g' |sed 's/"//g' > c
        
        if [ "${TRANSFERONLY}" = "no" ]; then
            echo "-------------------------------------------------"
            echo "Files diff from source $source_artifactory - Repo [$source_repo]/$folder_to_migrate -  [Progress: $folder_position out of $sibling_folder_count folders]"
            echo "-------------------------------------------------"
            cat -b c
        elif [ "${TRANSFERONLY}" = "yes" ]; then
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
                    http_status=$(echo "$prop_output" | jq -r '.errors[0].status')
                    if [ "$http_status" != "404" ]; then
                       # The artifact has properties
                        json_data=$(echo "$prop_output" | jq -c '.properties')
                        #escaped_json_data=$(echo "$json_data" | sed 's/"/\\"/g')
                        # Construct the modified JSON data dynamically
                        #modified_json="{\\"props\\": $escaped_json_data}"
                         modified_json="{\"props\": $json_data}"
                         escaped_modified_json=$(echo "$modified_json" | sed 's/"/\\"/g')
                        # Run the PATCH request using the modified JSON data to set the properties for the artifact after upload
                        #echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; rm -rf \"$line\" "$'\n'
                        # Cannot apply the XPATCH  to  /api/metadata as indexing takes time. See https://jfrog-int.atlassian.net/browse/RTDEV-34900 . 

                        # echo "jf rt curl -k -sL -XPATCH -H 'Content-Type: application/json' '/api/metadata/$target_repo/$line?atomicProperties=1' --server-id $target_artifactory -d '$modified_json'"$'\n' >> properties_patch.txt

                        # echo "jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$target_repo/$line?atomicProperties=1\" --server-id $target_artifactory -d \"$escaped_modified_json\""$'\n' >> properties_patch.txt
                        # So run the commands in properties_patch.txt in the end after all the artifacts are uploaded to target.

                        echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$target_repo/$line?atomicProperties=1\" --server-id $target_artifactory -d \"$escaped_modified_json\"; rm -rf \"$line\" "$'\n' 
                        #eval "jf rt curl -k -sL -XPATCH -H 'Content-Type: application/json' '/api/metadata/$target_repo/$line?atomicProperties=1' --server-id $target_artifactory -d '$modified_json'"

                    else
                       # The artifact does not have properties
                        echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; rm -rf \"$line\" "$'\n'
                    fi

                fi

            done < "c"
        else 
            echo "Wrong 5th Parameter, 5th parameter value should be yes or no"
        fi 
        
        rm -f a b c
    fi
}



# Check if the fifth parameter (root-folder) is provided
if [ $# -ge 6 ]; then
    root_folder="$6"
    # check for files in the root folder:
    src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$root_folder\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
    

    target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$root_folder\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands 
    src_list_in_dot_folder_command="$src_command1 $jq_sed_command"
    target_list_in_dot_folder_command="$target_command1 $jq_sed_command"

    #Call the migrate command without the trailing * in $folder_to_migrate
    run_migrate_command "$src_list_in_dot_folder_command" "$target_list_in_dot_folder_command" "$root_folder" "0" "0"
else
    root_folder=""
    # check for files in the root folder:
    src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \".\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
    

    target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \".\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands 
    src_list_in_dot_folder_command="$src_command1 $jq_sed_command"
    target_list_in_dot_folder_command="$target_command1 $jq_sed_command"

    #Call the migrate command without the trailing * in $folder_to_migrate
    run_migrate_command "$src_list_in_dot_folder_command" "$target_list_in_dot_folder_command" "." "0" "0"

fi

# Run the jf rt curl command and capture the output into a variable
if [ -z "$root_folder" ]; then
    output=$(jf rt curl -s -k -XGET "/api/storage/$source_repo?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
else
    output=$(jf rt curl -s -k -XGET "/api/storage/$source_repo/$root_folder?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
fi

# Parse the JSON output using jq and get the "uri" values for folders
folders=$(echo "$output" | jq -r '.files[] | select(.folder) | .uri')

# Split folders into an array
IFS=$'\n' read -rd '' -a folders_array <<< "$folders"

# Calculate the total number of folders
total_folders="$(expr "${#folders_array[@]}" + 1)"



if [ "${TRANSFERONLY}" = "yes" ]; then

    # Loop through the folders and generate the jf rt  commands
    for folder_position in "${!folders_array[@]}"; do
        folder="${folders_array[$folder_position]}"
        #Remove the leading slash i.e if folder is "/abc" it becomes "abc"
        folder="${folder#/}"
        # Check if the folder name is ".conan" and skip it as it will be generated
        if [ "$folder" = ".conan" ]; then
            continue  # Skip this iteration of the loop
        fi


        src_list_command=""
        target_list_command=""


        if [ -z "$root_folder" ]; then
        folder_to_migrate="$folder"
        else
            folder_to_migrate="$root_folder/$folder"
        fi

        src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
        

        target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

            # Concatenate the two commands 
        src_list_in_this_folder_command="$src_command1 $jq_sed_command"
        target_list_in_this_folder_command="$target_command1 $jq_sed_command"
        
    #     echo $src_list_command
    #    echo $target_list_command

        #Call the migrate command without the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        run_migrate_command "$src_list_in_this_folder_command" "$target_list_in_this_folder_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

    # Now check in the subfolders:

        src_command2="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate/*\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
        

        target_command2="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate/*\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands 
        src_list_in_subfolders_command="$src_command2 $jq_sed_command"
        target_list_in_subfolders_command="$target_command2 $jq_sed_command"

    #Call the migrate command with the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        run_migrate_command "$src_list_in_subfolders_command" "$target_list_in_subfolders_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

        # Limit to 5 parallel commands
        # if [[ $(jobs | wc -l) -ge 5 ]]; then
        #     wait -n
        # fi
    done #| parallel -j 8
else
   # Loop through the folders and generate the jf rt cp commands
    for folder_position in "${!folders_array[@]}"; do
        folder="${folders_array[$folder_position]}"
        #Remove the leading slash i.e if folder is "/abc" it becomes "abc"
        folder="${folder#/}"
        # Check if the folder name is ".conan" and skip it as it will be generated
        if [ "$folder" = ".conan" ]; then
            continue  # Skip this iteration of the loop
        fi


        src_list_command=""
        target_list_command=""


        if [ -z "$root_folder" ]; then
        folder_to_migrate="$folder"
        else
            folder_to_migrate="$root_folder/$folder"
        fi

        src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
        

        target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

            # Concatenate the two commands 
        src_list_in_this_folder_command="$src_command1 $jq_sed_command"
        target_list_in_this_folder_command="$target_command1 $jq_sed_command"
        
    #     echo $src_list_command
    #    echo $target_list_command

        #Call the migrate command without the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        run_migrate_command "$src_list_in_this_folder_command" "$target_list_in_this_folder_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"

    # Now check in the subfolders:

        src_command2="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate/*\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"
        

        target_command2="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
        --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate/*\"},\
            \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"

        # Concatenate the two commands 
        src_list_in_subfolders_command="$src_command2 $jq_sed_command"
        target_list_in_subfolders_command="$target_command2 $jq_sed_command"

    #Call the migrate command with the trailing * in $folder_to_migrate
        #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
        run_migrate_command "$src_list_in_subfolders_command" "$target_list_in_subfolders_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"
    done
fi

# Loop through the folders and delete the folders
for folder_position in "${!folders_array[@]}"; do
    folder="${folders_array[$folder_position]}"
    #Remove the leading slash i.e if folder is "/abc" it becomes "abc"
    folder="${folder#/}"
    # Check if the folder name is ".conan" and skip it as it will be generated
    if [ "$folder" = ".conan" ]; then
        continue  # Skip this iteration of the loop
    fi

    if [ -z "$root_folder" ]; then
    folder_to_migrate="$folder"
    else
        folder_to_migrate="$root_folder/$folder"
    fi

    # Check if the folder exists
    if [ -d "$folder_to_migrate" ]; then
        # Check if the folder is empty
        if [ -z "$(find "$folder_to_migrate" -type f 2>/dev/null)" ]; then
            echo "Folder '$folder_to_migrate' is empty, removing..."
            rm -rf "$folder_to_migrate"
        else
            echo "Folder '$folder_to_migrate' is not empty."
            # Add additional actions for non-empty folders here if needed
        fi
    fi

done

if [ -d "$root_folder" ]; then
    # Check if the folder is empty
    if [ -z "$(find "$root_folder" -type f 2>/dev/null)" ]; then
        echo "Folder '$root_folder' is empty, removing..."
        rm -rf "$root_folder"
    else
        echo "Folder '$root_folder' is not empty."
        # Add additional actions for non-empty folders here if needed
    fi
fi

# echo "Next PATCH the properties using patch_properties.sh "

