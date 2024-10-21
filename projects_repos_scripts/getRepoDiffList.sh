#! /bin/bash

### Exit the script on any failures
set -eo pipefail
set -e
set -u

getList() {
    echo $1
    projectid="int"
    if [[ $TYPE == "all" ]]; then
        curl -X GET -H 'Content-Type: application/json' -u "${USER_NAME}":"${3}" "${1}"/artifactory/api/repositories?project=$projectid -s | jq -rc '.[] | .key' > "$reposfile"_"$2"
    else
        curl -X GET -H 'Content-Type: application/json' -u "${USER_NAME}":"${3}" "${1}/artifactory/api/repositories?project=$projectid&type=${TYPE}" -s | jq -rc '.[] | .key' > "$reposfile"_"$2"
    fi
    cat "$reposfile"_"$2"
    echo -e "\n"
}

getDiff() {
    python3 ../getDiffOfFiles.py -f1 $1 -f2 $2
}

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
DR_1_JPD_URL="${2:?please enter JPD URL. ex - http://35.209.109.173:8082}"
TYPE="${3:?please enter type of repo. ex - local, remote, virtual, federated, all}"
USER_NAME="${4:?please provide the username in JPD . ex - admin}"  ### common username across 3 JPD's
AUTH_TOKEN_JPD_1="${5:?please provide the user identity token for source}"
AUTH_TOKEN_JPD_2="${6:?please provide the user identity token for DR}"
DRY_RUN="${7:?set DRY_RUN to true if required to check only difference}"

### define variables
reposfile="repos-list-${TYPE}"

### Run the curl API 
rm -rf *.json
rm -rf *.txt

getList $SOURCE_JPD_URL "source.txt" $AUTH_TOKEN_JPD_1
getList $DR_1_JPD_URL "jpd1.txt" $AUTH_TOKEN_JPD_2

echo -e "Respository Difference between Source (truth set) and DR"
getDiff "$reposfile"_source.txt "$reposfile"_jpd1.txt
echo -e ""

if [ -f "sourcejpd1.txt" ]; then
    if [ $DRY_RUN == "true" ]; then
        echo -e "This is DRY_RUN Mode and Only diff will be printed !! \n"
    else 
        echo -e "DRY_RUN is false. Hence, performing creation on $TYPE Repositories \n"
        ./updateRepoDiffConfigJPD.sh sourcejpd1.txt $SOURCE_JPD_URL $DR_1_JPD_URL $USER_NAME $AUTH_TOKEN_JPD_1 "create" $AUTH_TOKEN_JPD_2
    fi
else 
    echo "No Diff of repos Found between Source and DR !!"
fi

### sample cmd to run - ./getRepoDiffList.sh https://ramkannan.jfrog.io http://35.209.109.173:8082 local admin **** **** true