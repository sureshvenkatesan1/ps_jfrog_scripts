#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <log_directory> <log_file_pattern>"
    exit 1
fi

log_dir="$1"
log_pattern="$2"

# Check if the provided directory exists
if [ ! -d "$log_dir" ]; then
    echo "Directory '$log_dir' does not exist."
    exit 1
fi

# Find all the relevant files using the provided pattern and execute the monitoring for each file in parallel
find "$log_dir" -type f -name "$log_pattern" -print0 |
    parallel -0 -j0 'timeout 60s bash -c "initial_size=$(stat -c %s {}); sleep 60; final_size=$(stat -c %s {}); if [ "$final_size" -gt "$initial_size" ]; then echo \"File {} has grown in the last 60 seconds.\"; else echo \"File {} has not grown in the last 60 seconds.\"; fi"'

