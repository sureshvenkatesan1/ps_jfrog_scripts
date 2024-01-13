# Generate  Comparison Report for Repositories in Source and Target Artifactory Instances

This Python script is designed to compare repository details between source and target Artifactory Instances and generate a comprehensive comparison report. It also assists in generating transfer commands for migrating repositories from a source Artifactory to a target Artifactory.

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
jf rt curl -X POST "/api/storageinfo/calculate" --server-id=ncr
jf rt curl -X POST "/api/storageinfo/calculate" --server-id=ncratleostest  
``` 


Output:
{"info":"Calculating storage summary scheduled to run successfully"}

3. wait for 2 min for calculation to complete.

4. Generate the storage details for all repos for the source and target Artifactory Instances
```
jf rt curl -X GET "/api/storageinfo" --server-id=ncr > AllReposComparisonReport/input/ncr_storageinfo.json
jf rt curl -X GET "/api/storageinfo" --server-id=ncratleostest > AllReposComparisonReport/input/ncratleostest_storageinfo.json
```

5. Get the list of `local` repos you want to compare:
```
jf rt curl  -X GET "/api/repositories?type=local"  | jq -r '.[] | .key' >> ncr/all_local_repos_in_ncr.txt

sort -o ncr/all_local_repos_in_ncr.txt ncr/all_local_repos_in_ncr.txt
```
If you want to exclude some repos (listed in exclude_these_cust-resposibility_repos.txt)  from all_local_repos_in_ncr.txt you can do:
```
comm -23 <(sort all_local_repos_in_ncr.txt) <(sort exclude_these_cust-resposibility_repos.txt) > ps_currently_migrating_for_group2.txt
```

## Usage
Assume the list of repos we want to compare is  [group2_found_in_all_local_repos_in_ncr.txt](input/group2_found_in_all_local_repos_in_ncr.txt)

Generate the comparison report using:
```
python AllReposComparisonReport/compare_repo_list_details_in_source_vs_target_rt_after_migration.py \
 --source AllReposComparisonReport/input/ncr_storageinfo.json \
 --target AllReposComparisonReport/input/ncratleostest_storageinfo.json \
 --repos AllReposComparisonReport/input/group2_found_in_all_local_repos_in_ncr.txt \
 --out AllReposComparisonReport/output/comparison.txt \
 --source_server_id ncr \
 --target_server_id ncratleostest \
 --total_repos_customer_will_migrate 0 \
 --num_buckets_for_migrating_remaining_repos 3
```
This will generate the report in [comparison.txt](output/comparison.txt)

## Command-line arguments:
```

--source: Path to the source JSON file containing repository details.
--target: Path to the target JSON file containing repository details.
--repos: Path to the text file containing repoKeys that the customer wants to migrate.
--out: Path to the output comparison file where the report will be generated.
--source_server_id: Server ID of the source Artifactory.
--target_server_id: Server ID of the target Artifactory.
--total_repos_customer_will_migrate (optional): Specify the number of repositories that the customer is responsible for migrating.
--num_buckets_for_migrating_remaining_repos (optional): Specify the number of Client VMs  used to run "jf rt transfer-files" . So that
                                                  the comparison report can bucket the repos and genetrate the "jf rt transfer-files" command.
--repo_threshold_in_gb (optional): Threshold in gigabytes (GB) for source repositories to generate alternate migrate commands.
--print_alternative_transfer (optional): Include this flag to print alternative transfer methods for large source repositories.
```
