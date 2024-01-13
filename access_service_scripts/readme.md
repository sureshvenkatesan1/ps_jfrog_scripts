## Generate list of repositories and their associated permissions for an Artifactory user and group list

If you have a list of users   in **users-test.list** file and groups in **groups-unique.list** file then you can 
generate the repo and permission list using below script 
( taken from [GetReposAssignedToUsers.sh](GetReposAssignedToUsers.sh) that was in https://github.com/shivaraman83/security-entities-migration/blob/main/GetReposAssignedToUsers.sh )

```text
cat users-test.list |  while read line
do
  USER=$(echo $line)
  echo "Getting permissions for User $USER"
  curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/v2/security/permissions/users/$USER  >> $USER-PERMISSION-config.json
  cat $USER-PERMISSION-config.json | jq -r 'map(.repo.repositories) | flatten | unique | .[]' >> repositories-non-unique.list
 ##cat $USER-PERMISSION-config.json | jq -r 'map(.build.repositories) | flatten | unique | .[]' >> repositories-non-unique.list
  cat $USER-PERMISSION-config.json | jq -r '.[] | .name' >> permissions-non-unique.list
  cp repositories-non-unique.list users-repositories-non-unique.list
  rm  $USER-PERMISSION-config.json

  echo "Getting USER Details for User $USER"
  curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/security/users/$USER  >> $USER-config.json
  cat $USER-config.json | jq -r '.groups | flatten | unique | .[]' >> groups-non-unique.list
  rm $USER-config.json
done

echo "Looping of users-test.list is complete"

sort groups-non-unique.list | uniq >> groups-unique.list

echo "Sorting groups and making it unique is complete"
cat groups-unique.list |  while read line
do
  GROUP=$(echo $line)
 echo "Getting permissions for group $GROUP"
  curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/v2/security/permissions/groups/$GROUP  >> $GROUP-PERMISSION-config.json
  cat $GROUP-PERMISSION-config.json | jq -r 'map(.repo.repositories) | flatten | unique | .[]' >> repositories-non-unique.list
  cat $GROUP-PERMISSION-config.json | jq -r '.[] | .name' >> permissions-non-unique.list
  rm  $GROUP-PERMISSION-config.json
done

sort repositories-non-unique.list | uniq >> repositories-unique.list
sort permissions-non-unique.list | uniq >> permissions-unique.list


```
Now that you have the following files:
- users-test.list ( which is equivalent to "users_saml_internal_list.txt" in [createUser_SH_SaaS.sh](createUser_SH_SaaS.sh))
- groups-unique.list (  which is equivalent to "group_internal_list.txt" in [createGroup_SH_SaaS.sh](createGroup_SH_SaaS.sh))

Create the following in the target JFrog Platform Instance:
- users using [createUser_SH_SaaS.sh](createUser_SH_SaaS.sh) , 
- groups using [createGroup_SH_SaaS.sh](createGroup_SH_SaaS.sh) and 
- permissions using **permissions-unique.list**  (  which is equivalent to 
"permissions_list.txt" in [createPermissionTarget_SH_SaaS.sh](createPermissionTarget_SH_SaaS.sh))

- Next create the repos in **repositories-non-unique.list** in the target JPD using the
```text
semicolon_separated_list_of_repos=$(tr '\n' ';' < repositories-non-unique.list)

jf rt transfer-config-merge source-server target-server --include-repos "$semicolon_separated_list_of_repos" --include-projects ""

```

or
using https://github.com/shivaraman83/security-entities-migration/blob/main/create-repos.sh

Note: The "--include-projects" will transfer only the project and not the entities associated with the project , like environments , roles etc.

Note: All these scripts use the old security APIs.
The scripts that use the newer /access/api/v2 scripts to manage users, groups, permissions are under  
[improbable_uses_access_v2_apis](improbable_uses_access_v2_apis) 


