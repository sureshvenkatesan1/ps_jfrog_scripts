#! /bin/bash
JPDID="${1:?please enter JPD ID. ex - source-server}"
remoteurl="${2:?please remote jpd URL ex - https://smartremotejpd.jfrog.io}"
uname="${3:?please enter username with read access to remote repo ex - migrationuser}"
passwd="${4:?please enter passwd/token  ex - password/token}"
mkdir -p virt
rm -f virt/*.json
echo '{}' > repos.json
echo "Creating Virtual To Local Repo mapping"
for art in $(jf rt curl -s -XGET '/api/repositories?type=virtual' --server-id  $JPDID | jq -r '.[] | .key');
do
    jf rt curl -s -XGET "/api/v2/repositories/$art" --server-id=$JPDID  > virt/$art.json
    repolist=$(cat virt/$art.json| jq '.repositories')
    jq ". + {\"$art\":$repolist}" repos.json > tmp.json && mv tmp.json repos.json
done

pkgtypelist=("bower" "chef" "conan" "docker" "go" "oci" "nuget" "npm" "composer" "puppet" "gems" "swift")
for art in $(jf rt curl -s -XGET '/api/repositories?type=local' --server-id  $JPDID | jq -r '.[] | .key');
do
    jf rt curl -s -XGET "/api/v2/repositories/$art" --server-id=$JPDID  |jq '.rclass = "local"' > $art.json
    pkgType=$(cat $art.json|jq -r '.packageType')
    repoName=$(cat $art.json|jq -r '.key')
    cat $art.json | jq '.key += "-local"' > ${art}-local.json
    if [[ " ${pkgtypelist[@]} " =~ " $pkgType " ]]; then
        url="$remoteurl/artifactory/api/$pkgType/$repoName"
        jq -n "{\"key\": \"${repoName}-remote\", \"rclass\": \"remote\", \"packageType\": \"$pkgType\",\"url\" : \"$url\",\"username\":\"$uname\", \"password\":\"$passwd\"}" > $art-remote.json
    elif [ "$pkgType" = "cocoapods" ]; then
        url="$remoteurl/artifactory/api/pods/$repoName"
        jq -n "{\"key\": \"${repoName}-remote\", \"rclass\": \"remote\", \"packageType\": \"$pkgType\",\"url\" : \"$url\",\"username\":\"$uname\", \"password\":\"$passwd\"}" > $art-remote.json
    elif [[ "$pkgType" == 'pypi' ]]; then
        pyPIRegistryUrl="$remoteurl/artifactory/api/pypi/$repoName"
        url="$remoteurl/artifactory/$repoName"
        jq -n "{\"key\": \"${repoName}-remote\", \"rclass\": \"remote\", \"packageType\": \"$pkgType\",\"url\" : \"$url\",\"pyPIRegistryUrl\" : \"$pyPIRegistryUrl\",\"username\":\"$uname\", \"password\":\"$passwd\"}" > $art-remote.json
    else
        url="$remoteurl/artifactory/$repoName"
        jq -n "{\"key\": \"${repoName}-remote\", \"rclass\": \"remote\", \"packageType\": \"$pkgType\",\"url\" : \"$url\",\"username\":\"$uname\", \"password\":\"$passwd\"}" > $art-remote.json
    fi
    echo "Creating Local Repo ${art}-local"
    jf rt curl  -H 'Content-Type: application/json' -XPUT "/api/repositories/${art}-local"  -T ${art}-local.json --server-id=$JPDID
    echo "Creating Remote Repo ${art}-remote"
    jf rt rc $art-remote.json --server-id=$JPDID
    jq -n "{\"key\": \"${repoName}\", \"rclass\": \"virtual\", \"packageType\": \"$pkgType\",\"repositories\": [\"${art}-local\", \"$art-remote\"],\"defaultDeploymentRepo\": \"${art}-local\"}" > $art-virt.json
    echo "Deleting old Local Repo ${art}"
    jf rt repo-delete $art --quiet --server-id=$JPDID
    echo "Creating Virtual Repo ${art}"
    jf rt curl  -H 'Content-Type: application/json' -XPUT "/api/repositories/${art}"  -T ${art}-virt.json --server-id=$JPDID

    for virtrepo in $( jq -r --arg search "$art" 'to_entries[] | select(.value[] == $search) | .key' repos.json);
    do
        echo "$art - $virtrepo"
        cat virt/${virtrepo}.json |  jq ".repositories += [\"$art-local\",\"$art-remote\"]" | jq ".defaultDeploymentRepo = \"$art-local\"" > virt/${virtrepo}-updated.json
        echo "Updating Virtual Repo ${virtrepo}"
        jf rt curl  -H 'Content-Type: application/json' -XPOST "/api/repositories/${virtrepo}"  -T virt/${virtrepo}-updated.json --server-id=$JPDID
    done
done
