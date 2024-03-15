#! /bin/bash
# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right
# to use this code solely in connection with your use of a JFrog product or service.
# This code is provided 'as-is' and without any warranties or conditions, either
# express or implied including, without limitation, any warranties or conditions of
# title, non-infringement, merchantability or fitness for a particular cause.
# Nothing herein shall convey to you any right or title in the code, other than
# for the limited use right set forth herein. For the purposes hereof "you" shall
# mean you as an individual as well as the organization on behalf of which you
# are using the software and the JFrog product or service.

### sample cmd to run
# bash testremote_all_remote_repos.sh psemea
# or
# bash testremote_all_remote_repos.sh psemea "aba-test-docker-remote;anypoint-mulesoft-dev-remote" "anypoint-mulesoft-public-dev-remote;aws-terraform"
###

### Exit the script on any failures

## define variables
source="${1:?source-serverId ex - source-server}"
includerepos="${2:-}" # Optional semicolon-separated list of repos to include
excluderepos="${3:-artifactory-build-info;_intransit}" # Optional semicolon-separated list of repos to exclude with

# default value
TYPE="remote"

### Get the repository list
for REPO in $(jf rt curl "api/repositories?type=${TYPE}" -s --server-id="$source" | jq -r '.[].key'); do


    # Check if the repository is in the exclusion list
    if [[ -n "$excluderepos" ]] && [[ "$excluderepos" =~ (^|;)${REPO}(;|$) ]]; then
        echo "Skipping excluded Repo $REPO"
    # Check if the repository is not in the inclusion list
    elif [[ -n "$includerepos" ]] && [[ ! "$includerepos" =~ (^|;)${REPO}(;|$) ]]; then
        echo "Skipping Repo not in includerepos $REPO"
    else
        # If not excluded or not in the exclusion list, execute the desired actions for the repository
        #    echo "Getting configuration for $REPO"
#    Found this API from browser inspect     GET https://example.jfrog.io/ui/api/v1/ui/admin/repositories/remote/dev-maven-remote-a
        config=$(jf rt curl "api/admin/repositories/remote/$REPO" --server-id="$source" -s)

        echo "Test remote repo  '$REPO' in $source"

        # Check if "password" is not empty
        password=$(jq -r '.advanced.network.password' <<< "$config")
        if [[ -n "$password" && "${#password}" -gt 0 ]]; then
            echo "$REPO password is not empty and is $password"
        else
            echo "$REPO password is empty"
        fi


#        data=$(jf rt curl -X POST "api/admin/repositories/testremote" \
#               -H "Content-Type: application/json" -d "$config" --server-id="$source" -s | grep error | xargs)

        # Run the command and capture the output
        output=$(jf rt curl -X POST "api/admin/repositories/testremote" \
                 -H "Content-Type: application/json" -d "$config" --server-id="$source" -s)


        if [[ $output == *"error"* ]]; then
            echo "$REPO connection failed with error : $output"
            echo "=========================================="
        else
            echo "$REPO connection successful" : $output
            echo "=========================================="
        fi
    fi

done
