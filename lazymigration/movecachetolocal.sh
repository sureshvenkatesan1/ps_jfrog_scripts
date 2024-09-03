#! /bin/bash

######################################
# Update Below Variables             #
######################################
JPDID="local"
remoteurl="https://myremoterepo.jfrog.io" 

#######################################
remotejson=$(jf rt curl 'api/repositories?type=remote' -s  --server-id $JPDID)
for repo in $(echo $remotejson | jq -r ".[] | select(all(.url ;contains(\"$remoteurl\")))|.key");
do
   pkgtype=$(echo $remotejson |  jq -r ".[]| select(.key == \"$repo\") | .packageType"| tr '[:upper:]' '[:lower:]')
   reponame=$(echo $repo | sed 's/-remote$//')
   # echo -n $reponame
   case "$pkgtype" in
      "docker")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.jfrog/*' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.jfrog/*' --threads 16 --server-id=$JPDID
         ;;
      "rpm")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions 'repodata/*' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions 'repodata/*' --threads 16 --server-id=$JPDID
         ;;
      "helm")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions 'index.yaml' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions 'index.yaml' --threads 16 --server-id=$JPDID
         ;;
      "npm")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.npm/*' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.npm/*' --threads 16 --server-id=$JPDID
         ;;
      "pypi")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.pypi/*' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.pypi/*' --threads 16 --server-id=$JPDID
         ;;
      "conan")
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.conan/*' --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/ --exclusions '.conan/*' --threads 16 --server-id=$JPDID
         ;;
      *)
         echo "jf rt mv ${repo}-cache/* ${reponame}-local/  --threads 16 --server-id=$JPDID"
         jf rt mv ${repo}-cache/* ${reponame}-local/  --threads 16 --server-id=$JPDID
         ;;
   esac
done

