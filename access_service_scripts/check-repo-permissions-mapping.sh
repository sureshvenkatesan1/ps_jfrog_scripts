#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

### Exit the script on any failures
set -eo pipefail
set -e
set -u

### Get Arguments
SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://bankdata.jfrog.io}"
USER_TOKEN="${2:?please provide the identity token}"

permissions_target_list="permissions_list.txt"
local_replication_repos_list="../local_replication_repos_list.txt"
remote_replication_repos_list="../remote_replication_repos_list.txt"

rm -rf permissionsList/ ; mkdir permissionsList ; cd permissionsList/

curl -XGET -H "Authorization: Bearer $USER_TOKEN" "$SOURCE_JPD_URL/artifactory/api/security/permissions" -s | jq -rc '.[] | .name' | grep -v "INTERNAL" | sort | sed 's/ /%20/g' > $permissions_target_list

echo -e "\nPERMISSIONS LIST"
while IFS= read -r permissions; do
    echo -e "\nGetting JSON for Group ==> $permissions"
    curl -XGET -H "Authorization: Bearer $USER_TOKEN" "$SOURCE_JPD_URL/artifactory/api/security/permissions/$permissions" -s > "$permissions.json"
    repoList=$(cat "$permissions.json" | jq -r '.repositories| .[]' | tr '\n' , | rev | cut -c2- | rev)
    echo $repoList
    if [ -z "$repoList" ]; then
            echo -e "  ****PERMISSION $permissions has EMPTY REPO LIST"
            echo "$permissions" >> "empty_repos.txt"
    else 
        if echo "$repoList" | grep -q "ANY LOCAL"; then
            echo "Permission with ANY LOCAL - $permissions PERMISSION" >> "any_local_permissions.txt"
        fi
        if echo "$repoList" | grep -q "ANY REMOTE"; then
            echo "Permission with ANY REMOTE - $permissions PERMISSION" >> "any_remote_permissions.txt"
        fi
        if echo "$repoList" | grep -q "ANY"; then
            echo "Permission with ANY - $permissions PERMISSION" >> "any_permissions.txt"
        fi
        while IFS= read -r localrepo; do
                if echo "$repoList" | grep -q "$localrepo"; then
                    echo "LOCAL Repo $localrepo is present in $permissions PERMISSION" >> "local_repos_permissions.txt"
                fi
        done < $local_replication_repos_list
        while IFS= read -r remoterepo; do
                if echo "$repoList" | grep -q "$remoterepo"; then
                    echo "REMOTE Repo $remoterepo is present in $permissions PERMISSION" >> "remote_repos_permissions.txt"
                fi
        done < $remote_replication_repos_list
    fi
done < $permissions_target_list

echo -e "\nPermission Target with NO REPOS added :-" ; cat empty_repos.txt || true
echo -e "\nLOCAL :- " ; cat local_repos_permissions.txt || true
echo -e "\nREMOTE:- " ; cat remote_repos_permissions.txt || true
echo -e "\nANY LOCAL PERMISSIONS :- " ; cat any_local_permissions.txt | sort | uniq || true
echo -e "\nANY REMOTE PERMISSIONS :- " ; cat any_remote_permissions.txt | sort | uniq || true
echo -e "\nANY PERMISSIONS :- " ; cat any_permissions.txt | sort | uniq || true

### sample cmd to run - ./check-repo-permissions-mapping.sh https://bankdata.jfrog.io ****
