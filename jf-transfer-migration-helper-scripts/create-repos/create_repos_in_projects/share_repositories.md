# Share Repositories Script

## Description
This [share_repositories.py](share_repositories.py) script is designed to replicate repository sharing in the target JPD to match the configuration in the source JPD, based on the following conditions:

a) When a project name is provided as a parameter, the script replicates the sharing configuration for repositories assigned to that specific project in the source JPD.

b) When a repository key is provided as a parameter, the script replicates the sharing configuration for that specific repository.

c) If neither a project name nor a repository key is provided, the script replicates the sharing configuration for all repositories, ensuring the target JPD mirrors the source JPD.

Note: For a) & b) conditions the [Share Repository with Target Project](https://jfrog.com/help/r/jfrog-rest-apis/share-repository-with-target-project) API is used.

For condition c) the [Share Repository with All Projects](https://jfrog.com/help/r/jfrog-rest-apis/share-repository-with-all-projects) API is used.

## Usage
To run the script, use the following command:
```
python share_repositories.py --project_report <path_to_project_report.json> --token <authorization_token> --base_url <jfrog_base_url> [--project_name <project_name>] [--repo_key <repository_key>]
```

### Arguments:
- `--project_report`: Path to the project_report.json file generated from [get_project_report_from_repos.py](get_project_report_from_repos.md). For example [sample_report_output/project_report.json](sample_report_output/project_report.json)
- `--token`: Authorization token for JFrog API.
- `--base_url`: Base URL for JFrog API.
- `--project_name`: (Optional) Specific project name to process to find the repos to share.
- `--repo_key`: (Optional) Specific repository key to share.

## Functions
- `share_repository_with_project(repo_key, project_name, token, base_url)`: Shares a specific repository with a given project.
- `share_repository_with_all(repo_key, token, base_url)`: Shares a repository with all projects.

## Logging
The script uses the logging module to log information about the sharing process.