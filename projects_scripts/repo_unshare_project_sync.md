# Repository Unshare Project Sync Script

The `repo_unshare_project_sync.sh` script is a Bash tool designed to automate the process of unsharing repositories associated with projects between two JFrog Platform Deployments (JPDs). This script is useful when you need to synchronize projects between different JPD instances while removing repository sharing between them.

## Prerequisites

Before using this script, ensure that you have the following prerequisites:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **JFrog Platform Deployments (JPDs):**
    - **Source JPD URL:** The URL of the source JPD instance from which you want to synchronize projects and unshare repositories (e.g., `https://ramkannan.jfrog.io`).
    - **Target JPD URL:** The URL of the target JPD instance where you want to synchronize projects and unshare repositories (e.g., `http://35.208.78.203:8082`).

3. **Authentication Tokens/Keys:**
    - **Source Authentication Token:** An authentication bearer token, user password, or API key for the source JPD instance.
    - **Target Authentication Token:** An authentication bearer token for the target JPD instance.

## Usage

You can use the script by running the following command:

```bash
./repo_unshare_project_sync.sh <source_JPD_URL> <target_JPD_URL> <source_auth_token> <target_auth_token>
```

- `<source_JPD_URL>`: The URL of the source JPD instance.

- `<target_JPD_URL>`: The URL of the target JPD instance.

- `<source_auth_token>`: The authentication bearer token, user password, or API key for the source JPD instance.

- `<target_auth_token>`: The authentication bearer token for the target JPD instance.

## Script Overview

The script performs the following actions:

1. **Retrieve Project and Repository Lists:**
    - It sends an API request to the source JPD instance to retrieve a list of projects and saves them in a text file (`projects_list.txt`).
    - It also retrieves a list of repositories and saves them in another text file (`repos_list.txt`).

2. **Unshare Repositories:**
    - For each project in the `projects_list.txt` file, it iterates through the repositories listed in `repos_list.txt`.
    - It sends a DELETE request to the target JPD instance to unshare each repository from the project using the provided authentication token.

## Example Command

Here is an example command to run the script:

```bash
./repo_unshare_project_sync.sh https://ramkannan.jfrog.io http://35.209.109.173:8082 <source_token> <target_token>
```

Ensure that you have the necessary permissions and configurations in both the source and target JPD instances to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed for unsharing repositories between projects during project synchronization. Make sure it fits your specific use case, and consider adapting it if you need additional functionality or have different requirements.