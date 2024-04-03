#! /bin/bash

# JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this  code   solely in connection with your use of a JFrog product or service. This  code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service. 

# export MYTOKEN=
# usage: bash ./jpd-data-collection.sh https://psemea.jfrog.io  ${MYTOKEN} sh/saas [true/false]

### sample cmd to run - bash ./jpd-data-collection.sh https://ramkannan.jfrog.devopsacc.team **** sh/saas

SOURCE_JPD_URL="${1:?please enter JPD URL. ex - https://ramkannan.jfrog.io}"
JPD_TOKEN="${2:?please provide the identity token}"
TYPE="${3:?please let us know the jpd is saas or sh (for self-hosted)}"
DETAILS="${4:-false}"  # Default value is false if not provided

REPORT_FILE="jpd-data-collection.txt"


echo -e "=====> JFrog Platform Data Collection <=====" > "$REPORT_FILE"

jf c rm source-jpd --quiet

jf c add source-jpd --url="${SOURCE_JPD_URL}" --access-token="${JPD_TOKEN}" --interactive=false

jf c use source-jpd

echo -e "\nPing System.."
jf rt curl -XGET /api/system/ping
echo -e "\nPing Completed..\n"

echo -e "\nSystem Configuration Print.."
#jf rt curl -XGET /api/system/configuration

if [ "$TYPE" = "saas" ]; then
    echo -e "\nGetting License Info.."
    license=$(jf rt curl -XGET /api/system/license -s)
    echo -e $license
    echo -e "License:\n $license" >> "$REPORT_FILE"
    echo -e "\n"
elif [ "$TYPE" = "sh" ]; then
    echo -e "\nGetting Current URL.."
    urlBase=$(jf rt curl -XGET /api/system/configuration -s | grep -i urlBase)
    echo -e $urlBase
    echo -e "urlBase:\n $urlBase" >> "$REPORT_FILE"

    echo -e "\nGetting License Info.."
    license=$(jf rt curl -XGET /api/system/licenses -s)
    echo -e $license
    echo -e "License:\n $license" >> "$REPORT_FILE"

    echo -e "\nGetting Webserver Info.."
    webserver=$(jf rt curl -XGET /api/system/configuration/webServer -s)
    echo -e $webserver
    echo -e "webserver:\n $webserver" >> "$REPORT_FILE"
else
    echo -e "\n Invalid Type. Run with sh / saas"
fi

echo -e "\nGetting Current version of Artifactory.."
art_version=$(jf rt curl -XGET /api/system/version -H "Content-Type: application/json" -s | jq .version | xargs)
echo -e $webserver
echo -e "\nCurrent version of Artifactory = $art_version\n" >> "$REPORT_FILE"

echo -e "\nGetting Package Types currently used.."
echo -e "\nPackage Types currently used :" >> "$REPORT_FILE"
jf rt curl -s -XGET /api/repositories | jq -r '.[].packageType' | sort | uniq | sed 's/^/===> /' >> "$REPORT_FILE"

# Function to get entity names sorted in ascending order
get_entity_names() {
    local entity_type="$1"
    local entity_url="$2"
    echo -e "\n$entity_type:" >> "$REPORT_FILE"
    entity_names=$(jf rt curl -s -XGET "$entity_url" | jq -r '.[].key')
    sorted_entity_names=$(echo "$entity_names" | sort)
    count=$(echo "$sorted_entity_names" | wc -l)
    echo "===> Count: $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        echo "$sorted_entity_names" >> "$REPORT_FILE"
    fi
}

echo -e "\nGetting Repositories.."
echo -e "\nRepositories : " >> "$REPORT_FILE"
get_entity_names "Local Repositories" "/api/repositories?type=local"
get_entity_names "Remote Repositories" "/api/repositories?type=remote"
get_entity_names "Virtual Repositories" "/api/repositories?type=virtual"
get_entity_names "Federated Repositories" "/api/repositories?type=federated"

