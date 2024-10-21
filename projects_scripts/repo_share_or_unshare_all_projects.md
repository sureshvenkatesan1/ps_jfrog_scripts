# Repository Share or Unshare with All Projects Script

The `repo_share_or_unshare_all_projects.sh` script is a Bash utility designed to streamline the process of sharing or unsharing repositories with all projects within a JFrog Platform Deployment (JPD). This script allows you to perform bulk repository sharing or unsharing operations across multiple projects within a JPD instance.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **JFrog Platform Deployment (JPD):**
    - **JPD URL:** The URL of the JPD instance where you want to share or unshare repositories (e.g., `https://ramkannan.jfrog.io`).

3. **Authentication Token/Key:**
    - **JPD Authentication Token:** An authentication bearer token, user password, or API key for the JPD instance.

4. **Action:** Specify whether you want to "share" or "unshare" repositories with all projects.

## Usage

You can use the script by running the following command:

```bash
./repo_share_or_unshare_all_projects.sh <JPD_URL> <JPD_AUTH_TOKEN> <ACTION>
```

- `<JPD_URL>`: The URL of the JPD instance where the repository sharing or unsharing operation will be performed.

- `<JPD_AUTH_TOKEN>`: The authentication bearer token, user password, or API key for the JPD instance.

- `<ACTION>`: Mention whether you want to "share" or "unshare" repositories with all projects.

## Script Overview

The script performs the following actions:

1. **Retrieve Repositories List:**
    - It sends an API request to the JPD instance to retrieve a list of repositories.
    - The list of repositories is saved in a text file (`repos_list.txt`).

2. **Share or Unshare Repositories:**
    - For each repository listed in `repos_list.txt`, it performs the specified action (share or unshare) with all projects within the JPD.
    - The script sends the corresponding API request to the JPD instance to perform the action.

3. **Validation:**
    - The script checks if the specified action is either "share" or "unshare." If the action is not one of these, it displays an "Invalid Action" message.

## Example Command

Here are example commands to run the script:

- To share repositories with all projects:

```bash
./repo_share_or_unshare_all_projects.sh https://ramkannan.jfrog.io <JPD_AUTH_TOKEN> share
```

- To unshare repositories from all projects:

```bash
./repo_share_or_unshare_all_projects.sh https://ramkannan.jfrog.io <JPD_AUTH_TOKEN> unshare
```


Ensure that you have the necessary permissions and configurations in the JPD instance to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed to simplify the process of bulk repository sharing or unsharing with all projects within a JPD. Ensure that it aligns with your specific use case, and consider adapting it if you have different requirements.