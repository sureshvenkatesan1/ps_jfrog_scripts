# Get Project Component List Script

The `getProjectComponentList.sh` script is a Bash utility designed to retrieve and collect information about users, groups, or roles associated with projects in a JFrog Platform Deployment (JPD) instance. This script allows you to gather data related to project components for analysis or management purposes.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **JFrog Platform Deployment (JPD):**
    - **JPD URL:** The URL of the JPD instance from which you want to collect project component data (e.g., `https://ramkannan.jfrog.io`).

3. **JPD Type:** Specify the type of JPD instance you are targeting (e.g., `source`, `jpd1`, `jpd2`). This helps in naming the output files.

4. **Data Type (users/groups/roles):** Choose the type of project component data you want to collect (`users`, `groups`, `roles`).

5. **Identity Token:** You need an authentication bearer token or identity token to access the JPD instance.

## Usage

You can use the script by running the following command:

```bash
./getProjectComponentList.sh <JPD_URL> <JPD_Type> <Data_Type> <AUTH_TOKEN>
```

- `<JPD_URL>`: The URL of the JPD instance.

- `<JPD_Type>`: Specify the type of JPD instance you are targeting (e.g., `source`, `jpd1`, `jpd2`).

- `<Data_Type>`: Choose the type of project component data you want to collect (`users`, `groups`, `roles`).

- `<AUTH_TOKEN>`: The authentication bearer token or identity token for accessing the JPD instance.

## Script Overview

The script performs the following actions:

1. **Retrieve Project List:**
    - It sends an API request to the JPD instance to retrieve a list of projects.
    - The list of project names is saved in a text file (`project-list.txt`).

2. **Collect Project Component Data:**
    - For each project listed in `project-list.txt`, it performs the following actions:
        - Sends an API request to the JPD instance to retrieve project component data (users, groups, or roles).
        - Saves the retrieved data in a JSON file named based on the JPD type, project name, and data type (e.g., `source_projectname_users.txt`).
        - Parses the JSON data to extract and sort relevant information (names of users, groups, or roles).
        - Saves the sorted data in a text file named based on the JPD type, project name, and data type (e.g., `source_projectname_users.txt`).

3. **Output Files:**
    - The script generates multiple output files, each containing the sorted component data for a specific project in a specific JPD type.

## Example Command

Here is an example command to run the script:

```bash
./getProjectComponentList.sh https://ramkannan.jfrog.io source users ****
```

Ensure that you have the necessary permissions and configurations in the JPD instance to access and retrieve project component data. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is designed to automate the collection of project component data for analysis or management purposes. Make sure it aligns with your specific use case, and consider adapting it if you have different requirements.