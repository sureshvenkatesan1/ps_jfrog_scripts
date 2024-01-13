#Empty the contents of a  a huge repo in a multi-threaded way ( to avoid  "504 Gateway Time-out" mentioned in 263977 )
# Note: Not sure if the tuning from 24153 was tried out as customer just tried repication without the webserver
#to avoid the Time-out , which is not possible in SAAS migration.
# using jf:
#jf rt del example-repo-local/ --quiet --server-id=mill
#
#or
#
#How to delete the artifacts 2 at a time in a loop until
#output=$(jf rt del example-repo-local/ --limit=2 --quiet)
#the output returns a json with "success" value as 0 or the command errored out. Usually it returns
#{
#  "status": "success",
#  "totals": {
#    "success": 2,
#    "failure": 0
#  }
#}
#You can now run the script  to delete artifacts from repository in batches as below.
#bash ./delete_artifacts_in_repo_in_batches.sh example-repo-local 1000 mill
#Replace example-repo-local, 1000, and mill with your desired repository name, limit value, and server ID.
#The script will use these values to perform artifact deletion.

#!/bin/bash

# Check if required parameters are provided
if [ $# -ne 3 ]; then
  echo "Usage: $0 <repository-name> <limit-value> <server-id>"
  exit 1
fi

repo_name="$1"
limit_value="$2"
server_id="$3"

while true; do
  output=$(jf rt del "$repo_name/" --limit="$limit_value" --quiet --server-id="$server_id")

  # Check if the command errored out
  if [ $? -ne 0 ]; then
    echo "Command errored out."
    break
  fi

  # Parse the JSON output using jq
#  success=$(echo "$output" | jq -r '.totals.success')

  # or Extract success value from output
  success=$(echo "$output" | grep -o '"success": [0-9]*' | awk '{print $2}')


  # Check if success value is 0
  if [ "$success" -eq 0 ]; then
    echo "Deletion complete."
    break
  fi

  echo "Deleted $success artifacts."
done

