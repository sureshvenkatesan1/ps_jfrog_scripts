

SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://proservices.jfrog.io}"
JPD_AUTH_TOKEN="${2:?ID token . ex - Identity token}"


rm repositories*.list
rm users-repo*.list
rm groups*.list
rm permissions*.list
rm to-delete*.list
rm all-users.list
rm all-users.json
rm to-delete*.list
rm all*.list
##cat users-test.list
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


echo "Getting all the users"
curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/security/users >> all-users.json
cat all-users.json | jq -r '.[] | .name' >> all-users.list
rm  all-users.json
sort all-users.list >> all-users-sorted.list
rm all-users.list
echo "Sorted all the users"
sort users-test.list | uniq >> users-test-sorted.list
echo "sorted the input list"
echo "Generating the user deletion file"
fgrep -vf users-test.list all-users-sorted.list > to-delete-users.list
#diff users-test.list all-users-sorted.list|grep ">"|cut -c 3- > to-delete-users.list

echo "Getting all the Groups"
curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/security/groups >> all-groups.json
cat all-groups.json | jq -r '.[] | .name' >> all-groups.list
rm all-groups.json
sort all-groups.list | uniq >> all-groups-sorted.list
rm all-groups.list
echo "Sorted all the groups"
echo "Generating the groups deletion file"
#fgrep -vf groups-unique.list all-groups-sorted.list > to-delete-groups.list
diff groups-unique.list all-groups-sorted.list|grep ">"|cut -c 3- > to-delete-groups.list


echo "Getting all the Permissions"
curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SOURCE_JPD_URL/artifactory/api/security/permissions >> all-permissions.json
cat all-permissions.json | jq -r '.[] | .name' >> all-permissions.list
rm all-permissions.json
sort all-permissions.list | uniq >> all-permissions-sorted.list
rm all-permissions.list
echo "Sorted all the permissions"
echo "Generating the permissions deletion file"
#fgrep -vf permissions-unique.list all-permissions-sorted.list > to-delete-permissions.list
diff permissions-unique.list all-permissions-sorted.list|grep ">"|cut -c 3- > to-delete-permissions.list



echo "Below is the output"

wc -l repositories-unique.list

echo "Groups  reconciliation"
wc -l all-groups-sorted.list
wc -l groups-unique.list
wc -l to-delete-groups.list

echo "Permissions reconciliation"
wc -l all-permissions-sorted.list
wc -l permissions-unique.list
wc -l to-delete-permissions.list

echo "Users reconciliation"
wc -l all-users-sorted.list
wc -l users-test.list
wc -l to-delete-users.list
