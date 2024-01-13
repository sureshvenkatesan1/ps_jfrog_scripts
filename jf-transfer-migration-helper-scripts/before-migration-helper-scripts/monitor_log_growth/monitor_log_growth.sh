#!/bin/bash
# script to monitor the log growth to determine if your script that writes to the log file is completed.

# bash ./monitor_log_growth.sh . 'upload-session*.log' 30

# Check if the correct number of arguments is provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <log_directory> <log_file_pattern> <sleep_duration_seconds>"
    exit 1
fi

log_dir="$1"
log_pattern="$2"
sleep_duration="$3"

# Check if the provided directory exists
if [ ! -d "$log_dir" ]; then
    echo "Directory '$log_dir' does not exist."
    exit 1
fi

# Find all the relevant files using the provided pattern
files=$(find "$log_dir" -type f -name "$log_pattern")

# Check if any files were found
if [ -z "$files" ]; then
    echo "No files matching pattern '$log_pattern' found in '$log_dir'."
    exit 1
fi

# Function to check a file for growth
check_file_growth() {
    local file="$1"
    local initial_size=$(stat -c %s "$file")
    sleep "$sleep_duration"
    local final_size=$(stat -c %s "$file")
    
    if [ "$final_size" -ne "$initial_size" ]; then # other options use -gt
        echo "File '$file' has grown in the last $sleep_duration seconds. <----------"
    else
        echo "File '$file' has not grown in the last $sleep_duration seconds."
    fi
}

# Loop through the files and check each file in the background
for file in $files; do
    check_file_growth "$file" &
done

# Wait for all background jobs to complete
wait
