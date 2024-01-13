# README for create-repos-during-migration.sh

## Overview

The [create-repos-during-migration.sh](create-repos-during-migration.sh) script is a Bash script that automates the process of migrating repositories from a source server to a target server using JFrog Artifactory's REST API. This script provides flexibility in selecting which repositories to migrate based on various criteria, such as repository type and inclusion/exclusion lists.

## Usage

To use the script, run it with the following command:

```bash
./create-repos-during-migration.sh source-server target-server TYPE includerepos excluderepos
```

- `source-server`: The source server from which you want to migrate repositories.
- `target-server`: The target server where you want to create the migrated repositories.
- `TYPE`: The type of repositories to migrate (e.g., local, remote, virtual, federated, all).
- `includerepos` (Optional): A semicolon-separated list of repositories to include in the migration. Only repositories in this list will be processed.
- `excluderepos` (Optional): A semicolon-separated list of repositories to exclude from the migration. These repositories will be skipped during migration. The default value includes common exclusion repositories, such as "artifactory-build-info" and "_intransit".

## Script Behavior

The script performs the following steps:

1. Creates a directory named `repository` and navigates to it.

2. Retrieves a list of repositories from the source server using the JFrog Artifactory REST API based on the specified repository type (`TYPE`).

3. Iterates through the list of repositories and performs the following actions for each repository:

   - Checks if the repository is in the exclusion list (`excluderepos`). If it is, the repository is skipped.
   - Checks if the repository is in the inclusion list (`includerepos`). If it is, the repository is processed.
   - If neither inclusion nor exclusion criteria apply, the repository is processed by:
     - Exporting the repository's configuration using the REST API and storing it in a file named `$REPO-config.json`.
     - Modifying the exported JSON configuration:
       - If the repository's "rclass" is "remote" and the "password" field is not empty, it replaces the "password" with an empty string.
     - Sending a PUT request to the target server's REST API to create the repository with the modified configuration.
     - Recording the result, and if there is a conflict, the repository is listed in the `conflicting-repos.txt` file.

## Disclaimer

Please note that this script is provided by JFrog on an "as-is" basis and without any warranties or conditions. Use this script responsibly and ensure that you have the necessary permissions and backups in place when migrating repositories.

## License

This script is provided by JFrog for use exclusively in connection with JFrog products and services, subject to the limited rights granted in the script.

For any questions or issues related to this script, please reach out to JFrog support.