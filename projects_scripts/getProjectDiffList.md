# Get Project Difference List Script

The `getProjectDiffList.sh` script is a Bash utility designed to identify the differences in project configurations between two JFrog Platform Deployments (JPDs). It allows you to compare projects in a source JPD with those in another JPD and optionally apply the differences to synchronize the projects.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **Python Script:** The script uses a Python script called `getDiffOfFiles.py` to calculate the differences between project lists. Ensure that Python 3 is installed, and the `getDiffOfFiles.py` script is available in the script's parent directory.

3. **JFrog Platform Deployments (JPDs):**
    - **Source JPD URL:** The URL of the source JPD instance from which you want to compare projects (e.g., `https://ramkannan.jfrog.io`).
    - **DR_1 JPD URL:** The URL of the second JPD instance (e.g., `http://35.208.78.203:8082`).

4. **Identity Tokens:** You need authentication bearer tokens or identity tokens for both the source and DR_1 JPD instances.

5. **Dry Run Option (Optional):** You can set the `DRY_RUN` variable to `true` if you want to check the differences without making any changes. If you set it to `false`, the script will apply the differences.

## Usage

You can use the script by running the following command:

```bash
./getProjectDiffList.sh <source_JPD_URL> <DR_1_JPD_URL> <source_auth_token> <DR_1_JPD_auth_token> <DRY_RUN>
```

- `<source_JPD_URL>`: The URL of the source JPD instance.

- `<DR_1_JPD_URL>`: The URL of the second JPD instance (DR_1).

- `<source_auth_token>`: The authentication bearer token or identity token for the source JPD instance.

- `<DR_1_JPD_auth_token>`: The authentication bearer token or identity token for the DR_1 JPD instance.

- `<DRY_RUN>`: Set this option to `true` if you want to check the differences without making any changes. Set it to `false` to apply the differences.

## Script Overview

The script performs the following actions:

1. **Retrieve Project Lists:**
    - It sends API requests to both the source and DR_1 JPD instances to retrieve lists of projects.
    - The project lists are saved in text files (`project-list_source.txt` and `project-list_jpd1.txt`).

2. **Calculate Project Differences:**
    - It uses a Python script (`getDiffOfFiles.py`) to calculate the differences between the project lists.
    - The differences are saved in an output file.

3. **Synchronize Projects (Optional):**
    - If differences are found, it checks the `DRY_RUN` setting.
    - If `DRY_RUN` is set to `true`, it displays the differences without making changes.
    - If `DRY_RUN` is set to `false`, it runs the `updateProjectDiffConfigJPD.sh` script to apply the differences and synchronize projects.

## Example Command

Here is an example command to run the script:

```bash
./getProjectDiffList.sh https://ramkannan.jfrog.io http://35.208.78.203:8082 <source_auth_token> <DR_1_JPD_auth_token> true
```

Ensure that you have the necessary permissions and configurations in both the source and DR_1 JPD instances to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed to automate the comparison of project configurations between two JPD instances and synchronize them if needed. Make sure it aligns with your specific use case, and consider adapting it if you have different requirements.