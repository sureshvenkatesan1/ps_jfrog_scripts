
# Find Unshared Repositories in a JFrog Artifactory Project

This Python script allows you to find repositories in a JFrog Artifactory project that are not shared with the specified project.

## Usage

To use this script, follow the instructions below:

1. **Prerequisites:**
   - You must have Python installed on your system.
   - Obtain an access token for authentication with the JFrog Artifactory service.

2. **Command Line Usage:**
   Execute the script using the following command-line arguments:

   ```bash
   python find_unshared_repositories_in_project.py --project-key <project_key> --access-token <access_token> --base-url <base_url>
   ```

- `--project-key <project_key>`: The key of the project you want to check for unshared repositories.
- `--access-token <access_token>`: Your access token for authentication.
- `--base-url <base_url>`: The base URL of the Artifactory service (e.g., `https://proservices.jfrog.io`).

3. **Example:**
   ```bash
   python find_unshared_repositories_in_project.py --project-key my-project --access-token my-access-token --base-url https://proservices.jfrog.io
   ```

4. **Note:**
    - This script retrieves information about local, remote, and virtual repositories within the specified project.
    - It identifies repositories that are not shared with the project specified by `--project-key` and lists their names.

    - Make sure to provide the correct values for `project-key`, `access-token`, and `base-url`.

## Script Details

The script consists of several functions to perform the following tasks:

- Fetch repositories of different types (local, remote, virtual, federated) within the specified project.
- Identify repositories that are not shared with the project.
- Handle virtual repositories and their selected repositories differently.
- Recursively check shared status for selected repositories within virtual repositories.

## Troubleshooting
One issue I found was the following API returns inconsistent results:

```curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p1"```

Sometimes it incorrectly shows that "repoKey":"p1-lr1" is "sharedWithProjects":["p2"] as below:
```
[
  {
    "repoKey": "p1-lr1",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p1",
    "projectName": "project1",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [
      "p2"
    ],
    "shareWithAllProjects": false,
    "replications": false,
    "target": false,
    "sharedReadOnly": false
  }
]
```

Sometimes the result is correct as "repoKey":"p1-lr1" is not any project i.e  "sharedWithProjects":[]
```
[
  {
    "repoKey": "p1-lr1",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p1",
    "projectName": "project1",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [],
    "shareWithAllProjects": false,
    "replications": false,
    "target": false,
    "sharedReadOnly": false
  }
]
```

Need to check on this internally.

Current workaround is to run the script few times to verify if the "repoKey":"p1-lr1" is really shared with the project you are interested in or not.