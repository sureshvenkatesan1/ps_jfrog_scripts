##################################################################################################
#  NOTE: Repo's, builds and RB must be synced before running watch sync
################################################################################################## 

source_id="${1:?Source ID for JF CLI.}"
target_id="${2:?Target ID for JF CLI.}"

# #### Sync all golbal Watches and no project polices.

for watchname in `jf xr curl -s -XGET api/v2/watches --server-id $source_id| jq -r '.[].general_data|select(.project_key|not) | .name'`
do
    jf xr curl -s -XGET api/v2/watches/$watchname --server-id $source_id > $watchname.json
    echo jf xr curl -XPOST -H "Content-Type: application/json" api/v2/watches -T $watchname.json --server-id $target_id
    jf xr curl -XPOST -H "Content-Type: application/json" api/v2/watches -T $watchname.json --server-id $target_id 
    echo ""
done


### Sync all  project policies. Make sure project sync is done before
for watchname in `jf xr curl -s -XGET api/v2/watches --server-id $source_id| jq -r '.[].general_data| select(.project_key) | .name'`
do
    
    jf xr curl -s -XGET api/v2/watches/$watchname --server-id $source_id> $watchname.json
    project_key=`cat $watchname.json | jq -r '.general_data.project_key'`
    cat $watchname.json | jq -r 'del(.general_data.project_key)' > new_$watchname.json
    echo jf xr curl -XPOST -H "Content-Type: application/json" api/v2/watches?projectKey=$project_key -T new_$watchname.json --server-id $target_id
    jf xr curl -XPOST -H "Content-Type: application/json" api/v2/watches?projectKey=$project_key -T new_$watchname.json --server-id $target_id
    echo ""
done
