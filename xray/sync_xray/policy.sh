##################################################################################################
#  NOTE: Projects must be synced before running Policy sync
################################################################################################## 

source_id="${1:?Source ID for JF CLI.}"
target_id="${1:?Target ID for JF CLI.}"


# #### Sync all golbal policies and no project polices.
for policyname in `jf xr curl -s -XGET api/v2/policies --server-id $source_id| jq -r '.[]| select(.project_key|not) | .name'`
do
    jf xr curl -s -XGET api/v2/policies/$policyname --server-id $source_id > $policyname.json
    jf xr curl -XPOST -H "Content-Type: application/json" api/v2/policies -T $policyname.json --server-id $target_id
done

### Sync all  project policies. Make sure project sync is done before
for policyname in `jf xr curl -s -XGET api/v2/policies --server-id $source_id| jq -r '.[]| select(.project_key) | .name'`
do
    
    jf xr curl -s -XGET api/v2/policies/$policyname --server-id $source_id > $policyname.json
    project_key=`cat $policyname.json | jq -r '.project_key'`
    cat $policyname.json | jq -r 'del(.project_key)' > new_$policyname.json
    jf xr curl -XPOST -H "Content-Type: application/json" api/v2/policies?projectKey=$project_key -T new_$policyname.json --server-id $target_id 
done
