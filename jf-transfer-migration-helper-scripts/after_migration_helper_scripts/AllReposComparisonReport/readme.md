# Generate  Comparison Report for Repositories in Source and Target Artifactory Instances

This Python script is designed to compare repository details between source and target Artifactory Instances and generate a comprehensive comparison report. It also assists in generating transfer commands for migrating repositories from a source Artifactory to a target Artifactory.

If  any repos in the source Artifactory have files that have not been transferred to the corresponding  target 
Artifactory repos  the report also generates the necessary [repodiff.py](../repoDiff/repodiff.py) commands  that 
can be run to get the delta in the `“output/<source-repo>/cleanpaths.txt"` as explained in the [readme.md](../repoDiff/readme.md)

**cleanpaths.txt**: Contains the URIs of artifacts present in the source repository but missing in the target repository. It also provides statistics on the total size and file extensions.

Next Transfer this delta , based on  file list  in the  cleanpaths.txt ( that is in source repo and has not been 
transferred to the target repo) using [transfer_cleanpaths_delta_from_repoDiff.py](../fix_the_repoDiff/transfer_cleanpaths_delta_from_repoDiff.py)

Please review the [readme.md](../fix_the_repoDiff/readme.md) of  this script on the usage. It reads the  cleanpaths.txt 
and transfers only the missing files to the target repository in the SAAS instance.

## Prerequisites

Before using this script, make sure you have the following prerequisites installed:

- Python 3.x

## Installation

1. **Clone this repository** to your local machine:

   ```bash
   git clone <repository_url>
   ```
2. Calculate the storage for the source and target Artifactory Instances  
```
jf rt curl -X POST "/api/storageinfo/calculate" --server-id=source
jf rt curl -X POST "/api/storageinfo/calculate" --server-id=target  
``` 


Output:
{"info":"Calculating storage summary scheduled to run successfully"}

3. wait for 2 min for calculation to complete.

4. Generate the storage details for all repos for the source and target Artifactory Instances
```
jf rt curl -X GET "/api/storageinfo" --server-id=source > AllReposComparisonReport/input/source_storageinfo.json
jf rt curl -X GET "/api/storageinfo" --server-id=target > AllReposComparisonReport/input/target_storageinfo.json
```

5. Get the list of `local` repos you want to compare:
```
jf rt curl  -X GET "/api/repositories?type=local"  --server-id=source | jq -r '.[] | .key' >> all_local_repos_in_source.txt

sort -o all_local_repos_in_source.txt all_local_repos_in_source.txt
```
If you want to exclude some repos (listed in exclude_these_cust-responsibility_repos.txt)  from all_local_repos_in_source.txt you can do:
```
comm -23 <(sort all_local_repos_in_source.txt) <(sort exclude_these_cust-resposibility_repos.txt) > ps_currently_migrating_for_group2.txt
```

## Usage
Assume the list of repos we want to compare is  [group2_found_in_all_local_repos_in_ncr.txt](input/group2_found_in_all_local_repos_in_ncr.txt)

Generate the comparison report (comparison.txt) in the "output" folder using:
```
python AllReposComparisonReport/compare_repo_list_details_in_source_vs_target_rt_after_migration.py \
 --source AllReposComparisonReport/input/source_storageinfo.json \
 --target AllReposComparisonReport/input/target_storageinfo.json \
 --repos AllReposComparisonReport/input/group2_found_in_all_local_repos_in_ncr.txt \
 --out comparison.txt \
 --source_server_id source \
 --target_server_id target \
 --total_repos_customer_will_migrate 0 \
 --num_buckets_for_migrating_remaining_repos 3
```
This will generate the report in [comparison.txt](output/comparison.txt)

## Command-line arguments:
```

--source: Path to the source JSON file containing repository details.
--target: Path to the target JSON file containing repository details.
--repos: Path to the text file containing repoKeys that the customer wants to migrate.
--out: the output comparison file where the report will be generated in the "ouput" folder.
--source_server_id: Server ID of the source Artifactory.
--target_server_id: Server ID of the target Artifactory.
--total_repos_customer_will_migrate (optional): Specify the number of repositories that the customer is responsible for migrating.
--num_buckets_for_migrating_remaining_repos (optional): Specify the number of Client VMs  used to run "jf rt transfer-files" . So that
                                                  the comparison report can bucket the repos and genetrate the "jf rt transfer-files" command.
--repo_threshold_in_gb (optional): Threshold in gigabytes (GB) for source repositories to generate alternate migrate commands.
--print_alternative_transfer (optional): Include this flag to print alternative transfer methods for large source repositories.
```
Note: For "Docker" packageType repos in the "--repos" list  , the comparison excludes  the  "repository.catalog" and "*_uploads" in the (source/target)_files_count
     and (source/target)_space_in_bytes calculation , as the files in "*_uploads" from source will not be replicated to the target artifactory instance.