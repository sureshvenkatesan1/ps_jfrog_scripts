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

source_server_name=ramkannan
target_server_name=psinaz

sourceHealthCheck=$(jf rt ping --server-id=$source_server_name)
targetHealthCheck=$(jf rt ping --server-id=$target_server_name)
echo -e "Health Check for Source Server = $sourceHealthCheck"
echo -e "Health Check for Target Server = $targetHealthCheck"
echo -e ""

rm -R -- */

jf rt cl "/api/repositories?type=local" --server-id=$source_server_name -s | jq -r '.[].key' > repos_list.txt

while IFS= read -r reponame; do
    echo -e "\n\n##### Performing for $reponame #####"
    mkdir $reponame
    cd $reponame/
    echo "Downloading $reponame from $source_server_name server..."
    jf rt dl "$reponame" --server-id=$source_server_name
    echo "Uploading $reponame to $target_server_name server..."
    jf rt u "*" "$reponame" --server-id=$target_server_name
    cd ..
    rm -rf $reponame
    echo -e "Completed $reponame ..."
done < "repos_list.txt"
