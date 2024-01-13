#!/bin/bash

# Function to log commands
log_command() {
    local command="$1"
    local folder_position="$2"
    local total_folders="$3"
    local log_file="$4"
    echo "$command [Progress: $folder_position out of $total_folders]" >> "$log_file"
}

# Function to run a command and log errors, returns exit status
run_command() {
    local command="$1"
    local folder_position="$2"
    local total_folders="$3"
    local failed_commands_file="$4"
    local list_file="$5"
    local all_commands_file="$6"

    log_command "$command" "$folder_position" "$total_folders" "$all_commands_file"
    eval "$command >> $list_file"
    exit_status=$?

    if [ $exit_status -ne 0 ]; then
        echo "Error: Command failed - $command" >> "$failed_commands_file"
    fi

    return $exit_status
}

# # Function to run the migrate command
# run_migrate() {
#     local source_command="$1"
#     local target_command="$2"
#     local folder_to_migrate="$3"
#     local folder_position="$4"
#     local total_folders="$5"
#     local failed_commands_file="$6"

#     run_command "$source_command" "$folder_position" "$total_folders" "$failed_commands_file" "a"
#     src_exit_status=$?

#     run_command "$target_command" "$folder_position" "$total_folders" "$failed_commands_file" "b"
#     target_exit_status=$?

#     if [ $src_exit_status -eq 0 ] && [ $target_exit_status -eq 0 ]; then
#         # Your migration logic here
#         perform_migration_logic "a" "b" "$folder_position" "$total_folders" "$failed_commands_file"

#     fi
# }

# Function to perform migration logic
perform_migration_logic() {
    local source_file="$1"
    local target_file="$2"
    local folder_position="$3"
    local total_folders="$4"
    local failed_commands_file="$5"
    local folder_to_migrate="$6"
     local source_repo="$7"
     local source_artifactory="$8" 
     local target_repo="$9" 
     local target_artifactory="$10"

    join -v1 <(sort "$source_file") <(sort "$target_file") | sed -re 's/,[[:alnum:]]+"$/"/g' | sed 's/"//g' > c

    if [ "${TRANSFERONLY}" = "no" ]; then
        echo "-------------------------------------------------"
        echo "Files diff from source $source_artifactory - Repo [$source_repo]/$folder_to_migrate -  [Progress: $folder_position out of $total_folders folders]"
        echo "-------------------------------------------------"
        cat -b c
    elif [ "${TRANSFERONLY}" = "yes" ]; then
        # generate_transfer_commands "c" "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"
        while IFS= read -r line; do
            echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; rm -rf \"$line\" "
        done < "$diff_file"
    else
        echo "Wrong 5th Parameter, 5th parameter value should be yes or no"
    fi
    read -r
    rm -f "a" "b" "c"
}

# Function to generate transfer commands
generate_transfer_commands() {
    local diff_file="$1"
    local source_repo="$2"
     local source_artifactory="$3" 
     local target_repo="$4" 
     local target_artifactory="$5"

    while IFS= read -r line; do
        echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; rm -rf \"$line\" "
    done < "$diff_file"
}

# Function to list files for a given folder
list_files() {
    local folder="$1"
    local repo="$2"
    local artifactory="$3"
    local jq_sed_cmd="$4"

    local command="jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $artifactory --insecure \
    --data 'items.find({\"repo\":  {\"\$eq\":\"$repo\"}, \"path\": {\"\$match\": \"$folder\"},\
        \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")' $jq_sed_cmd"

    echo "$command"
}

# Call the migrate command
run_migrate_command() {
    local src_list_in_this_folder_command="$1"
    local target_list_in_this_folder_command="$2"
    local folder_to_migrate="$3"
    local folder_position="$4"
    local total_folders="$5"
    local failed_commands_file="$6"
    local all_commands_file="$7"
     local source_repo="$8"
     local source_artifactory="$9" 
     local target_repo="$10" 
     local target_artifactory="$11"

    # run_migrate "$src_folder" "$target_folder" "$folder_to_migrate" "$folder_position" "$total_folders" "$failed_commands_file"

    run_command "$src_list_in_this_folder_command"  "$folder_position" "$total_folders" "$failed_commands_file" "a" "$all_commands_file"
    src_exit_status=$?

    run_command "$target_list_in_this_folder_command" "$folder_position" "$total_folders" "$failed_commands_file" "b" "$all_commands_file"
    target_exit_status=$?

    # if [ $src_exit_status -eq 0 ] && [ $target_exit_status -eq 0 ]; then
    #     # Your migration logic here
    #     # perform_migration_logic "a" "b" "$folder_position" "$total_folders" "$failed_commands_file" "$folder_to_migrate" "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"

    #         join -v1 <(sort a) <(sort b) | sed -re 's/,[[:alnum:]]+"$/"/g' | sed 's/"//g' > c

    #         if [ "${TRANSFERONLY}" = "no" ]; then
    #             echo "-------------------------------------------------"
    #             echo "Files diff from source $source_artifactory - Repo [$source_repo]/$folder_to_migrate -  [Progress: $folder_position out of $total_folders folders]"
    #             echo "-------------------------------------------------"
    #             cat -b c
    #         elif [ "${TRANSFERONLY}" = "yes" ]; then
    #             # generate_transfer_commands "c" "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"
    #             while IFS= read -r line; do
    #                 echo "jf rt dl \"$source_repo/$line\" . --threads=8 --server-id $source_artifactory ; jf rt u \"$line\" \"$target_repo/$line\" --threads=8 --server-id $target_artifactory ; rm -rf \"$line\" "
    #             done < "$diff_file"
    #         else
    #             echo "Wrong 5th Parameter, 5th parameter value should be yes or no"
    #         fi

    #         rm -f "a" "b" "c"

    # fi
}

