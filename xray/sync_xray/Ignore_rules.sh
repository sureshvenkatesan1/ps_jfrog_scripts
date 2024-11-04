##################################################################################################
#  NOTE: Policies and Watches must be synced before running IgnoreRule sync
################################################################################################## 
source_id="${1:?Source ID for JF CLI.}"
target_id="${2:?Target ID for JF CLI.}"
# #### Sync all golbal ignore_rules and no project polices.
for igname in `jf xr curl -s -XGET api/v1/ignore_rules --server-id $source_id| jq -r '.data[]| select(.project_key|not) | .id'`
do
    jf xr curl -s -XGET api/v1/ignore_rules/$igname --server-id $source_id > $igname.json
    jf xr curl -XPOST -H "Content-Type: application/json" api/v1/ignore_rules -T $igname.json --server-id nagag-jpd1
done

### Sync all  project ignore_rules. 
for igname in `jf xr curl -s -XGET api/v1/ignore_rules --server-id $source_id| jq -r '.data[]| select(.project_key) | .id'`
do
    
    jf xr curl -s -XGET api/v1/ignore_rules/$igname --server-id $source_id> $igname.json
    project_key=`cat $igname.json | jq -r '.project_key'`
    cat $igname.json | jq -r 'del(.project_key)' > new_$igname.json
    jf xr curl -XPOST -H "Content-Type: application/json" api/v1/ignore_rules?projectKey=$project_key -T new_$igname.json --server-id $target_id
done
