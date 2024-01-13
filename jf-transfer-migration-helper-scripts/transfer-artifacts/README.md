Tranfser all artifacts from all repo in src artifactory to target artifactory. The main purpose for developing this script is to transfer from **Artifactory OSS to Pro.**
The transfer is **Incremental** 
## Precondition:
1. Install jq and JF CLI in the Linux
2. Add both the artifactory details to jf cli (Ex: local and remote)

## How to run the script
### Diff list from source on target
```
chmod +x transfer.sh
./transfer.sh <SRC Artifactory Server ID> <Target Artifactory Server ID> no
```
**Example:** 
```
  ./transfer.sh local remote no
```

### Transfer Diff list from source on target
```
chmod +x transfer.sh
./transfer.sh <SRC Artifactory Server ID> <Target Artifactory Server ID> yes | sh
```
**Example:** 
```
  ./transfer.sh local remote yes | sh
  # Transfer files in 8 threads
  ./transfer.sh local remote yes | xargs -P 8 -I {} sh -c '{}'
```

---

# README for `transfer.sh`

## Overview

The `transfer.sh` script is a Bash script designed to automate the transfer of artifacts between two Artifactory servers. It compares the contents of a source Artifactory server to a target Artifactory server and can perform the following tasks based on user-defined parameters:

- Transfer artifacts from the source server to the target server.
- View the differences between the two servers without performing any transfers.

The script is designed to work with JFrog Artifactory and makes use of the JFrog CLI (`jf`) and the Artifactory Query Language (AQL) to identify and handle artifacts.

## Usage

To use the script, run it with the following command:

```bash
./transfer.sh SOURCE_ID TARGET_ID TRANSFERONLY
```

- `SOURCE_ID`: The Artifactory server ID of the source server.
- `TARGET_ID`: The Artifactory server ID of the target server.
- `TRANSFERONLY`: Specify whether you want to transfer artifacts (`yes`) or view differences (`no`). Valid options for `TRANSFERONLY` are `'yes'` or `'no'`.

## Script Behavior

The script performs the following steps:

1. Accepts the source and target Artifactory server IDs and the `TRANSFERONLY` parameter.
2. Validates the `TRANSFERONLY` parameter to ensure it's set to either `'yes'` or `'no'`. If not, the script exits with an error message.
3. Defines a function `runtask` to perform the following steps:
    - Queries the source and target servers using AQL to retrieve artifact information (including repository, path, name, and SHA256 hash).
    - Compares the artifact lists to find differences between the two servers.
    - Depending on the value of `TRANSFERONLY`, either displays the differences or initiates artifact transfers from the source to the target server.
4. Iterates through all repositories on the source server and calls the `runtask` function for each repository.
5. Cleans up temporary files created during the comparison and transfer process.

## Usage Examples

### Transfer Artifacts

To transfer artifacts from the source to the target server, use the following command:

```bash
./transfer.sh SOURCE_ID TARGET_ID yes
```

### View Differences

To view the differences between the source and target servers without transferring artifacts, use the following command:

```bash
./transfer.sh SOURCE_ID TARGET_ID no
```

## Disclaimer

This script is provided as-is and without any warranties or conditions. It is intended for use with JFrog Artifactory and should be used responsibly and with appropriate permissions. Ensure you have backups and take necessary precautions before transferring artifacts between servers.

## License

The script is provided for use exclusively in connection with JFrog products and services, subject to the limited rights granted in the script.

For questions or issues related to this script, please reach out to JFrog support.

