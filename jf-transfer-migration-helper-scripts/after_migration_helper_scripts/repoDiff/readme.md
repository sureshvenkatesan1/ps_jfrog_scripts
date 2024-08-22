# Artifactory Repository Data Comparison

The [repodiff.py](repodiff.py) is designed to compare artifacts between source and target repositories in  different 
JFrog Artifactory instances and identifies artifacts present in the source repository but missing in the target repository. It fetches the list of 
artifacts from both source and target repositories , compares the URIs (finds the diff  based on repo path and the 
`sha1` checksum) , and generates reports of missing artifacts and statistics.

It also provides additional features such as extracting and sorting artifact statistics and filtering unwanted files.
This tool is essential for ensuring repository consistency and integrity across different Artifactory instances 
especially after a SAAS migration.

It has same logic as the original script in 
https://github.com/jfrog/artifactory-scripts/blob/master/replicationDiff/replicationDiff.sh
and uses the jfrog cli to connect to Artifactory.

## Features

- Fetches and compares artifacts between source and target repositories.
- Generates reports on unique URIs present in the source but missing in the target.
- Provides file statistics sorted by extension.
- Supports filtering out unwanted metadata files.
- Logs detailed information about artifact download statistics.

## Prerequisites

Before running the script, ensure you have the following prerequisites:

- Python 3.x
- [Artifactory CLI (JFrog CLI)](https://www.jfrog.com/confluence/display/JFROG/JFrog+CLI) installed and configured 
  with server IDs to access source and target JFrog Artifactory instances

## Usage

1. Download the script  [repodiff.py](repodiff.py)  to your local machine.

2. Open a terminal and navigate to the directory where the script is located.

3. Run the script with the following command:

```bash
   python repodiff.py --source-artifactory SOURCE_ARTIFACTORY_ID --target-artifactory TARGET_ARTIFACTORY_ID \
      --source-repo SOURCE_REPOSITORY_NAME --target-repo TARGET_REPOSITORY_NAME \
      [--path-in-repo  <path_within_repository>]
```
### Arguments:

- `--source-artifactory`: The URL of the source Artifactory.
- `--target-artifactory`: The URL of the target Artifactory.
- `--source-repo`: The name of the source repository.
- `--target-repo`: The name of the target repository.
- `--path-in-repo` (optional): Path within the repository ( example: for repo docker-dev-local it can be app1/tag1 i.e the path with no repo name and ending "/" )

The repodiff.py will perform the following actions:

- Fetch artifact information from the source and target repositories.
- Optionally, it can fetch data from a specific path within the repository if `--path-in-repo` parameter is provided.
- Identify artifacts present in the source repository but missing in the target repository.
- Calculate the total size of missing artifacts.
- Write various output files with the results, including lists of unique URIs and statistics in the 
  `output/<source-repo>`    directory.

## Output

The script generates the following output files:

- **cleanpaths.txt**: Contains the URIs of artifacts present in the source repository but missing in the target repository. It also provides statistics on the total size and file extensions.

- **filepaths_uri.txt**: Contains the URIs with the source repository prefix for missing artifacts.

- **filepaths_nometadatafiles.txt**: Contains the URIs without unwanted files, such as metadata files.

- **filepaths_uri_lastDownloaded_desc.txt**: Contains a list of unique URIs for missing artifacts. These URIs are accompanied by their download statistics ( from "artifactory.stats" ) , 
  sorted in descending order of lastDownloaded timestamp in UTC. If an artifact has never been downloaded,  a default timestamp of **"Jan 1, 1900, 00:00:00 UTC"** is used.
- **all_delta_paths_with_differnt_sizes.txt**: List of paths with size , sha1 mismatches or missing in the target.

## Alternative scripts/plugin:
- https://git.jfrog.info/projects/PROFS/repos/ps_jfrog_scripts/browse/compare_repos
- https://git.jfrog.info/projects/PROFS/repos/jfrog-cli-plugin-compare/browse

---
Note:

The output of
```text
jf rt curl -XGET "/api/storage/APM123-att-repository-gold-local/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1"
```
already contains the last download statistics under "artifactory.stats." Therefore, we can utilize the `source_data` to retrieve the `mdTimestamps.artifactory.stats` for each artifact. In cases where an artifact has never been downloaded, we have the option to fall back on the "lastModified" date. However, I've chosen to assign the default last download timestamp as `"1900-01-01T00:00:00.000Z"` for artifacts that were never downloaded.
```text

{
  "uri" : "https://proservices.jfrog.io/artifactory/api/storage/APM123-att-repository-gold-local",
  "created" : "2023-11-08T06:02:37.392Z",
  "files" : [ {
    "uri" : "/",
    "size" : -1,
    "lastModified" : "2023-11-01T15:33:50.186Z",
    "folder" : true
  }, {
    "uri" : "/org/jfrog/test/multi/4.0/multi-4.0.pom",
    "size" : 3270,
    "lastModified" : "2023-11-01T15:41:53.497Z",
    "folder" : false,
    "sha1" : "95a4881c266fd1d4679e1008754f45b19cb4da82",
    "sha2" : "6c258cb4cf2a34eed220d3144e4c873eaefd5346f5382f07b7fd5e930bc4d97c",
    "mdTimestamps" : {
      "properties" : "2023-11-01T15:59:51.694Z"
    }
  }, {
    "uri" : "/org/jfrog/test/multi/maven-metadata.xml",
    "size" : 366,
    "lastModified" : "2023-11-01T15:59:51.116Z",
    "folder" : false,
    "sha1" : "8aaf767b2ed90f5614ab7c600dc0dda967f43923",
    "sha2" : "93cd16c957e5cfc44dfaebe7ac54c353ac92eea796f66b45e4bd51d0262582e9",
    "mdTimestamps" : {
      "artifactory.stats" : "2023-11-08T04:08:23.894Z"
    }
}, {
    "uri" : "/org/jfrog/test/multi3/maven-metadata.xml",
    "size" : 367,
    "lastModified" : "2023-11-01T15:59:51.124Z",
    "folder" : false,
    "sha1" : "ffea43340e639fa5c76fe664c2a5ce87ca81f090",
    "sha2" : "c17e801615a49a46db3d6ece16b66060d7e1084bc09ff535764cc470748e969b"
  } ]
}
```
---
### Behind the scenes:

I initially experimented with below scripts  which were improvised from 
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


Finally came up with the above  convenient python script [repodiff.py](repodiff.py):

---

Print all lines from the file that do not match the pattern "-202":
```
awk '!/-202/' filepaths_nometadatafiles.txt
```

Optional Helper commands ( not required , just FYI):
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
---
#### Performance improvement in Script Functions:

- **`extract_file_info(files)`**:
  - Converts a list of files into a dictionary (hashmap) where the `uri` is the key, and the value is a tuple of the file’s `size` and `sha1` checksum.
  - This dictionary enables constant-time complexity for lookups.

- **`compare_logs(source_files, target_files)`**:
  - Compares the source and target dictionaries by checking if each file exists in both locations and if their 
    checksums match. Using  dictionaries to perform quick lookups and comparisons reduces the time
    complexity to O(1) for each lookup , making it scalable for large datasets.
  - Returns a list of `uri` paths with mismatches or missing files.

---
