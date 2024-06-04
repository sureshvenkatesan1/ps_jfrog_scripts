# create-repos-during-migration.sh

This [create-repos-during-migration.sh](create-repos-during-migration.sh) is designed to facilitate the migration of repositories between two JFrog Artifactory instances. It retrieves the configurations of repositories from a source Artifactory instance and recreates them on a target Artifactory instance, with optional inclusion and exclusion lists, and support for setting passwords for remote repositories.

## Usage

```bash
./create-repos-during-migration.sh source-server target-server repo-type [includerepos] [excluderepos] [password]
```

### Parameters

1. `source-server`: The source Artifactory server ID.
2. `target-server`: The target Artifactory server ID.
3. `repo-type`: The type of repositories to migrate (e.g., local, remote, virtual, federated, all).
4. `includerepos` (optional): A semicolon-separated list of repositories to include in the migration.
5. `excluderepos` (optional): A semicolon-separated list of repositories to exclude from the migration. Default value: `artifactory-build-info;_intransit`.
6. `password` (optional): Password for remote repositories if needed.

### Example Command

```bash
./create-repos-during-migration.sh source-server target-server remote "acme-helm-bitnami-remote;ad-npm-remote" "ad-nuget-remote;alex-docker" "your_password"
```

## Script Details

1. **Initialization**: The script initializes variables with the provided parameters and creates a `repository` directory.

2. **Fetching Repository List**: The script retrieves the list of repositories from the source Artifactory instance based on the specified type.

3. **Processing Repositories**: For each repository:
    - It checks if the repository is in the exclusion list or not in the inclusion list.
    - If the repository passes the checks, it retrieves the repository configuration from the source Artifactory instance.
    - If the repository is of type "remote" and a password is provided, it sets the password in the configuration.
    - The repository configuration is then used to create the repository on the target Artifactory instance.

4. **Logging**: Any conflicts or issues during the creation process are logged to `conflicting-repos.txt`.

## Disclaimer

JFrog hereby grants you a non-exclusive, non-transferable, non-distributable right to use this code solely in connection with your use of a JFrog product or service. This code is provided 'as-is' and without any warranties or conditions, either express or implied including, without limitation, any warranties or conditions of title, non-infringement, merchantability, or fitness for a particular cause. Nothing herein shall convey to you any right or title in the code, other than for the limited use right set forth herein. For the purposes hereof "you" shall mean you as an individual as well as the organization on behalf of which you are using the software and the JFrog product or service.

## Exit on Failures

The script is designed to exit on any failures to ensure consistency and reliability during the migration process.