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

if [ $# -lt 2 ]; then
    echo "Usage: $0 <source_server_name> <target_server_name> [diff_for_buildname] [diff_for_buildnumber] [createdafter]"
    exit 1
fi

source_server_name=$1
target_server_name=$2
diff_for_buildname=${3:-false}
diff_for_buildnumber=${4:-true}
createdafter=${5:-""}

sourceHealthCheck=$(jf rt ping --server-id=$source_server_name)
targetHealthCheck=$(jf rt ping --server-id=$target_server_name)
echo -e "Health Check for Source Server = $sourceHealthCheck"
echo -e "Health Check for Target Server = $targetHealthCheck"
echo -e ""

interateBuilds () {
    echo -e "\nDownloading from $source_server_name artifactory for buildname = $buildname and Build Number = $buildnumberiterate"
    jf rt curl -s -XGET "/api/build/$buildname/$buildnumberiterate" --server-id=$source_server_name > buildinfo-$buildname-$buildnumberiterate.json
    echo -e "Saving Build Info with Build Name = $buildname and Build Number = $buildnumberiterate to v7 artifactory..."
    cat buildinfo-$buildname-$buildnumberiterate.json | sed '$d' | sed '2d' | jq 'del(.uri)' | sed '$s/\,//g' | jq '.' > updated-bi-$buildname-$buildnumberiterate.json
    echo -e "Uploading to $target_server_name artifactory"
    jf rt curl -XPUT "/api/build" -H "Content-Type: application/json" --server-id=$target_server_name -T "updated-bi-$buildname-$buildnumberiterate.json"
    echo -e "Build Info with BuildName = $buildname and BuildNumber = $buildnumberiterate uploaded successfully"
}

rm -rf *.txt
rm -rf *.json

if [ -z "$createdafter" ]; then
      if $diff_for_buildname ; then 
        jf rt curl -s -XGET "/api/build" --server-id=$source_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > t1.txt
        jf rt curl -s -XGET "/api/build" --server-id=$target_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > t2.txt
        diff -u <(sort t2.txt) <(sort t1.txt) --suppress-common-lines | grep '^+' | sed 1d | sed 's/^.//' > buildnames.txt
    else
        jf rt curl -s -XGET "/api/build" --server-id=$source_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > buildnames.txt
    fi
else
      echo -e "\nCreated After Date is set to ==> $createdafter"
      echo "jf rt curl /api/search/aql -H 'Content-Type:text/plain' -s -d 'builds.find({\"created\" : {\"\$gte\" : \"$createdafter\"}})' --server-id=$source_server_name | jq '.results[] | .\"build.name\"+ \"/\" +.\"build.number\"' | sort -r | uniq | sed 's/\"//g' > buildNameAndNumber.txt"
      cmd="jf rt curl /api/search/aql -H 'Content-Type:text/plain' -s -d 'builds.find({\"created\" : {\"\$gte\" : \"$createdafter\"}})' --server-id=$source_server_name | jq '.results[] | .\"build.name\"+ \"/\" +.\"build.number\"' | sort -r | uniq | sed 's/\"//g' > buildNameAndNumber.txt"
      eval "$cmd"
      while IFS= read -r data; do
        buildname=$(echo "$data" | cut -d '/' -f1)
        buildnumberiterate=$(echo "$data" | cut -d '/' -f2)
        interateBuilds $buildname $buildnumberiterate
      done < "buildNameAndNumber.txt"
fi


while IFS= read -r buildname; do
    if $diff_for_buildnumber ; then 
        echo -e "\nChecking Diff for $buildname.."
        jf rt curl -s -XGET "/api/build/$buildname" --server-id=$source_server_name | jq .buildsNumbers | jq -r '.[].uri' | sed 's/\///g' > $source_server_name-blnum.txt
        jf rt curl -s -XGET "/api/build/$buildname" --server-id=$target_server_name | jq .buildsNumbers | jq -r '.[].uri' | sed 's/\///g' > $target_server_name-blnum.txt
        diff -u <(sort $target_server_name-blnum.txt) <(sort $source_server_name-blnum.txt) --suppress-common-lines | grep '^+' | sed 1d | sed 's/^.//' > $buildname-buildnumbers.txt
    else
        echo -e "\nFetching build numbers for $buildname"
        jf rt curl -s -XGET "/api/build/$buildname" --server-id=$source_server_name | jq .buildsNumbers | jq -r '.[].uri' | sed 's/\///g' > $buildname-buildnumbers.txt
    fi
    while IFS= read -r buildnumberiterate; do
        interateBuilds $buildname $buildnumberiterate
    done < "$buildname-buildnumbers.txt"
done < "buildnames.txt"

#rm -rf *.txt

### sample cmd to run - ./buildMigrate.sh 