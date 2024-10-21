# Project Component Diff Config JPD Update Script

This Bash script, `updateProjectComponentDiffConfigJPD.sh`, is designed to facilitate the management of project components across multiple JFrog Platform Deployments (JPDs). It helps synchronize changes made to project components such as users, groups, and roles between two different JPD instances.

## Prerequisites

Before using this script, ensure that you have the following prerequisites:

1. Bash Shell: The script is written in Bash and requires a Bash-compatible shell to execute.

2. JFrog Platform Deployments (JPDs):
    - Source JPD URL: The URL of the source JPD instance from which you want to export data.
    - Target JPD URL: The URL of the target JPD instance to which you want to import data.

3. Authentication Tokens:
    - Source Authentication Token: An authentication bearer token for the source JPD instance.
    - Target Authentication Token: An authentication bearer token for the target JPD instance.

4. Data to Be Collected:
    - Specify the type of data you want to manage. This can be one of the following:
        - users
        - groups
        - roles

5. Project Name: The ID of the project for which you want to manage components.

## Usage

You can use the script by providing the required arguments as follows:

```bash
./updateProjectComponentDiffConfigJPD.sh <file_name> <source_JPD_URL> <target_JPD_URL> <source_auth_token> <target_auth_token> <data_type> <project_name>
```

- `<file_name>`: The name of the text file containing the component differences (e.g., `diffFile.txt`).

- `<source_JPD_URL>`: The URL of the source JPD instance (e.g., `http://35.208.78.203:8082`).

- `<target_JPD_URL>`: The URL of the target JPD instance (e.g., `https://ramkannan.jfrog.io`).

- `<source_auth_token>`: The authentication bearer token for the source JPD instance.

- `<target_auth_token>`: The authentication bearer token for the target JPD instance.

- `<data_type>`: The type of data to be managed (e.g., `users`, `groups`, `roles`).

- `<project_name>`: The ID of the project for which components will be managed (e.g., `dp1`).

## Script Overview

The script performs the following actions:

1. Reads the differences from the specified text file (`<file_name>`).

2. Iterates through each line in the file and determines whether it's an addition or deletion of a component.

3. For additions:
    - Retrieves the component data from the source JPD using the provided authentication token and URL.
    - Exports the data to a JSON file.
    - Imports the JSON data to the target JPD.

4. For deletions:
    - Deletes the specified component from the target JPD.

## Example Command

Here is an example command to run the script:

```bash
./updateProjectComponentDiffConfigJPD.sh diffFile.txt https://ramkannan.jfrog.io http://35.208.78.203:8082 <source_token> <target_token> users dp1
```

Please ensure that you have the necessary permissions and configurations in both the source and target JPD instances to perform these operations.

**Note:** Make sure you handle authentication tokens securely and follow best practices for storing and managing sensitive information.