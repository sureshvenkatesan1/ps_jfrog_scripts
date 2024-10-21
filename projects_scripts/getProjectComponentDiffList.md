# Get Project Component Difference List Script

The `getProjectComponentDiffList.sh` script is a Bash utility designed to identify the differences in project component configurations (users, groups, and roles) between two JFrog Platform Deployments (JPDs). It allows you to compare project components in a source JPD with those in another JPD and synchronize them if needed.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **Python Script:** The script uses a Python script called `getDiffOfFiles.py` to calculate the differences between project component lists. Ensure that Python 3 is installed, and the `getDiffOfFiles.py` script is available in the script's parent directory.

3. **Project Component Data Scripts:** This script relies on another script named `getProjectComponentList.sh`, which should be available in the same directory. Ensure that this script is correctly configured and operational.

4. **JFrog Platform Deployments (JPDs):**
    - **Source JPD URL:** The URL of the source JPD instance from which you want to compare project components (e.g., `http://35.208.78.203:8082`).
    - **DR_1 JPD URL:** The URL of the second JPD instance (e.g., `https://ramkannan.jfrog.io`).

5. **Identity Tokens:** You need authentication bearer tokens or identity tokens for both the source and DR_1 JPD instances.

## Usage

You can use the script by running the following command:

```bash
./getProjectComponentDiffList.sh <SOURCE_JPD_URL> <DR_1_JPD_URL> <SOURCE_AUTH_TOKEN> <DR_1_JPD_AUTH_TOKEN>
```

- `<SOURCE_JPD_URL>`: The URL of the source JPD instance.

- `<DR_1_JPD_URL>`: The URL of the second JPD instance (DR_1).

- `<SOURCE_AUTH_TOKEN>`: The authentication bearer token or identity token for the source JPD instance.

- `<DR_1_JPD_AUTH_TOKEN>`: The authentication bearer token or identity token for the DR_1 JPD instance.

## Script Overview

The script performs the following actions:

1. **Retrieve Project Lists:**
    - It uses the `getProjectList.sh` script to send an API request to the source JPD instance and retrieve a list of projects.
    - The list of project names is saved in a text file (`project-list.txt`).

2. **Calculate Project Component Differences:**
    - For each project component type (users, groups, and roles), it performs the following actions:
        - Calls the `getProjectComponentList.sh` script for the source and DR_1 JPD instances to retrieve project component lists.
        - Calculates the differences between the project component lists using the `getDiffOfFiles.py` script.
        - If differences are found, it  uses the  [updateProjectComponentDiffConfigJPD.sh](updateProjectComponentDiffConfigJPD.sh) to synchronize the components.

3. **Synchronize Project Components:**
    - For each project and component type, it checks if differences exist between the source and DR_1 JPD instances.
    - If differences are found, it executes the corresponding synchronization script to update the components in the DR_1 JPD.

## Example Command

Here is an example command to run the script:

```bash
./getProjectComponentDiffList.sh http://35.208.78.203:8082 https://ramkannan.jfrog.io **** ****
```

Ensure that you have the necessary permissions and configurations in both the source and DR_1 JPD instances to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed to automate the comparison and synchronization of project component configurations between two JPD instances. Make sure it aligns with your specific use case, and consider adapting it if you have different requirements.