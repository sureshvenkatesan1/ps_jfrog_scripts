#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right
# to use this  code   solely in connection with your use of a JFrog product or service.
# This  code is provided 'as-is' and without any warranties or conditions, either
# express or implied including, without limitation, any warranties or conditions of
# title, non-infringement, merchantability or fitness for a particular cause.
# Nothing herein shall convey to you any right or title in the code, other than
# for the limited use right set forth herein. For the purposes hereof "you" shall
# mean you as an individual as well as the organization on behalf of which you
# are using the software and the JFrog product or service.

### Exit the script on any failures
## define variable
server_id="${1:?Enter  artifactory server ID}"
cd maven-high
#rm non-unique-maven-snapshotVersionBehavior.list
#rm *.json


jf rt curl api/repositories\?type=local\&packageType=Maven -s --server-id=$server_id | jq -rc '.[] | .key' > repositories.list

cat repositories.list |  while read line
do
    REPO=$(echo $line | cut -d ':' -f 2)
    echo "Getting configuration for "$REPO
    jf rt curl api/repositories/$REPO --server-id=$server_id >> $REPO-config.json

    cat  $REPO-config.json  | jq -r 'select(.snapshotVersionBehavior == "non-unique" ) | .key' >> maven-non-unique-ncr.list
    rm $REPO-config.json
done