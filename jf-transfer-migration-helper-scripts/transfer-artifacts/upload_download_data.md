# README for `upload_download_data.sh`

## Overview

The `upload_download_data.sh` script is a Bash script designed to automate the process of transferring repositories from a source Artifactory server to a target Artifactory server. This script is intended for use with JFrog Artifactory and facilitates repository migration and synchronization between two Artifactory instances.

The script performs the following tasks:

1. Checks the health status of both the source and target Artifactory servers.
2. Retrieves a list of local repositories from the source server.
3. Iterates through each repository, downloading it from the source server and uploading it to the target server.

The script is provided by JFrog and is intended for use exclusively in connection with JFrog products and services.

## Usage

To use the script, follow these steps:

1. Ensure you have the JFrog CLI (`jf`) installed and configured on your system with access to the source and target Artifactory servers.

2. Run the script with the following command:

```bash
./upload_download_data.sh
```

## Script Behavior

The script performs the following steps:

1. Checks the health status of both the source and target Artifactory servers to ensure they are reachable and operational.

2. Retrieves a list of local repositories from the source Artifactory server using the JFrog CLI and stores it in a file named `repos_list.txt`.

3. Iterates through each repository in the `repos_list.txt` file and performs the following actions for each repository:

    - Creates a temporary directory with the repository name to download the repository contents.
    - Downloads the repository contents from the source server to the temporary directory using the `jf rt dl` command.
    - Uploads the contents of the temporary directory to the target server using the `jf rt u` command.
    - Removes the temporary directory after the transfer is complete.

4. Continues this process for each repository in the list.

## Disclaimer

This script is provided by JFrog under certain usage rights and conditions. Please review the licensing and usage terms provided in the script header.

It is essential to ensure that you have the necessary permissions and access to both the source and target Artifactory servers before using this script. Additionally, make sure to back up your data and test the script in a non-production environment before performing any migrations.

## License

The script is provided by JFrog for use exclusively in connection with JFrog products and services, subject to the limited rights granted in the script.

For any questions or issues related to this script, please reach out to JFrog support.