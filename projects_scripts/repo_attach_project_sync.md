# Repository Attach Project Sync Script

The `repo_attach_project_sync.sh` script is a Bash utility created to automate the synchronization of repositories and their attachment to projects within two JFrog Platform Deployments (JPDs). This script simplifies the process of managing repository attachments and synchronization across different JPD instances.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **JFrog Platform Deployments (JPDs):**
    - **Source JPD URL:** The URL of the source JPD instance from which you want to synchronize repositories and their attachments (e.g., `https://ramkannan.jfrog.io`).
    - **Target JPD URL:** The URL of the target JPD instance where you want to synchronize repositories and their attachments (e.g., `http://35.208.78.203:8082`).

3. **Repository Type (local, remote, virtual, federated, all):** Specify the type of repositories to synchronize. You can specify a specific type (e.g., `local`) or use `all` to synchronize all repository types.

4. **Username in JPD:** The username in the source JPD instance used for authentication.

5. **Authentication Tokens/Keys:**
    - **Source Authentication Token:** An authentication bearer token, user password, or API key for the source JPD instance.
    - **Target Authentication Token:** An authentication bearer token for the target JPD instance.

## Usage

You can use the script by running the following command:

```bash
./repo_attach_project_sync.sh <source_JPD_URL> <target_JPD_URL> <repository_type> <username_in_JPD> <source_auth_token> <target_auth_token>
```

- `<source_JPD_URL>`: The URL of the source JPD instance.

- `<target_JPD_URL>`: The URL of the target JPD instance.

- `<repository_type>`: Specify the type of repositories to synchronize (`local`, `remote`, `virtual`, `federated`, `all`).

- `<username_in_JPD>`: The username in the source JPD instance used for authentication.

- `<source_auth_token>`: The authentication bearer token, user password, or API key for the source JPD instance.

- `<target_auth_token>`: The authentication bearer token for the target JPD instance.

## Script Overview

The script performs the following actions:

1. **Retrieve Repositories List:**
    - It sends an API request to the source JPD instance to retrieve a list of repositories based on the specified repository type.
    - The list of repositories is saved in a text file (`repos_list_<repository_type>.txt`).

2. **Synchronize Repository Attachments:**
    - For each repository listed in the `repos_list_<repository_type>.txt` file, it performs the following actions:
        - Export JSON information for the repository from the source JPD.
        - Check if the repository is attached to a project in the source JPD.
        - If the repository is not attached to any project, it unassigns it from projects in the target JPD (if it was previously assigned).
        - If the repository is attached to a project, it unassigns it from projects in the target JPD (if it was previously assigned) and assigns it to the corresponding project in the target JPD.



## Example Command

Here is an example command to run the script:

```bash
./repo_attach_project_sync.sh https://ramkannan.jfrog.io http://35.209.109.173:8082 local admin <source_auth_token> <target_auth_token>
```

Ensure that you have the necessary permissions and configurations in both the source and target JPD instances to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed to automate the synchronization of repositories and their attachments between projects. Ensure that it aligns with your specific use case, and consider adapting it if you have different requirements.