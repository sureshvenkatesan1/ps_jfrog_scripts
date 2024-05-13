
# Fetch URIs for Missing SHA1 Checksums

## Overview

This script fetches URIs for missing SHA1 checksums from JFrog Artifactory, particularly useful when using an S3 
bucket as the filestore. It compares SHA1 checksums in the Artifactory database with those in the S3 filestore and identifies missing binaries.

The URIs are URL-encoded to handle special characters in artifact names  as URI returned by the [Checksum Search](https://jfrog.com/help/r/jfrog-rest-apis/checksum-search) 
REST call is not encoded  as per [RTFACT-9137](https://jfrog.atlassian.net/browse/RTFACT-9137) .

The steps are similarly to `"Method 1"`  in the JFrog knowledge base article,
[How to check integrity of binaries in Artifactory database against filestore?](https://jfrog.com/help/r/how-to-check-integrity-of-binaries-in-artifactory-database-against-filestore/how-to-check-integrity-of-binaries-in-artifactory-database-against-filestore)
This is preferable to avoid the slow https://github.com/JFrogDev/artifactory-scripts/tree/master/filestoreIntegrity 
mentioned in `"Method 3`.

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

---

