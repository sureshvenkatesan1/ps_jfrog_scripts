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
    echo "Usage: $0 <source_server_name> <target_server_name>"
    exit 1
fi

source_server_name=$1
target_server_name=$2

rm -rf *.txt
rm -rf *.json

jf rt curl -s -XGET "/api/build" --server-id=$source_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > t1.txt
jf rt curl -s -XGET "/api/build" --server-id=$target_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > t2.txt
diff -u <(sort t2.txt) <(sort t1.txt) --suppress-common-lines | grep '^-' | sed 1d | sed 's/^.//' > buildnames-diff-delete.txt
jf rt curl -s -XGET "/api/build" --server-id=$target_server_name | jq .builds | jq -r '.[].uri' | sed 's/\///g' > buildnames.txt
while IFS= read -r buildname; do
    echo -e "\nChecking Diff for $buildname.."
    jf rt curl -s -XGET "/api/build/$buildname" --server-id=$source_server_name | jq .buildsNumbers | jq -r '.[].uri' | sed 's/\///g' > $source_server_name-blnum.txt
    jf rt curl -s -XGET "/api/build/$buildname" --server-id=$target_server_name | jq .buildsNumbers | jq -r '.[].uri' | sed 's/\///g' > $target_server_name-blnum.txt
    diff -u <(sort $target_server_name-blnum.txt) <(sort $source_server_name-blnum.txt) --suppress-common-lines | grep '^-' | sed 1d | sed 's/^.//' > $buildname-buildnumbers-delete.txt
done < "buildnames.txt"

while true; do
    read -p "Proceed with Build Deletion (y/n) ? " hachoice
    case "$hachoice" in 
        Y|y) echo -e "\nDelete = Yes" ; break;;
        N|n ) echo -e "\Delete = No" ; break;;
        * ) echo "invalid";;
    esac
done

if [[ "$hachoice" =~ ^[Yy]$ ]]; then
    echo "Deleting builds.."
    while IFS= read -r buildname; do
        while IFS= read -r buildnumberiterate; do
            echo -e "$buildname/$buildnumberiterate"
            #echo "jf rt curl -XDELETE "/api/build/$buildname?buildNumbers=$buildnumberiterate" --server-id=$target_server_name"
            #jf rt curl -XDELETE "/api/build/$buildname?buildNumbers=$buildnumberiterate" --server-id=$target_server_name
        done < "$buildname-buildnumbers-delete.txt"
    done < "buildnames.txt"
    echo "Deleting Completed.."
fi

#rm -rf *.txt

### sample cmd to run - ./buildDiffDelete.sh 