echo -e "\nGetting Storage Info.."
echo -e "\nStorage Info : " >> "$REPORT_FILE"
binariesCount=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.binariesCount | xargs)
binariesSize=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.binariesSize | xargs)
artifactsCount=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.artifactsCount | xargs)
artifactsSize=$(jf rt curl -XGET /api/storageinfo -H "Content-Type: application/json" -s | jq .binariesSummary.artifactsSize | xargs)
echo -e "===> Binary Count = $binariesCount" >> "$REPORT_FILE"
echo -e "===> Binary Size = $binariesSize" >> "$REPORT_FILE"
echo -e "===> Artifact Count = $artifactsCount" >> "$REPORT_FILE"
echo -e "===> Artifact Size = $artifactsSize" >> "$REPORT_FILE"

echo -e "\nGetting Largest file size.."
largestFileSize=$(jf rt curl -XPOST api/search/aql -H "Content-Type: text/plain" -d 'items.find({"name" : {"$match":"*"}}).include("size").sort({"$desc" : ["size"]}).limit(1)' -s | jq '.results | .[] | .size')
echo -e "\nLargest File size = $largestFileSize" >> "$REPORT_FILE"
if (( largestFileSize > 25000000000 )); then
    echo -e "NOTE: Contact JFrog Support to increase the size limit" >> "$REPORT_FILE"
fi

echo -e "\nGetting Docker Repositories Name Matching . or _ .."
echo -e "\nDocker Repositories Name Matching . or _  :-" >> "$REPORT_FILE"
jf rt curl -s -XGET "/api/repositories?packageType=docker" | jq -r '.[].key' | grep -F '.' >> "$REPORT_FILE"
jf rt curl -s -XGET "/api/repositories?packageType=docker" | jq -r '.[].key' | grep -F '_' >> "$REPORT_FILE"

get_acess_entity_names() {
    local entity_type="$1"
    local entity_url="$2"
    local entity_filter="$3"
    echo -e "\n$entity_type:" >> "$REPORT_FILE"
    # Print the curl command
    # echo "curl -XGET -H \"Authorization: Bearer ${JPD_TOKEN}\" \"${SOURCE_JPD_URL}${entity_url}\" -s | \
    #         jq -r "${entity_filter}" | sort"


    entity_names=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}${entity_url}" -s | \
                    jq -r "${entity_filter}" | sort)


    count=$(echo "$entity_names" | wc -l)
    echo "===> Count: $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        echo "$entity_names" >> "$REPORT_FILE"
    fi

}

echo -e "\nGetting Access Entities .."
echo -e "\nAccess Entities:" >> "$REPORT_FILE"
get_acess_entity_names "Users" "/access/api/v2/users" "(.users // [])[] | .username // empty | select(. != null)"
get_acess_entity_names "Groups" "/access/api/v2/groups" "(.groups // [])[] | .group_name // empty | select(. != null)"
get_acess_entity_names "Permissions" "/access/api/v2/permissions"  "(.permissions // [])[] | .name // empty | select(. != null)"
get_acess_entity_names "Tokens" "/access/api/v1/tokens"  "(.tokens // [])[] | .token_id // empty | select(. != null)"

echo -e "\nGetting Projects .."
echo -e "\nProjects:" >> "$REPORT_FILE"
projects=$(curl -XGET -H "Authorization: Bearer ${JPD_TOKEN}" "${SOURCE_JPD_URL}/access/api/v1/projects" -s | jq -r '.[].project_key')
sorted_projects=$(echo "$projects" | sort)
count=$(echo "$sorted_projects" | wc -l)

if (( count > 0 )); then
    echo -e "\nProject Used = YES" >> "$REPORT_FILE"
    echo -e "===> Count: $count" >> "$REPORT_FILE"

    if [ "$DETAILS" = "true" ]; then
        echo "$sorted_projects" >> "$REPORT_FILE"
    fi
else
    echo -e "\nProject Used = NO" >> "$REPORT_FILE"
fi

