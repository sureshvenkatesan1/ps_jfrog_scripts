#! /bin/bash

### Exit the script on any failures
## define variables
if [ $# -lt 2 ]; then
    echo "Usage: $0 <source> <target> <semicolon_seperated_repos> [--dry-run]"
    exit 1
fi



source_server="${1}"
target_server="${2}"
repos_input="${3}"
dry_run=0

if [ "$4" = "--dry-run" ]; then
    dry_run=1
fi

# Define the replication directory
replication_dir="replication"
mkdir -p "${replication_dir}"
cd "${replication_dir}"

IFS=';' read -ra REPOS <<< "$repos_input"

rm -rf *.json

# Set the source Artifactory server
jf config use "${source_server}"

# Define cron settings. .The below schedules replication for all repos 2 minutes apart
max=60
maxhr=24
cronmin=0
mininterval=2
cronhr=0
reset=0

for REPO in "${REPOS[@]}"; do
    REPO_FILENAME=$(echo ${REPO} | sed 's/[^a-zA-Z0-9]/_/g') # Get a valid filename

    data=$(jf rt curl api/replications/${REPO_FILENAME} -s | grep message | xargs)

    if [[ $data == *"message"* ]]; then
        echo "Creating JSON payload for replicating ${REPO_FILENAME}"

        if [ $cronmin -lt $max -a $cronhr -lt $maxhr ]; then
            cronmin=$(( $mininterval + $cronmin))
            if [[ $cronmin -eq $max ]]; then
                cronhr=$(( $cronhr + 1))
                cronmin=$reset
            fi
        elif [[ $cronmin -eq $max ]]; then
            cronhr=$(( $cronhr + 1))
            cronmin=$reset
        elif [[ $cronhr -eq $maxhr ]]; then
            cronhr=$reset
            cronmin=$reset
        fi

        echo '{ "enabled": "true","cronExp":"0 '$cronmin' '$cronhr' * * ?",' > ${REPO_FILENAME}-template.json
        # Insert the repository Key
        echo '"repoKey": "'$REPO'",' >> ${REPO_FILENAME}-template.json
        # Insert the remaining parameters, note we're replicating to the same repository name
        echo '"serverId": "'$target_server'", "targetRepoKey": "'$REPO'", "enableEventReplication":"true" }' >> ${REPO_FILENAME}-template.json

        # Create delete replication script proactively
        echo "jf rt replication-delete ${REPO_FILENAME} --server-id="${source_server}" --quiet" >> delete-replication.txt
    else
        echo "Replication already available - Add the replication manually"
        echo "$REPO_FILENAME" >> replication-configured-repos.txt
    fi
done

for json_file in *.json; do

    echo "jf rt replication-create ${json_file} --server-id="${source_server}""
    if [ "$dry_run" -eq 0 ]; then
        echo "Running: jf rt replication-create ${json_file}"
        jf rt replication-create ${json_file} --server-id="${source_server}"
    fi
done