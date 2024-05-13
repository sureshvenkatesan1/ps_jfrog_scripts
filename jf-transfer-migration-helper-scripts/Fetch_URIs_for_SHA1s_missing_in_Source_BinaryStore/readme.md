
# Fetch URIs for SHA1 Checksums Missing in BinaryStore but present in Artifactoy Database

## Overview

The [filestoreIntegrity.py](https://github.com/jfrog/artifactory-scripts/blob/master/filestoreIntegrity/filestoreIntegrity.py) script can be used to check for inconsistencies in your Artifactory filestore. 
This is useful, for example, when some external process has deleted files directly from the filestore. 
The JFrog knowledge base article,
[How to check integrity of binaries in Artifactory database against filestore?](https://jfrog.com/help/r/how-to-check-integrity-of-binaries-in-artifactory-database-against-filestore/how-to-check-integrity-of-binaries-in-artifactory-database-against-filestore)
mentions that the `filestoreIntegrity.py` script is not particularly fast or efficient, and may not be suitable for use on large Artifactory instances.

Use the [fetch_uris_for_sha1.py](fetch_uris_for_sha1.py) script instead. 
This script fetches URIs for missing SHA1 checksums from JFrog Artifactory   similar to `"Method 1"`  in the KB, and is particularly useful when using an S3 
bucket as the filestore. It compares SHA1 checksums in the Artifactory database with those in the S3 filestore and identifies missing binaries.

Note: The URIs are URL-encoded to handle special characters in artifact names  as URI returned by the [Checksum Search](https://jfrog.com/help/r/jfrog-rest-apis/checksum-search) 
REST call is not encoded  as per [RTFACT-9137](https://jfrog.atlassian.net/browse/RTFACT-9137) .

 


## Prerequisites

- **Python 3.x**: Ensure Python is installed on your system.
- **JFrog CLI**: Install and configure the JFrog CLI with the appropriate `server-id`.
- **jq**: Install `jq` for JSON parsing.


## Usage

### Step 1: Retrieve SHA1 Checksums from Artifactory Database

Execute the following SQL query on your Artifactory database to export SHA1 checksums to `db_sha1s.txt`:
```sql
SELECT sha1 FROM binaries ORDER BY sha1 ASC;
```

### Step 2: List SHA1 Checksums from S3 Filestore

Run the following command to list SHA1 checksums from your S3 bucket and save to `s3_sha1s.txt`:
```bash
aws s3 ls s3://<YOUR-S3-BUCKET>/filestore/ --recursive | awk '$0 !~ /\/$/ { $1=$2=$3=""; print $0}' | cut -c17-  | sort > s3_sha1s.txt

For example:
aws s3 ls s3://adim-bucket/filestore/ --recursive | awk '$0 !~ /\/$/ { $1=$2=$3=""; print $0}' | cut -c17- | sort > s3_sha1s.txt

```
See  [s3_sha1s.txt](s3_sha1s.txt) of example output.

### Step 3: Compare SHA1 Lists

Generate the list of missing SHA1 checksums:
```bash
comm -23 <(sort db_sha1s.txt) <(sort s3_sha1s.txt) > missing_sha1s.txt
```

### Step 4: Run the Script

Use the [fetch_uris_for_sha1.py](fetch_uris_for_sha1.py) script to fetch URIs for the missing SHA1 checksums:

#### Command

```bash
python fetch_uris_for_sha1.py <server_id> <missing_sha1s_file> <output_file>
```

#### Example

```bash
python fetch_uris_for_sha1.py soleng missing_sha1s.txt missing_uris.txt
```



## Conclusion

By following these steps, you can effectively identify and fetch URIs for binaries missing in your S3 filestore, ensuring the integrity of your Artifactory instance. The script leverages JFrog CLI and `jq` for efficient processing and retrieval of data.

More details of the uris in the `missing_uris.txt` can  be got using `jf`:
For exmaple if the missing binary url is:
`https://soleng.jfrog.io/artifactory/api/storage/AvanadeTest/giscus-main%20%282%29.zip`
You can run:
```
jf rt curl "/api/storage/AvanadeTest/giscus-main%20%282%29.zip" --server-id=YOUR-SERVER-ID
```
To get output simialr to:
```
{
  "repo" : "AvanadeTest",
  "path" : "/giscus-main (2).zip",
  "created" : "2024-04-30T06:02:42.005Z",
  "createdBy" : "avanade",
  "lastModified" : "2024-04-30T06:02:25.879Z",
  "modifiedBy" : "avanade",
  "lastUpdated" : "2024-04-30T06:02:42.006Z",
  "downloadUri" : "https://soleng.jfrog.io/artifactory/AvanadeTest/giscus-main (2).zip",
  "mimeType" : "application/zip",
  "size" : "519367",
  "checksums" : {
    "sha1" : "fc8da3ae50723a8f98b693e965ea8f0b658a8565",
    "md5" : "05409ef70e6db2f627f517047208363c",
    "sha256" : "a7601bdccc351e4f48ecaedc8c641d45f81146ee2041411576f5132b0d0eef16"
  },
  "originalChecksums" : {
    "sha1" : "fc8da3ae50723a8f98b693e965ea8f0b658a8565",
    "md5" : "05409ef70e6db2f627f517047208363c",
    "sha256" : "a7601bdccc351e4f48ecaedc8c641d45f81146ee2041411576f5132b0d0eef16"
  },
  "uri" : "https://soleng.jfrog.io/artifactory/api/storage/AvanadeTest/giscus-main (2).zip"
}
```

---