echo -e "\nGetting Builds .."
echo -e "\nBuilds:" >> "$REPORT_FILE"
# builds=$(jf rt curl -s -XGET "/api/build" | jq -r '.builds[].uri')
builds=$(jf rt curl -s -XGET "/api/build" | jq -r  "(.builds // [])[] | .uri // empty | select(. != null)"  | sort)
count=$(echo "$builds" | wc -l)
echo -e "===> Count: $count" >> "$REPORT_FILE"

if [ "$DETAILS" = "true" ]; then
    echo "$builds" >> "$REPORT_FILE"
fi
# Iterate over each project key
while IFS= read -r projectKey; do
    # URL encode the project key
    # encoded_projectKey=$(printf "%s" "$projectKey" | jq -s -R -r @uri)
    # Get builds for the current project
    # echo "jf rt curl -s -XGET \"/api/build?project=${projectKey}\""
    #'.builds[].uri'
    builds=$(jf rt curl -s -XGET "/api/build?project=${projectKey}" | jq -r  "(.builds // [])[] | .uri // empty | select(. != null)"  | sort)
    count=$(echo "$builds" | wc -l)
    # Print project key and associated builds to the report file
    echo -e "\n    Project: $projectKey" >> "$REPORT_FILE"
    echo "                 ===> Count: $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        for build in $builds; do
            echo "                 $build" >> "$REPORT_FILE"
        done
    fi

done <<< "$sorted_projects"

echo -e "\nProperty Sets : "

echo -e "\nFetching Property Sets : " >> "$REPORT_FILE"
propertySets=$(jf rt curl "api/propertysets" -s | jq -r  ".[] | .name // empty | select(. != null)"  | sort)
count=$(echo "$propertySets" | wc -l)
echo -e "===> PropertySets Count = $count" >> "$REPORT_FILE"
if [ "$DETAILS" = "true" ]; then
    echo "$propertySets" >> "$REPORT_FILE"
fi


echo -e "\n===> XRAY <===" >> "$REPORT_FILE"
echo -e "\nGetting XRAY Details :-\n"
xrayConfig=$(jf rt curl "api/xrayRepo/getIntegrationConfig" -s | jq .)
echo -e $xrayConfig
echo -e "xrayConfig:\n $xrayConfig" >> "$REPORT_FILE"

# Extract xrayEnabled property from the response
xrayEnabled=$(echo "$xrayConfig" | jq -r .xrayEnabled)
echo -e "===> XRAY Enabled = $xrayEnabled" >> "$REPORT_FILE"

if [ "$xrayEnabled" = "true" ]; then
    echo -e "\nXray Watches:" >> "$REPORT_FILE"
    xray_watches=$(jf xr curl -s -XGET "api/v2/watches" | jq -r '.[].general_data.name')
    sorted_xray_watches=$(echo "$xray_watches" | sort)
    count=$(echo "$sorted_xray_watches" | wc -l)
    echo -e "===> XRAY Watch Count = $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        echo "$sorted_xray_watches" >> "$REPORT_FILE"
    fi


    echo -e "\nXray Policies:" >> "$REPORT_FILE"
    xray_policies=$(jf xr curl -s -XGET "api/v2/policies" | jq -r '.[].name')
    sorted_xray_policies=$(echo "$xray_policies" | sort)
    count=$(echo "$sorted_xray_policies" | wc -l)
    echo -e "===> XRAY Policies Count = $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        echo "$sorted_xray_policies" >> "$REPORT_FILE"
    fi


    echo -e "\nXray IgnoreRules IDs:" >> "$REPORT_FILE"
    xray_ignore_rules=$(jf xr curl -s -XGET api/v1/ignore_rules | jq -r '.data[].id')
    sorted_xray_ignore_rules=$(echo "$xray_ignore_rules" | sort)
    count=$(echo "$sorted_xray_ignore_rules" | wc -l)
    echo -e "===> XRAY IgnoreRules Count = $count" >> "$REPORT_FILE"
    if [ "$DETAILS" = "true" ]; then
        echo "$sorted_xray_ignore_rules" >> "$REPORT_FILE"
    fi

fi

echo -e "\n"

