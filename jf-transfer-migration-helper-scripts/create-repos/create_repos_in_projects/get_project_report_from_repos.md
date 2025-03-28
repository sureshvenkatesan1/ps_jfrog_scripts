# Repository Project Report Generator

This [get_project_report_from_repos.py](get_project_report_from_repos.py) script generates a report of repository project assignments in Artifactory. It can report on either a specific repository or all repositories of a given type (virtual/local/remote/federated).

## Features

- Get project assignments for a specific repository
- Get project assignments for all repositories of a specific type (virtual/local/remote/federated)
- Get a detailed breakdown of repositories assigned to a specific project
- Report includes:
  - Repository name
  - Project assignment
  - Shared with projects list
  - Shared with all projects status
  - Environment information
- Output in JSON format, table format, and detailed logs. See the [sample_report_output](sample_report_output) directory for an example.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `requests` (`pip install requests`)
  - `tabulate` (`pip install tabulate`)
  - `tqdm` (`pip install tqdm`)
- Access to an Artifactory instance
- Valid Artifactory access token

## Setup

1. Set environment variables (optional, can also be provided as command-line arguments):

```bash
export ARTIFACTORY_URL="http://your-artifactory-instance:8082"
export MYTOKEN2="your-access-token"
```

## Usage

### Basic Usage

1. For all repositories (no filtering):

```bash
python get_project_report_from_repos.py
```

2. For a specific repository:

```bash
python get_project_report_from_repos.py --repo-name your-repo-name
```

3. For all repositories of a specific type:

```bash
python get_project_report_from_repos.py --repo-type local
```

4. For repositories assigned to a specific project:

```bash
python get_project_report_from_repos.py --repo-type all --project-key your-project-key
```

This will output:
- A breakdown of repositories by type (local/remote/virtual/federated)
- A list of shared repositories
- A semicolon-separated list of all non-virtual repositories assigned to the project

### Advanced Usage

1. With custom output file:

```bash
python get_project_report_from_repos.py --repo-type remote --output custom_report.json
```

2. Providing URL and token directly:

```bash
python get_project_report_from_repos.py \
    --repo-type local \
    --artifactory-url "http://your-artifactory:8082" \
    --token "your-access-token"
```

3. Process repositories in parallel:

```bash
# Process 20 repositories simultaneously
python get_project_report_from_repos.py --parallel 20

# Process remote repositories with 30 parallel threads
python get_project_report_from_repos.py --repo-type remote --parallel 30
```

### Command-line Options

```
--repo-name          Name of a specific repository to check (optional)
--repo-type          Type of repositories to check (local/remote/federated/virtual/all) (optional)
--artifactory-url    Artifactory URL (default: from ARTIFACTORY_URL env var)
--token             Access token (default: from MYTOKEN2 env var)
--output            Output JSON file path (default: project_report.json)
--parallel          Number of repositories to process in parallel (default: 10)
--project-key       Project key to filter repositories (used with --repo-type all)
--help              Show help message and exit
```

Note: If neither --repo-name nor --repo-type is specified, the script will generate a report for all repositories.
The --project-key option can only be used with --repo-type all.

## Output

The script generates several types of output:

1. Console Table Display:
   Shows the report in an easy-to-read tabular format directly in the terminal.

2. Project-Specific Output (when using --project-key):
   ```
   Repositories for project myproject:

   Assigned repositories by type:
   LOCAL: repo1;repo2;repo3
   REMOTE: remote1;remote2
   VIRTUAL: virtual1
   FEDERATED: fed1;fed2

   Shared repositories by type:
   LOCAL: shared1;shared2
   REMOTE: shared-remote1
   VIRTUAL: shared-virtual1
   FEDERATED: 

   All assigned non-virtual repositories:
   fed1;fed2;remote1;remote2;repo1;repo2;repo3
   ```

3. Text Report ([project_report.txt](sample_report_output/project_report.txt) or based on specified output name):
   - Contains the same tabular format as console display
   - Easy to read and share
   - Great for quick visual inspection

4. JSON Report ([project_report.json]((sample_report_output/project_report.json)) or specified output file):
   - Structured data format
   - Ideal for programmatic processing
   - Contains all details in machine-readable format

5. Log File ([project_report.log](sample_report_output/project_report.log)):
   - Contains detailed information about the script execution
   - Includes any errors or warnings
   - Shows progress of repository processing

## Examples

1. Get report for a specific repository:

```bash
python get_project_report_from_repos.py --repo-name aanch-deb-local
```

2. Get report for all local repositories:

```bash
python get_project_report_from_repos.py --repo-type local
```

3. Get report for remote repositories with custom output:

```bash
python get_project_report_from_repos.py --repo-type remote --output remote_repos_report.json
```

4. Get report for all repositories:

```bash
python get_project_report_from_repos.py --repo-type all
```

## Error Handling

The script includes comprehensive error handling:

- Validates required parameters before execution
- Logs errors for failed API requests
- Continues processing remaining repositories if one fails
- Provides clear error messages for missing credentials or invalid parameters

## Troubleshooting

1. Authentication Errors
   - Verify your access token is valid
   - Ensure the token has appropriate permissions
   - Check if token is properly set in environment or passed as argument

2. Connection Issues
   - Verify the Artifactory URL is correct and accessible
   - Check network connectivity
   - Ensure no proxy settings are blocking the connection

3. No Data Returned
   - Verify the repository name or type is correct
   - Check if you have permissions to access the repository
   - Ensure the repository exists in Artifactory

## Sample API Responses
### API [Get Repositories by Type and Project](https://jfrog.com/help/r/jfrog-rest-apis/get-repositories-by-type-and-project) Response :
```json
[
  {
    "key": "aanch-deb-local",
    "description" : "",
    "type": "LOCAL",
    "url": "http://artifactory:8082/artifactory/aanch-deb-local",
    "packageType": "Debian"
  }
]
```


### API [Get Status of Project Repository](https://jfrog.com/help/r/jfrog-rest-apis/get-status-of-project-repository) Response:

```json
{
  "resource_name": "aanch-deb-local",
  "assigned_to": "test",
  "environments": ["DEV"],
  "shared_with_projects": ["project1", "project2"],
  "shared_with_all_projects": false,
  "shared_read_only": false
}

### Internal UI API "/ui/api/v1/projects/<projectkey>"
This API gives a list of all repos assigned to a project and their "environments"