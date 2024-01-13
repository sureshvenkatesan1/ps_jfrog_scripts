#!/bin/bash
# usage: ./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test | ./runcommand_in_parallel_and_log_outcome.sh properties_patch_failed.txt 16

log_file=$1
max_parallel="$2"

# Function to execute a single command and log failures
execute_command() {
  local command="$1"
  local log_file="$2"
  local output="$($SHELL -c "$command" 2>&1)"
  
  if [ $? -eq 0 ]; then
    echo "Command successful: $command"
  else
    echo "Command failed: $command"
    echo "$command" >> "$log_file"
    echo "$output" >> "$log_file"
  fi
  
  
}

# Check if max_parallel is a positive integer
if [[ ! "$max_parallel" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: max_parallel must be a positive integer."
  exit 1
fi

# Read commands from standard input
while IFS= read -r command; do
  # Remove leading and trailing whitespace
  command="$(echo -e "${command}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  
  # Check if the trimmed command is not empty
  if [ -n "$command" ]; then
    execute_command "$command" "$log_file" &
    
    # Limit the number of parallel processes
    while (( $(jobs | wc -l) >= max_parallel )); do
      sleep 1
    done
  fi
done

# Wait for all background jobs to finish
wait
