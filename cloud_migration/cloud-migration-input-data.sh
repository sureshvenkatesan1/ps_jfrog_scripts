#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.devopsacc.team}"
USER_NAME="${2:?please provide the username in JPD . ex - admin}" 
JPD_TOKEN="${3:?please provide the identity token}"
REPORT_FILE="cloudmigration.txt"

echo -e "=====> Cloud Migration Info Collection <=====" > "$REPORT_FILE"

echo -e "Installing JF CLI"
#sudo curl -fL https://install-cli.jfrog.io | sh
jf --version

echo "Installing JQ"
#JQ=/usr/bin/jq ; curl https://stedolan.github.io/jq/download/linux64/jq > $JQ && chmod +x $JQ ; ls -la $JQ
jq --version

jf c rm cloud-migrate-data --quiet

jf c add cloud-migrate-data --url="${SOURCE_JPD_URL}" --access-token="${JPD_TOKEN}" --interactive=false

jf c use cloud-migrate-data

while true; do
    echo -e ""
    read -p "Artifactory Installation in onprem or cloud (onprem/cloud)? " localtype
    case "$localtype" in 
        cloud) echo "cloud"; break;;
        onprem ) echo "onprem"; break;;
        * ) echo "invalid";;
    esac
done

if [ "$localtype" = "cloud" ]; then
    echo -e "\nArtifactory Installed in Customer = Cloud environment" >> "$REPORT_FILE"
    read -p "Installation Type ( VM / Ansible / Docker / K8S): " installtype
    echo -e "Installation Type = $installtype" >> "$REPORT_FILE"
else
    echo -e "Artifactory Installed in Customer = OnPrem environment" >> "$REPORT_FILE"
fi

read -p "Enter the region in which you have install artifactory : " region
echo -e "\nArtifactory Region = $region" >> "$REPORT_FILE"

read -p "External Database used? If so, name the database : " extDB
echo -e "\nExternal Database Details = $extDB" >> "$REPORT_FILE"

read -p "External Binarystore used? If so, name the binarystore : " extDB
echo -e "\nExternal Database Details = $extDB" >> "$REPORT_FILE"

while true; do
    read -p "Is CleanUp Required before migration (y/n) ? " cleanUpChoice
    case "$cleanUpChoice" in 
        Y|y) echo -e "\nCleanUp Required = Yes" >> "$REPORT_FILE" ; break;;
        N|n ) echo -e "\nCleanUp Required = No" >> "$REPORT_FILE" ; break;;
        * ) echo "invalid";;
    esac
done

while true; do
    read -p "Is HA Setup Enabled (y/n) ? " hachoice
    case "$hachoice" in 
        Y|y) echo -e "\nHA Setup = Yes" >> "$REPORT_FILE" ; break;;
        N|n ) echo -e "\nHA Setup = No" >> "$REPORT_FILE" ; break;;
        * ) echo "invalid";;
    esac
done

if [[ "$hachoice" =~ ^[Yy]$ ]]; then
    read -p "How many instance in HA cluster? " ha_num
    echo -e "No. of nodes in HA Cluster = $ha_num" >> "$REPORT_FILE"
fi

art_version=$(jf rt curl -XGET /api/system/version -H "Content-Type: application/json" -s | jq .version | xargs)
echo -e "\nCurrent version of Artifactory = $art_version" >> "$REPORT_FILE"

echo -e "\nPackage Types currently used :" >> "$REPORT_FILE"
jf rt curl -s -XGET /api/repositories | jq -r '.[].packageType' | sort | uniq | sed 's/^/===> /' >> "$REPORT_FILE"

no_of_local=$(jf rt curl -s -XGET "/api/repositories?type=local" | jq -r '.[].key' | wc -l | xargs)
no_of_remote=$(jf rt curl -s -XGET "/api/repositories?type=remote" | jq -r '.[].key' | wc -l | xargs)
no_of_virtual=$(jf rt curl -s -XGET "/api/repositories?type=virtual" | jq -r '.[].key' | wc -l | xargs)
no_of_federated=$(jf rt curl -s -XGET "/api/repositories?type=federated" | jq -r '.[].key' | wc -l | xargs)

echo -e "\nNo of repositories : " >> "$REPORT_FILE"
echo -e "===> LOCAL = $no_of_local" >> "$REPORT_FILE"
echo -e "===> REMOTE = $no_of_remote" >> "$REPORT_FILE"
echo -e "===> VIRTUAL = $no_of_virtual" >> "$REPORT_FILE"
echo -e "===> FEDERATED = $no_of_federated" >> "$REPORT_FILE"

