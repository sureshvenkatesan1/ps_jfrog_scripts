# DISCLAIMER:
# Your use of this code is governed by the following license:JFrog hereby grants you a non-
# exclusive, non-transferable, non-distributable right to use this code solely in connection with
# your use of a JFrog product or service. This code is provided 'as-is' and without any warranties or
# conditions, either express or implied including, without limitation, any warranties or conditions
# of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall
# convey to you any right or title in the code, other than for the limited use right set forth
# herein. For the purposes hereof "you" shall mean you as an individual as well as the organization
# on behalf of which you are using the software and the JFrog product or service.


#!/bin/bash

# Enable exit on error and set debug trap
#set -e
trap 'echo "Executing: $BASH_COMMAND"' DEBUG

# ./migrate_n_subfolders_in_parallel.sh usvartifactory5 liquid jfrogio liquid  no
# Check if at least the first 5 required parameters are provided
if [ $# -lt 5 ]; then
    echo "Usage: $0 <source-artifactory> <source-repo> <target-artifactory> <target-repo> <transfer yes/no> \
    [root-folder] [target_repo_root_folder] [migrateFolderRecursively yes/no] [semicolon separated exclude_folders] \
    [parallel background jobs count]"
    exit 1
fi

# Create an "output" folder and run the script inside it
mkdir -p output
cd output

# Assign the input parameters to variables
source_artifactory="$1"
source_repo="$2"
target_artifactory="$3"
target_repo="$4"
TRANSFERONLY="$5"
migratefiles_and_subfolders_recursive="yes"

# Check if the sixth parameter (root-folder) is provided
if [ $# -ge 6 ] && [ -n "${6}" ]; then
    root_folder="$6"
else
    root_folder="."
fi

# Check if the 7th parameter (target-repo-root-folder) is provided
if [ $# -ge 7 ] && [ -n "${7}" ]; then
    target_repo_root_folder="${7}"
else
    target_repo_root_folder=""
fi


# Check if the 8th argument is provided and not empty
if [ $# -ge 8 ] && [ -n "${8}" ]; then
    # Check if the 8th argument is either "yes" or "no"
    if [ "${8}" = "yes" ] || [ "${8}" = "no" ]; then
        migratefiles_and_subfolders_recursive="${8}"
    else
        echo "Error: The 8th argument must be 'yes' or 'no'. Using default value 'yes'."
    fi
fi

# EXCLUDE_FOLDERS excludes the ".conan" folder as it is  a generated one when a conan repo is indexed during
# artifact upload to that repo
if [ $# -ge 9 ] && [ -n "${9}" ]; then
    EXCLUDE_FOLDERS=";.conan;.npm;${9};"
else
    EXCLUDE_FOLDERS=";.conan;.npm;"
fi

# jq_sed_command="jq '.results[]|(.path +\"/\"+ .name+\",\"+(.sha256|tostring))'  | sed  's/\.\///'"

# Counter to limit parallel  execution i.e max number of concurrent background execute_artifact_migration jobs
if [ $# -ge 10 ] && [[ "${10}" =~ ^[0-9]+$ ]]; then
    parallel_count="${10}"
    echo "parallel_count has been set to: $parallel_count"
else
    echo "Error: The 10th argument (parallel_count) must be an integer. Using default value 16."
    parallel_count=16
fi



# Log failed, successful, and all commands to separate files
failed_commands_file="failed_commands.txt"
successful_commands_file="successful_commands.txt"
all_commands_file="all_commands.txt"


# Function to execute the migration commands for a single file
execute_artifact_migration() {
    local folder_position="$1"
    local source_repo="$2"
    local line="$3"
    local source_artifactory="$4"
    local target_repo="$5"
    local target_artifactory="$6"
    local escaped_modified_json="$7"
    # Save the current directory to a variable
    local current_dir="$(pwd)"

    # Reapply the DEBUG trap within the function
    trap 'echo "Executing: $BASH_COMMAND"' DEBUG

    if [ -n "$target_repo_root_folder" ]; then
        target_path="$target_repo/$target_repo_root_folder/$line"
    else
        target_path="$target_repo/$line"
    fi

    # Check if the length of the trimmed $escaped_modified_json is greater than 1 , i.e artifact has a property
    if [ ${#escaped_modified_json} -gt 1 ]; then
        # Execute the commands for a single artifact
        encoded_target_path=$(urlencode_spaces "$target_path")
        cd "$folder_position" && \
        echo "Executing: jf rt dl \"$source_repo/$line\" . --threads=8 --server-id \"$source_artifactory\"" | tee -a "$all_commands_file" && \
        jf rt dl "$source_repo/$line" . --threads=8 --server-id "$source_artifactory" && \
        echo "Executing: jf rt u \"$line\" \"$target_path\" --threads=8 --server-id \"$target_artifactory\"" | tee -a "$all_commands_file" && \
        jf rt u "$line" "$target_path" --threads=8 --server-id "$target_artifactory" && \
        echo "Executing: jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$encoded_target_path?atomicProperties=1\" --server-id \"$target_artifactory\" -d \"$escaped_modified_json\"" | tee -a "$all_commands_file" && \
        jf rt curl -k -sL -XPATCH -H "Content-Type: application/json" "/api/metadata/$encoded_target_path?atomicProperties=1" --server-id "$target_artifactory" -d "$escaped_modified_json" && \
        rm -rf "$line" && \
        cd "$current_dir" # Return to the saved directory i.e "$OLDPWD"
        if [ $? -ne 0 ]; then
            echo "At least one command failed for: $source_repo/$line" | tee -a "$current_dir/$failed_commands_file"
        else
            echo "All commands succeeded for: $source_repo/$line" | tee -a "$current_dir/$successful_commands_file"
        fi
    else
        # Execute the commands for a single artifact
        cd "$folder_position" && \
        echo "Executing: jf rt dl \"$source_repo/$line\" . --threads=8 --server-id \"$source_artifactory\"" | tee -a "$all_commands_file" && \
        jf rt dl "$source_repo/$line" . --threads=8 --server-id "$source_artifactory" && \
        echo "Executing: jf rt u \"$line\" \"$target_path\" --threads=8 --server-id \"$target_artifactory\"" | tee -a "$all_commands_file" && \
        jf rt u "$line" "$target_path" --threads=8 --server-id "$target_artifactory" && \
        rm -rf "$line" && \
        cd "$current_dir" # Return to the saved directory i.e "$OLDPWD"
        if [ $? -ne 0 ]; then
            echo "At least one command failed for: $source_repo/$line" | tee -a "$current_dir/$failed_commands_file"
        else
            echo "All commands succeeded for: $source_repo/$line" | tee -a "$current_dir/$successful_commands_file"
        fi
    fi
}



run_migrate_command() {

    local src_list_command="$1"
    local target_list_command="$2"
    local folder_to_migrate="$3"
    local folder_position="$4"  # Pass the folder position as an argument
    local sibling_folder_count="$5"
    local top_or_inner="$6"

    mkdir -p $folder_position


    context=$(echo "$folder_to_migrate" | tr '/' '_' | tr '.' '_')
    context="${context}_${top_or_inner}"
    # Modify the file names for files "a," "b," and "c"

    a="$folder_position/src_list_$source_repo_$context"
    b="$folder_position/target_list_$source_repo_$context"
    c="$folder_position/migrate_list_$source_repo_$context"


    # Log what is currently running
    echo "[Progress: $folder_position out of $sibling_folder_count sub folders]" | tee -a "$all_commands_file"
    echo "Running commands:" | tee -a "$all_commands_file"
    echo "$src_list_command" | tee -a "$all_commands_file"
    echo "$target_list_command" | tee -a "$all_commands_file"



    # Run the command
    # echo "$src_list_command"
    # echo "$target_list_command"
    # Enable debugging
    #  set -x

    src_output=$(eval "$src_list_command")
    src_exit_status=$?

    if [ $src_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $src_list_command" | tee -a "$failed_commands_file"
    fi

    target_output=$(eval "$target_list_command")
    target_exit_status=$?

    if [ $target_exit_status -ne 0 ]; then
        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $target_list_command" | tee -a "$failed_commands_file"
    fi
    # Disable debugging when no longer needed
    #  set +x
    if [ $src_exit_status -eq 0 ] && [ $target_exit_status -eq 0 ]; then
        # By using double quotes around $src_output when passing it to echo and when saving it to the file, the exact formatting, including extra spaces, is preserved.
        echo "$src_output" > "${a}.tmp"
        echo "In run_migrate_command - 1 - b4 calling jq"
#        cat "${a}.tmp"
        cat "${a}.tmp" | jq  '.results[] | select(has("path") and .path != null and has("name") and .name != null and has("sha256") and .sha256 != null) | ((.path + "/" + .name) | sub("^\\./"; "")) + "," + (.sha256|tostring)'  > "$a"
#        echo "In run_migrate_command - 2 - after calling jq"
#        cat "${a}"

        echo "$target_output" > "${b}.tmp"
#        echo "In run_migrate_command - 3 - b4 calling jq"
#        cat "${b}.tmp"
        cat "${b}.tmp" | jq  '.results[] | select(has("path") and .path != null and has("name") and .name != null and has("sha256") and .sha256 != null) | ((.path + "/" + .name) | sub("^\\./"; "")) + "," + (.sha256|tostring)'  > "$b"
#        echo "In run_migrate_command - 4 - after calling jq"

        #join -v1  <(sort "$a") <(sort "$b") | sed -re 's/,[[:alnum:]]+"$/"/g' | sed 's/"//g'| sed  '/\(index\.json\|\.timestamp\|conanmanifest\.txt\)$/d' > "$c"
        # join -v1  <(sort "$a") <(sort "$b") | sed -E -e 's/,[[:alnum:]]+"$/"/g' -e 's/"//g' -e '/(index\.json|\.timestamp|conanmanifest\.txt)$/d' > "$c"
        echo "In $(pwd) comparing - $a    to   $b"
        # join -v1  <(sort "$a") <(sort "$b") | sed -E -e 's/,[[:alnum:]]+"$/"/g' -e 's/"//g'  > "$c"
        # comm -23 <(sort "$a") <(sort "$b") | sed -E -e 's/,[[:alnum:]]+"$/"/g' -e 's/"//g'  > "$c"
        comm -23 <(sort "$a") <(sort "$b") | awk '{gsub(/,[[:alnum:]]+\"$/, "\""); gsub(/"/, ""); print}' > "$c"

        # Check if the file exists and is not empty
        if [ -s "$c" ]; then
            if [ "${TRANSFERONLY}" = "no" ]; then
                echo "-------------------------------------------------"
                echo "Files diff in $c for source $source_artifactory - Repo [$source_repo]/$folder_to_migrate -  [Progress: $folder_position out of $sibling_folder_count folders]"
                echo "-------------------------------------------------"

                cat -b "$c"
            elif [ "${TRANSFERONLY}" = "yes" ]; then
                while IFS= read -r line
                do

                    # If the file path i.e the $line has a space in the folder or file name then encode it:
                    encoded_file_path=$(urlencode_spaces "$line")


                    # Does the artifact have properties
                    get_item_properties_cmd="jf rt  curl -s -k -XGET \"/api/storage/$source_repo/$encoded_file_path?properties\" --server-id $source_artifactory"
#                    echo $get_item_properties_cmd
                    prop_output=$(eval "$get_item_properties_cmd")
                    prop_exit_status=$?
                    # echo $prop_output

                    if [ $prop_exit_status -ne 0 ]; then
                        echo "Error: Command failed for folder: $folder_to_migrate - Run Command: $get_item_properties_cmd" | tee -a "$failed_commands_file"

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
                        echo "Executing: execute_artifact_migration \"$folder_position\" \"$source_repo\" \"$line\" \"$source_artifactory\" \"$target_repo\" \"$target_artifactory\" \"$escaped_modified_json\""

                        execute_artifact_migration "$folder_position" "$source_repo" "$line" "$source_artifactory" \
                        "$target_repo" "$target_artifactory" "$escaped_modified_json" &

                        # Limit the number of concurrent background execute_artifact_migration jobs
                        job_count=$(jobs -p | wc -l)
                        if [ "$job_count" -ge "$parallel_count" ]; then
                            wait
                        fi


                    fi

                done < "$c"
            else
                echo "Wrong 5th Parameter, 5th parameter value should be yes or no"
            fi
        else
            echo "The file $c is either empty or doesn't exist."
        fi
        # Wait for execute_artifact_migration background jobs to complete
        wait
       rm -f "$a" "${a}.tmp" "$b" "${b}.tmp" "$c"
    fi
}


# Function to run the migration for a folder and its sub-folders
run_migration_for_folder() {
    local src_list_command="$1"
    local target_list_command="$2"
    local folder_to_migrate="$3"
    local folder_position="$4"  # Pass the folder position as an argument
    local sibling_folder_count="$5"
    local top_or_inner="$6"

    # Create and run a background job for the folder
    (
        run_migrate_command "$src_list_command" "$target_list_command" "$folder_to_migrate" "$folder_position" "$sibling_folder_count" "$top_or_inner"
    ) &

    # Check the number of background run_migrate_command jobs and wait for them to complete if it exceeds 5
    job_count=$(jobs -p | wc -l)
    if [ $job_count -ge 5 ]; then
        wait
    fi


}


# Function to URL-encode only spaces in a string
urlencode_spaces() {
    local encoded=""
    local char
    for (( i=0; i<${#1}; i++ )); do
        char="${1:i:1}"
        if [ "$char" == " " ]; then
            encoded="$encoded$(printf '%%%02X' "'$char")"
        else
            encoded="$encoded$char"
        fi
    done
    echo "$encoded"
}



migrateFolderRecursively(){
    # Enable debugging
    # set -x
    # Define a stack to keep track of folders to process
    folder_stack=("$1")

    # Iterate until the stack is empty
    while [ ${#folder_stack[@]} -gt 0 ]; do
        # Print the contents of the folder_stack
#        echo "Current folder_stack contents:"
#        for folder in "${folder_stack[@]}"; do
#            echo "----->$folder"
#        done

        # Pop the top folder from the stack safely
        l_root_folder="${folder_stack[0]}"
        folder_stack=("${folder_stack[@]:1}")

        # Print l_root_folder for debugging
        # echo "Processing folder: $l_root_folder"

        # Find all the sub-folders of the $l_root_folder
        if [ "$l_root_folder" != "." ]; then
            # If the "$l_root_folder" has a space in the folder name then urlencode it.
            encoded_path=$(urlencode_spaces "$l_root_folder")
            echo "Executing: jf rt curl -s -k -XGET \"/api/storage/$source_repo/$encoded_path?list&deep=1&depth=1&listFolders=1\" --server-id $source_artifactory" | tee -a "$all_commands_file"
            output=$(jf rt curl -s -k -XGET "/api/storage/$source_repo/$encoded_path?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
        else
            echo "Executing: jf rt curl -s -k -XGET \"/api/storage/$source_repo?list&deep=1&depth=1&listFolders=1\" --server-id $source_artifactory" | tee -a "$all_commands_file"
            output=$(jf rt curl -s -k -XGET "/api/storage/$source_repo?list&deep=1&depth=1&listFolders=1" --server-id $source_artifactory)
        fi


#        echo "In migrateFolderRecursively - 1 - b4 calling jq"
        # Parse the JSON output using jq and get the "uri" values for folders
        # echo "$output"
        folders=$(echo "$output"  | jq -r '.files[] | select(has("folder") and .folder != null and .folder == true and has("uri") and .uri != null) |  .uri')

#        echo "In migrateFolderRecursively - 2 - after calling jq"

        # Split folders into an array
        IFS=$'\n' read -rd '' -a folders_array <<< "$folders"

        # Calculate the total number of sub-folders
        local total_folders=$(( ${#folders_array[@]} ))
        echo "total_folders is $total_folders . is it >= 1"

        if [ "$total_folders" -ge 1 ]; then
            echo "yes it is ......"
            for folder_position in "${!folders_array[@]}"; do
                folder="${folders_array[$folder_position]}"
                #Remove the leading slash i.e if folder is "/abc" it becomes "abc"
                folder="${folder#/}"
                if [ -n "$folder" ]; then # folder is not null
                    # Check if the folder name starts with a dot like ".conan" , ".npm" or if it's "_uploads" skip it
                    # as it will be generated.
                    # Also skip any other folder in the "$EXCLUDE_FOLDERS" that user wants to exclude
                    echo "~~~~~~~~~~~>${folder}"
                    if [[ "$EXCLUDE_FOLDERS" == *";$folder;"* ]] || [[ "$folder" == .* ]]  || [ "$folder" = "_uploads" ]; then
                        echo "============excluding=====>${folder}"
                        continue  # Skip this iteration of the loop
                    fi

                    # Push the subfolder onto the stack for processing
                    if [ "$l_root_folder" = "." ]; then
                        folder_to_migrate="$folder"
                    else
                        folder_to_migrate="$l_root_folder/$folder"
                    fi
                    echo "Push the subfolder {$folder_to_migrate} onto the stack for processing ..."
                    folder_stack+=("$folder_to_migrate")
                fi
            done

        fi

        # Process the "$l_root_folder"  contents as the subfolders will be processed  when the stack is popped.
        echo "Check if the  files in $l_root_folder needs to be migrated."
        echo "Processing folder: $l_root_folder"
        processFolderContents "$l_root_folder"

    done
    # Disable debugging (optional)
    # set +x
}



processFolderContents() {
    local folder_to_migrate="$1"

#    echo " In processFolderContents folder_to_migrate is '$folder_to_migrate'"
    echo "In processFolderContents folder_to_migrate is '$folder_to_migrate'" | tee -a "$all_commands_file"



    # migrate files in the sub-folder
    src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"


    target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$folder_to_migrate\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"


    #Call the migrate command without the trailing * to migrate files in  $folder_to_migrate
    #folder_to_migrate="${folder_to_migrate/%\*/}"  # Remove the trailing "*"
    # run_migration_for_folder "$src_files_list_in_this_folder_command" "$target_files_list_in_this_folder_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders"
    run_migration_for_folder "$src_command1" "$target_command1" "$folder_to_migrate" "1" "1" "top"


    # Check if the folder exists
    # echo "1st  for loop In $(pwd) - Checking Folder $((folder_position+1))/$folder_to_migrate is empty . If empty remove. ---->" >> "$failed_commands_file"
    # echo "$(du -sh $((folder_position+1))/$folder_to_migrate)" >> "$failed_commands_file"
    # echo "$(ls -al $((folder_position+1))/$folder_to_migrate)" >> "$failed_commands_file"


    # Wait for any remaining run_migration_for_folder background jobs to complete
    wait

    # Loop through the folders numbered >=1  i.e output/1 , output/2 .. and delete the folders .
    # Loop through the folders numbered >=1  i.e output/1 , output/2 .. and delete the folders .
    # The files in folder 0 are artifacts so are already deleted.
    # So folder 0 should already be empty.


    # Check if the folder exists
    if [ -d "1/$folder_to_migrate" ]; then
        # Check if the folder is empty
        if [ -z "$(find 1/$folder_to_migrate -type f 2>/dev/null)" ]; then
        #if [ "$(du -s $((folder_position+1))/$folder_to_migrate | awk '{print $1}')" -eq 0 ]; then
            echo "Folder 1/$folder_to_migrate is empty, removing..." | tee -a "$successful_commands_file"
            rm -rf "1/$folder_to_migrate"
        else
            echo "Folder '1/$folder_to_migrate' is not empty." | tee -a "$failed_commands_file"
            echo "$(du -s 1/$folder_to_migrate | awk '{print $1}')"  | tee -a "$failed_commands_file"
            # Add additional actions for non-empty folders here if needed
        fi
    fi

}






# check for files in the root folder:
src_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $source_artifactory --insecure \
--data 'items.find({\"repo\":  {\"\$eq\":\"$source_repo\"}, \"path\": {\"\$match\": \"$root_folder\"},\
    \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"


target_command1="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $target_artifactory --insecure \
--data 'items.find({\"repo\":  {\"\$eq\":\"$target_repo\"}, \"path\": {\"\$match\": \"$root_folder\"},\
    \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")'"



#Call the migrate command without the trailing * to migrate files in the $root_folder
run_migrate_command "$src_command1" "$target_command1" "$root_folder" "0" "0" "top"



if [ "$migratefiles_and_subfolders_recursive" = "yes" ]; then
    # Process sub-folders
    migrateFolderRecursively "$root_folder"
fi

echo "All transfers for $source_repo completed" | tee -a "$successful_commands_file"

