1. Ask customer for the list of repos to sync in phase1 as syncing all the repos from source to target will take time.
Customer gave us the 1-High_priority_repos.txt.  Verify if all the repos are in the source artifactory so that it can be created in the target.

The 1-High priority repos:
```
sort -o 1-High_priority_repos.txt 1-High_priority_repos.txt
```

Get all the repo names in source:
```
jf c use ncr
jf rt curl /api/repositories   | jq -r '.[] | .key' >> ncr/all_repositories.list
sort -o ncr/all_repositories.list ncr/all_repositories.list
```

I have 2 files with the lines sorted.  How to find out if all the lines in the  small file is in the big file  . If there are any lines that  are not in the big file I want to get those  lines:

*comm* utility has the -23 option to suppress the output of lines unique to the first file (-2) and lines that are common between both files (-1), resulting in only the lines unique to the first file.

Note: comm utility has the -12 option suppresses the output of lines unique to FILE1 (-1) and lines unique to FILE2 (-2), leaving only the lines that are common between both files.

```
sort -o ncr/NCRAtleos_HighPriorityRepositories_All.08222023 ncr/NCRAtleos_HighPriorityRepositories_All.08222023
```
Check if any of these repos are missing from ncr/all_repositories.list

I verified that there are no   repos in ncr/NCRAtleos_HighPriorityRepositories_All.08222023 that are not in ncr/all_repositories.list using:
```
comm -23 <(sort ncr/NCRAtleos_HighPriorityRepositories_All.08222023) <(sort ncr/all_repositories.list)  
```

You many also need to extract the local, remote , virtual repos as seperate lists using the following:
```
jf c use ncr
jf rt curl  -X GET "/api/repositories?type=local"  | jq -r '.[] | .key' >> ncr/all_local_repos_in_ncr.txt
sort -o ncr/all_local_repos_in_ncr.txt ncr/all_local_repos_in_ncr.txt

jf rt curl  -X GET "/api/repositories?type=remote"  | jq -r '.[] | .key' >> ncr/all_remote_repos_in_ncr.txt
sort -o ncr/all_remote_repos_in_ncr.txt ncr/all_remote_repos_in_ncr.txt

jf rt curl  -X GET "/api/repositories?type=virtual"  | jq -r '.[] | .key' >> ncr/all_virtual_repos_in_ncr.txt
sort -o ncr/all_virtual_repos_in_ncr.txt ncr/all_virtual_repos_in_ncr.txt
```

---

2. Bucket the high priority repos NCRAtleos_HighPriorityRepositories_All.08222023 we got from customer 
into local, remote and virtual.

Use [find_repos_in_files_and_bucket_by_type.py](find_repos_in_files_and_bucket_by_type.py) to read each repo name from a input file.
If the repo is in any of the  3 repo types file list i.e ["all_local_repos_in_ncr.txt", "all_remote_repos_in_ncr.txt", "all_virtual_repos_in_ncr.txt"]
you can bucket them in  found_in_<filename>.txt , where the <filename> is the name of the 3 repo types files :

```
python find_repos_in_files_and_bucket_by_type.py
```
Since the customer gave us only the local and virtual repo names , we need to create the repos from:
```
ncr/found_in_all_local_repos_in_ncr.txt
ncr/found_in_all_virtual_repos_in_ncr.txt
```


---

