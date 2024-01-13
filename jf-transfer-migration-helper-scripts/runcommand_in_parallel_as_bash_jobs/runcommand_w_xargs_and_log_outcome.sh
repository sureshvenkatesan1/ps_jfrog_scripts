#!/bin/bash
# usage: ./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test | tr '\n' '\0' | xargs -0 -P 8 -I {} ./runcommand_log_outcome.sh '{}' properties_patch_failed.txt
command=$1
log_file=$2

# Remove leading and trailing whitespace from the command
command="$(echo -e "${command}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

# Check if the length of the trimmed command is greater than 1
if [ ${#command} -gt 1 ]; then

    # Run the command within a new shell and capture both stdout and stderr
    # output="$($command 2>&1)"
    output="$($SHELL -c "$command" 2>&1)"

    # Check if the command was successful
    if [ $? -eq 0 ]; then
        # Command was successful, log it to stdout
        echo "Command successful: $command"
    else
        # Command failed, log it to stderr and the log file
        echo "Command failed: $command"
        echo "$command" >> "$log_file"
        # Log the output to the log file
        echo "$output" >> "$log_file"
    fi

fi