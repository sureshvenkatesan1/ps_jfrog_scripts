#! /bin/bash
 
#Get Arguments
SOURCE_ID="${1:?Enter source artifactory server ID}"
TARGET_ID="${2:?Enter target artifactory server ID}"
TRANSFERONLY="${3:?Transfer or View, valid options 'yes' or 'no'}"
case "$TRANSFERONLY" in
    yes)
        ;;
    no)
        ;;
    *)
        echo "Wrong 3rd Parameter, 3rd parameter value should be yes or no"
        exit 1
        ;;
esac

runtask() {
jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $SOURCE_ID --data "items.find({\"repo\": \"$1\"}).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | sed  's/\.\///' > a
jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $TARGET_ID --data "items.find({\"repo\": \"$1\"}).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | sed  's/\.\///' > b
join -v1  <(sort a) <(sort b) | sed -re 's/,[[:alnum:]]+"$/"/g' |sed 's/"//g' > c
#cat c | xargs -I {} echo "jf rt dl \"$1/{}\" . --server-id local ; jf rt u \"{}\" \"$1/{}\" --server-id local1 ; rm -f \"{}\" "
if [ "${TRANSFERONLY}" == "no" ]; then
        echo "-------------------------------------------------"
        echo "Files diff from source - Repo [$1]"
        echo "-------------------------------------------------"
        cat -b c
elif [ "${TRANSFERONLY}" == "yes" ]; then
while IFS= read -r line
do
 echo "jf rt dl \"$1/$line\" . --server-id $SOURCE_ID ; jf rt u \"$line\" \"$1/$line\" --server-id $TARGET_ID ; rm -f \"$line\" "
 #jf rt dl \"$1/$line\" . --server-id $SOURCE_ID ; jf rt u \"$line\" \"$1/$line\" --server-id $TARGET_ID ; rm -f \"$line\"
done < "c"
else 
  echo "Wrong 3rd Parameter, 3rd parameter value should be yes or no"
fi 
rm -f a b c
}
 
 
for art in $(jf rt curl -s -XGET /api/repositories --server-id  $SOURCE_ID | jq -r '.[] | .key');
do
   runtask $art
done