# Function to process folders
process_folders() {


    local root_folder="$1"
    local source_artifactory="$2"
    local source_repo="$3"
    local target_artifactory="$4"
    local target_repo="$5"
    local jq_sed_command="$6"
    local failed_commands_file="$7"
    local all_commands_file="$8"
    #https://unix.stackexchange.com/questions/612401/how-do-i-pass-an-array-as-an-argument
    # typeset -n folders_array1="$1"
    shift
    folders_array1=("$@")

    #reconstruct the array
    # for index in "${folder_array_indices[@]}"; do
    #     folders_array+=("${folders_arra[$index]}")
    # done

    # Calculate the total number of sub-folders
    total_folders="$(expr "${#folders_array1[@]}" + 1)"


    for folder_position in "${!folders_array1[@]}"; do
        
        folder="${folders_array1[$folder_position]}"
        echo "$folder $source_artifactory  $target_artifactory"

        # Remove the leading slash i.e if folder is "/abc" it becomes "abc"
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

        src_list_in_this_folder_command=$(list_files "$folder_to_migrate" "$source_repo" "$source_artifactory" "$jq_sed_command")
        target_list_in_this_folder_command=$(list_files "$folder_to_migrate" "$target_repo" "$target_artifactory" "$jq_sed_command")
  
        # Call the migrate command without the trailing * in $folder_to_migrate
        run_migrate_command "$src_list_in_this_folder_command" "$target_list_in_this_folder_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders" "$failed_commands_file" "$all_commands_file"  "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"


        # Now check in the subfolders:
        src_list_in_subfolders_command=$(list_files "$folder_to_migrate/*" "$source_repo" "$source_artifactory" "$jq_sed_command")
        target_list_in_subfolders_command=$(list_files "$folder_to_migrate/*" "$target_repo" "$target_artifactory" "$jq_sed_command")

        # Call the migrate command without the trailing * in $folder_to_migrate
        run_migrate_command "$src_list_in_subfolders_command" "$target_list_in_subfolders_command" "$folder_to_migrate" "$((folder_position+1))" "$total_folders" "$failed_commands_file" "$all_commands_file"  "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"
    done
}




main() {

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

    # Log files
    failed_commands_file="failed_commands.txt"
    all_commands_file="all_commands.txt"
    successful_commands_file="successful_commands.txt"

    # Check if the fifth parameter (root-folder) is provided
    if [ $# -ge 6 ]; then
        root_folder="$6"
    else
        root_folder=""
    fi



    # List files for the root folder
    if [ -z "$root_folder" ]; then
        src_list_in_dot_folder_command=$(list_files "." "$source_repo" "$source_artifactory" "$jq_sed_command")
        target_list_in_dot_folder_command=$(list_files "." "$target_repo" "$target_artifactory" "$jq_sed_command")
    else
        src_list_in_dot_folder_command=$(list_files "$root_folder" "$source_repo" "$source_artifactory" "$jq_sed_command")
        target_list_in_dot_folder_command=$(list_files "$root_folder" "$target_repo" "$target_artifactory" "$jq_sed_command")
    fi


    # Call the migrate command without the trailing * in $root_folder
    run_migrate_command "$src_list_in_dot_folder_command" "$target_list_in_dot_folder_command" "$root_folder" "0" "0" "$failed_commands_file" "$all_commands_file"  "$source_repo" "$source_artifactory" "$target_repo" "$target_artifactory"


    # Rest of your code for processing subfolders and cleaning up
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
  
    # folders_array_indices=("${!folders_array[@]}")  # Get the array indices
    #https://unix.stackexchange.com/questions/612401/how-do-i-pass-an-array-as-an-argument
    if [ "${TRANSFERONLY}" = "yes" ]; then
        # Process folders in parallel
        process_folders  "$root_folder" "$source_artifactory" "$source_repo" "$target_artifactory" "$target_repo" "$jq_sed_command" "$failed_commands_file" "$all_commands_file" "${folders_array[@]}" #| parallel -j 8
    else
        # Process folders sequentially
        process_folders  "$root_folder" "$source_artifactory" "$source_repo" "$target_artifactory" "$target_repo" "$jq_sed_command" "$failed_commands_file" "$all_commands_file" "${folders_array[@]}"
    fi

    # if [ "${TRANSFERONLY}" = "yes" ]; then
    #     # Process folders in parallel
    #     process_folders "$folders_array" "$root_folder" "$source_artifactory" "$source_repo" "$target_artifactory" "$target_repo" "$jq_sed_command" "$failed_commands_file" "$all_commands_file" | parallel -j 8
    # else
    #     # Process folders sequentially
    #     process_folders "$folders_array" "$root_folder" "$source_artifactory" "$source_repo" "$target_artifactory" "$target_repo" "$jq_sed_command" "$failed_commands_file" "$all_commands_file"
    # fi

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

}




# Call the main function with command-line arguments
main "$@"
