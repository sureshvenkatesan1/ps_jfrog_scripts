#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service.

source="proservices"
target="ramkannan"

## Policies
for row in  $(jf xr curl  -s -XGET /api/v2/policies --server-id="${source}" | jq -r '.[] | @base64'); do
    data=$(echo "${row}" | base64 --decode)
    policyname=$(echo $data | tr -d {\"name\": | cut -d "," -f 1)
    echo "Policy Name ===> $policyname <==="
    jf xr curl -XPOST /api/v2/policies -H 'Content-Type: application/json' -d "${data}" --server-id="${target}"
    echo -e "\n"
done

## WATCHES
for row in  $(jf xr curl  -s -XGET /api/v2/watches --server-id="${source}" | jq -r '.[] | @base64'); do
    data=$(echo "${row}" | base64 --decode)
    watchname=$(echo $data | cut -d ":" -f 4 | cut -d "," -f 1 | xargs)
    echo "Watch Name ===> $watchname <==="
    jf xr curl -XPOST /api/v2/watches -H 'Content-Type: application/json' -d "${data}" --server-id="${target}"
    echo -e "\n"
done



### sample cmd to run - ./buildMigrate.sh 