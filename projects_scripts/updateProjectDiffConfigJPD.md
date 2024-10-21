# Project Diff Config JPD Update Script

The `updateProjectDiffConfigJPD.sh` script is a Bash tool designed to facilitate the synchronization of projects between different JFrog Platform Deployments (JPDs). It allows you to manage the addition and deletion of projects across multiple JPD instances by providing a text file that contains project differences.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. **Bash Shell:** The script is written in Bash and requires a Bash-compatible shell to run.

2. **JFrog Platform Deployments (JPDs):**
    - **Source JPD URL:** The URL of the source JPD instance from which you want to export or delete projects (e.g., `http://35.208.78.203:8082`).
    - **Target JPD URL:** The URL of the target JPD instance where you want to import or delete projects (e.g., `https://ramkannan.jfrog.io`).

3. **Authentication Tokens:**
    - **Source Authentication Token:** An authentication bearer token for the source JPD instance.
    - **Target Authentication Token:** An authentication bearer token for the target JPD instance.

## Usage

You can use the script by providing the following command:

```bash
./updateProjectDiffConfigJPD.sh <file_name> <source_JPD_URL> <target_JPD_URL> <source_auth_token> <target_auth_token>
```

- `<file_name>`: The name of the text file that contains project differences (e.g., `diffFile.txt`).

- `<source_JPD_URL>`: The URL of the source JPD instance.

- `<target_JPD_URL>`: The URL of the target JPD instance.

- `<source_auth_token>`: The authentication bearer token for the source JPD instance.

- `<target_auth_token>`: The authentication bearer token for the target JPD instance.

## Script Overview

The script performs the following actions based on the content of the provided text file:

1. **Addition of Projects:**
    - If a line in the text file starts with a `+` sign, the script identifies it as an addition of a project.
    - It exports the project information from the source JPD using the source authentication token.
    - The project information is saved as a JSON file (`<project_name>.json`).
    - It imports the JSON data to the target JPD to create the project.

2. **Deletion of Projects:**
    - If a line in the text file starts with a `-` sign, the script identifies it as the deletion of a project.
    - It deletes the specified project from the target JPD.

3. **Invalid Input:**
    - If a line in the text file doesn't match the expected format, the script reports it as "Invalid Input."

## Example Command

Here is an example command to run the script:

```bash
./updateProjectDiffConfigJPD.sh diffFile.txt https://ramkannan.jfrog.io http://35.208.78.203:8082 <source_token> <target_token>
```

Make sure you have the necessary permissions and configurations in both the source and target JPD instances to perform these operations. Additionally, handle authentication tokens securely and follow best practices for storing and managing sensitive information.

**Note:** This script is specifically designed for managing projects. If you need to manage other types of components, consider using a similar script with appropriate modifications.