3. Create the "local" repos in target RT using the [create-repos.sh](https://github.com/shivaraman83/security-entities-migration/blob/main/create-repos.sh) script .
You can run a modified script  to create the repos from ncr/found_in_all_local_repos_in_ncr.txt in the target artifactory , ncratleostest :
```
cd /Users/sureshv/Documents/From_Customer/ncr/jpds
source=ncr
target=ncratleostest

cat ncr/found_in_all_local_repos_in_ncr.txt.txt |  while read line
do
    REPO=$line
    echo "Getting configuration for "$REPO

        jf rt curl api/repositories/$REPO --server-id=$source >> $target/creating-1-high_local-repos/$REPO-config.json
        echo creating repo -- $REPO on $target
        data=$( jf rt curl  -X PUT api/repositories/$REPO -H "Content-Type: application/json" -T $target/creating-1-high_local-repos/$REPO-config.json --server-id=$target -s | grep message | xargs)
        echo $data
        if [[ $data == *"message"*  ]];then
          echo "$REPO" >> $target/creating-1-high_local-repos/conflicting-repos.txt
        fi
done
```

or

It can be created just using the "jf rt transfer-config-merge" .
Not sure if reducing the  transfer-settings from 8 to  1 is needed as it seems to work with 8 as well.

You cna use shell command to read all lines in a file and print them in a single line with a semi-colon seperator
```
tr '\n' ';' < ncr/found_in_all_local_repos_in_ncr.txt.txt
```

Then use it in:
```
jf rt transfer-config-merge --include-repos "<Semi-colon seperated list of repos>" ncr ncratleostest
```

---

4. Create all required remote repos in the target RT

First find out the remotes in 
```
target=ncratleostest
jf rt curl  -X GET "/api/repositories?type=remote" --server-id=$target | jq -r '.[] | .key' >> "$target/all_remote_repos_in_$target.txt"
sort -o "$target/all_remote_repos_in_$target.txt" "$target/all_remote_repos_in_$target.txt"
```

Following remote repos are yet to the created :

Now which of the repos in ncr/NCRAtleos_HighPriorityRepositories_All.08222023 that are not in ncratleos/ncr-atleos-repositories.list
```
comm -23 <(sort ncr/all_remote_repos_in_ncr.txt) <(sort "$target/all_remote_repos_in_$target.txt") 
```
You can do it using "transfer-config-merge":
```
jf rt transfer-config-merge --include-repos "third-party-docker-aquasec-enforcer-proxy" ncr ncratleostest
```

If it  fails with:
```
06:05:58 [🔵Info] ========== Transferring repositories ==========
06:05:58 [🔵Info] Deactivating key encryption in Artifactory...
06:05:58 [🚨Error] server response: 405
{
  "errors": [
    {
      "status": 405,
      "message": "Cannot disable encryption for SaaS Artifactory"
    }
  ]
}
```


then just export the repo config and import them.
```
cd /Users/sureshv/Documents/From_Customer/ncr/jpds
source=ncr
target=ncratleostest

REPO=third-party-docker-aquasec-enforcer-proxy
jf rt curl api/repositories/$REPO --server-id=$source >> $target/creating-missing-remote-repos/$REPO-config.json

You may need to fix the "password". Just tio create the remote repo you can set it to `"password" : "password"` and change the password after repo creation:

jf rt curl  -X PUT api/repositories/$REPO -H "Content-Type: application/json" -T $target/creating-missing-remote-repos/$REPO-config.json --server-id=$target -s 
```
---

5. Now create the missing virtual repos in the target:

shell command to read all lines in a file and print them in a single line with a semi-colon seperator
```
tr '\n' ';' < ncr/found_in_all_virtual_repos_in_ncr.txt.txt
jf rt transfer-config-merge --include-repos "<Semi-colon seperated list of repos>" ncr ncratleostest
```


---
6. if customer also wants to copy the remote repos -cache to the target artifactory do the following:
Create the local "cached-*" prefix  repos for each of the remote repos
```
jf c use ncr
jf rt curl "/api/repositories?type=remote" | jq -r '.[] | .packageType'  | sort | uniq -c
```

Example:
```
   2 Bower
   2 Debian
   7 Docker
  25 Maven
   1 Npm
   5 NuGet
   1 Pypi
   1 YUM
```

Note:
The command , jf rt curl "/api/repositories?type=remote" , returns a list:
```
[ {
  "key" : "third-party-bower-herokuapp-proxy",
  "description" : " (local file cache)",
  "type" : "REMOTE",
  "url" : "https://github.com/",
  "packageType" : "Bower"
}, {
  "key" : "third-party-bower-proxy",
  "description" : "Third-Party Bower Proxy (local file cache)",
  "type" : "REMOTE",
  "url" : "https://github.com/",
  "packageType" : "Bower"
}
]
```


Ran the following command to create a generic [template.json](template.json) as mentioned in https://github.com/jfrog/SwampUp2022/tree/main/SUP016-Automate_everything_with_the_JFrog_CLI/lab-1 
```
jf rt repo-template template.json
```
Verify creation of the local "cached-*" prefix  repos using [create_cached_locals_for_all_remotes.sh](create_cached_locals_for_all_remotes.sh) with --dry-run option
```
bash ./create_cached_locals_for_all_remotes.sh ncr template.json --dry-run
```

Then create the new cached-* locals i.e without the  --dry-run:
```
bash ./create_cached_locals_for_all_remotes.sh ncr template.json
```
---

7. Next copy the content of the remote repo cache to the respective cached- repo using [copy_to_cached_locals_for_all_remotes.sh](copy_to_cached_locals_for_all_remotes.sh)
```
screen -dmS myjfsession bash -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic; ./copy_to_cached_locals_for_all_remotes.sh ncr --dry-run 2>&1 | tee /root/jf_output_1.log; exec bash'

screen -dmS myjfsession bash -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic; ./copy_to_cached_locals_for_all_remotes.sh ncr 2>&1 | tee /root/jf_output_1.log; exec bash'
```
---

8. Now get the list of cached-* repos as comma separated and create them in the target artifactory.
```
jf rt curl -X GET "/api/repositories?type=local" -s | jq -r '.[].key' | grep '^cached-' | tr '\n' ';'
jf rt transfer-config-merge --include-repos "<Semi-colon seperated list of repos>" ncr ncratleostest
```
---

9. Now start the transfer-files for the local repos from source to the target artifactory:
```
nohup sh -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic;jf rt transfer-files ncr ncratleostest --include-repos "<Semi-colon seperated list of repos>"' &

tail -F ~/nohup.out
```

10. If you have to redo the transfer-files for any of the repos you can use the "--ignore-state" option:

```
nohup sh -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic;jf rt transfer-files ncr ncratleostest --include-repos "<Semi-colon seperated list of repos>" --ignore-state' &
```

11. If you want you can setup replication between *all the local repos* in source artifactory to the corresponding repo in target using
[set-replication.sh](https://github.com/shivaraman83/convert-local-to-federated/blob/master/set-replication.sh)

or
just for  specific `"<Semi-colon seperated list of repos>"`  using [set-replication-for-given-repos.sh](set-replication-for-given-repos.sh):
```
bash -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic; bash ./set-replication-for-given-repos.sh ncr ncratleostest "<Semi-colon seperated list of repos>" --dry-run'

Then run:
bash -c 'export JFROG_CLI_LOG_LEVEL=DEBUG;JFROG_CLI_ERROR_HANDLING=panic; bash ./set-replication-for-given-repos.sh ncr ncratleostest "<Semi-colon seperated list of repos>"'
```

12. After the transfer-files or the replication between the repos are done , you can  compare the  source repos to the target repos to identify if all the artifacts/files  have been copied to the target repos using [compare_repo_list_details_in_source_vs_target_rt_after_migration.py](compare_repo_list_details_in_source_vs_target_rt_after_migration.py) which generates the repo comparison summary file [comparison.txt](output/comparison.txt):
```

jf rt curl -X POST "/api/storageinfo/calculate" --server-id=ncr 
Output:
{"info":"Calculating storage summary scheduled to run successfully"}

cd /Users/sureshv/Documents/From_Customer/ncr/jpds/ncr
jf rt curl -X GET "/api/storageinfo" --server-id=ncr > ncr_storageinfo.json


jf rt curl -X POST "/api/storageinfo/calculate" --server-id=ncratleostest 
cd /Users/sureshv/Documents/From_Customer/ncr/jpds/ncratleostest
jf rt curl -X GET "/api/storageinfo" --server-id=ncratleostest > ncratleostest_storageinfo.json

python compare_repo_list_details_in_source_vs_target_rt_after_migration.py --source /Users/sureshv/Documents/From_Customer/ncr/jpds/ncr/ncr_storageinfo.json \
 --target /Users/sureshv/Documents/From_Customer/ncr/jpds/ncratleostest/ncratleostest_storageinfo.json \
  --repos /Users/sureshv/Documents/From_Customer/ncr/jpds/ncr/local_repos_other_than_cached_that_should_sync_to_ncratleostest.txt \
   --out /Users/sureshv/Documents/From_Customer/ncr/scripts/output/comparison.txt
```



13. Then for each repo you can find the diff i.e files in source repo that is not in target repo :
I initially experimented with below scripts ( in [repoDiff](repoDiff) ) which were imporvised from 
[replicationDiff.sh](https://github.com/jfrog/artifactory-scripts/blob/master/replicationDiff/replicationDiff.sh) 

On mac:
```
bash ./replicationDiff_jf_modular_w_comm_v3.sh ncr ncratleostest fsg-th-docker-snapshots fsg-th-docker-snapshots
```

On linux:
```
bash ./replicationDiff_jf_modular_w_diff_v2.sh ncr ncratleostest fsg-th-docker-snapshots fsg-th-docker-snapshots
bash ./replicationDiff_jf_modular_w_jq_v4.sh ncr ncratleostest fsg-th-docker-snapshots fsg-th-docker-snapshots
bash ./replicationDiff_with_jf.sh ncr ncratleostest fsg-th-docker-snapshots fsg-th-docker-snapshots
```


Finally came up with this convenient python script [repodiff.py](repoDiff/repodiff.py):

```
python repodiff.py --source-artifactory ncr --target-artifactory ncratleostest --source-repo fsg-th-docker-snapshots --target-repo fsg-th-docker-snapshots
```

Helper commands:
```
Both the following grep commands were slow on my mac to check for files not containing "-202" in the file name in the 4 MB filepaths_nometadatafiles.txt:

uses regex:
grep -v "-202" filepaths_nometadatafiles.txt
and
The -F flag for grep can be used to treat the search pattern as a fixed string (rather than a regular expression)
grep -vF "-202" filepaths_nometadatafiles.txt

Instead this is fast , tells awk to print all lines from the file that do not match the pattern "-202".:
awk '!/-202/' filepaths_nometadatafiles.txt 

```

14. If you have to delete the artifacts in a huge repo , so you can start over the transfer-files for the repo you can use
[delete_artifacts_in_repo_in_batches.sh](delete_artifacts_in_repo_in_batches.sh) :
```
bash ./delete_artifacts_in_repo_in_batches.sh <repo_name> <total_artifacts_to_delete_in_batch> artifactory-serverid
Example:
bash ./delete_artifacts_in_repo_in_batches.sh example-repo-local 1000 ncr
```

