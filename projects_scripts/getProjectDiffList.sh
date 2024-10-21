#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

getList() {
    echo $1
    curl -XGET -H "Authorization: Bearer ${3}" ${1}/access/api/v1/projects -s | jq 'sort' | jq -r '.[].project_key' > "$projectfile"_"$2"
    cat "$projectfile"_"$2"
    echo -e "\n" 
}

getDiff() {
    python3 ../getDiffOfFiles.py -f1 $1 -f2 $2
}

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
DR_1_JPD_URL="${2:?please enter JPD URL. ex - http://35.208.78.203:8082 }"
SOURCE_AUTH_TOKEN="${3:?please provide identity token }"  ### diffes across 3 JPD's
DR_1_JPD_AUTH_TOKEN="${4:?please provide identity token }"  ### diffes across 3 JPD's
DRY_RUN="${5:?set DRY_RUN to true if required to check only difference}"

### define variables
projectfile="project-list"

### Run the curl API 
rm -rf *.json
rm -rf *.txt

getList $SOURCE_JPD_URL "source.txt" $SOURCE_AUTH_TOKEN
getList $DR_1_JPD_URL "jpd1.txt" $DR_1_JPD_AUTH_TOKEN

echo -e "Project Difference between Source and JPD1"
getDiff "$projectfile"_source.txt "$projectfile"_jpd1.txt
echo -e "\n"

if [ -f "sourcejpd1.txt" ]; then
    if [ $DRY_RUN == "true" ]; then
        echo -e "This is DRY_RUN Mode and Only diff will be printed !! \n"
    else
        echo -e "DRY_RUN is false. Hence, performing creation of Projects \n"
        ./updateProjectDiffConfigJPD.sh sourcejpd1.txt $SOURCE_JPD_URL $DR_1_JPD_URL $SOURCE_AUTH_TOKEN $DR_1_JPD_AUTH_TOKEN
    fi
else 
    echo "No Diff of Projects Found between Source and JPD1 !!"
fi


### sample cmd to run - ./getProjectDiffList.sh https://ramkannan.jfrog.io http://35.208.78.203:8082 **** **** true