echo -e "\nStoage Info : " >> "$REPORT_FILE"
binariesCount=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.binariesCount | xargs)
binariesSize=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.binariesSize | xargs)
artifactsCount=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.artifactsCount | xargs)
artifactsSize=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.artifactsSize | xargs)
echo -e "===> Binary Count = $binariesCount" >> "$REPORT_FILE"
echo -e "===> Binary Size = $binariesSize" >> "$REPORT_FILE"
echo -e "===> Artifact Count = $artifactsCount" >> "$REPORT_FILE"
echo -e "===> Artifact Size = $artifactsSize" >> "$REPORT_FILE"

largestFileSize=$(jf rt curl -XPOST api/search/aql -H "Content-Type: text/plain" -d 'items.find({"name" : {"$match":"*"}}).include("size").sort({"$desc" : ["size"]}).limit(1)' -s | jq '.results | .[] | .size')
echo -e "\nLargest File size = $largestFileSize" >> "$REPORT_FILE"
if (( largestFileSize > 25000000000 )); then
    echo -e "NOTE: Contact JFrog Support to increase the size limit" >> "$REPORT_FILE"
fi

echo -e "\nDocker Repositories Matching . or _ Data :-" >> "$REPORT_FILE"
jf rt curl -s -XGET "/api/repositories?packageType=docker" | jq -r '.[].key' | grep -F '.' >> "$REPORT_FILE"
jf rt curl -s -XGET "/api/repositories?packageType=docker" | jq -r '.[].key' | grep -F '_' >> "$REPORT_FILE"

projectsdata=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}/access/api/v1/projects" -s | jq -r '.[].display_name' | wc -l | xargs)
if (( projectsdata > 0 )); then
    echo -e "\nProject Used = YES" >> "$REPORT_FILE"
    echo -e "No of Projects = $projectsdata" >> "$REPORT_FILE"
else 
    echo -e "\nProject Used = NO" >> "$REPORT_FILE"
fi

buildinfo=$(jf rt curl -s -XGET "/api/build" | jq .builds | jq -r '.[].uri' | wc -l | xargs)
if (( buildinfo > 0 )); then
    echo -e "\nBuild Info Available = YES" >> "$REPORT_FILE"
    echo -e "Total No of Build = $projectsdata" >> "$REPORT_FILE"
    read -p "Do you want to migrate BuildInfo? : " extDB
    while true; do
        read -p "Do you want to migrate BuildInfo? (y/n) ? " buildInfoChoice
        case "$buildInfoChoice" in 
            Y|y) echo -e "Build Info Migrate = Yes" >> "$REPORT_FILE" ; break;;
            N|n ) echo -e "Build Info Migrate = No" >> "$REPORT_FILE" ; break;;
            * ) echo "invalid";;
        esac
    done
else 
    echo -e "\nBuild Info Available = NO" >> "$REPORT_FILE"
fi

while true; do
    read -p "Any custom layouts added? (y/n) ? " customlayoutchoice
    case "$customlayoutchoice" in 
        Y|y) echo -e "\nCustom Layouts = Yes" >> "$REPORT_FILE" ; break;;
        N|n ) echo -e "\nCustom Layouts = No" >> "$REPORT_FILE" ; break;;
        * ) echo "invalid";;
    esac
done

if [[ "$customlayoutchoice" =~ ^[Yy]$ ]]; then
    while true; do
        read -p "Do you want to migrate the custom layouts? (y/n) ? " migrateCustomLayoutChoice
        case "$migrateCustomLayoutChoice" in 
            Y|y) echo -e "Migrate Custom Layouts = Yes" >> "$REPORT_FILE" ; break;;
            N|n ) echo -e "Migrate Custom Layouts = No" >> "$REPORT_FILE" ; break;;
            * ) echo "invalid";;
        esac
    done
fi

echo -e "\nAccess Federation : " >> "$REPORT_FILE"
usersCount=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}/access/api/v2/users" -s | jq .users | jq -r '.[].username' | wc -l | xargs)
groupsCount=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}/access/api/v2/groups" -s | jq .groups | jq -r '.[].group_name' | wc -l | xargs)
permissionsCount=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}/access/api/v2/permissions" -s | jq .permissions | jq -r '.[].name' | wc -l | xargs )
echo -e "===> Users Count = $usersCount" >> "$REPORT_FILE"
echo -e "===> Groups Count = $groupsCount" >> "$REPORT_FILE"
echo -e "===> Permissions Count = $permissionsCount" >> "$REPORT_FILE"

### sample cmd to run - ./cloud-migration-input-data.sh https://ramkannan.jfrog.devopsacc.team admin ****