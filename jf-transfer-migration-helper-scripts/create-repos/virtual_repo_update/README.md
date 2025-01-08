# Artifactory Virtual Repository Update Tool

This Python script automates the process of updating Artifactory virtual repository configurations. It specifically helps in reorganizing repository order by placing local repositories first, followed by a specified remote repository, and then any remaining repositories.

## Features

- Automatically reorders repositories within a virtual repository
- Places local repositories first in the priority order
- Inserts a specified remote repository after local repositories
- Maintains the order of other existing repositories
- Provides detailed logging of operations
- Supports SSL verification disable for internal/development environments

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - urllib3

## Installation

1. Clone this repository or download the script
2. Install the required packages:
```bash
pip install requests urllib3
```

## Usage

Run the script using the following command:

```bash
python update_virtual_repo.py --url ARTIFACTORY_URL --token ACCESS_TOKEN --virtual-repo VIRTUAL_REPO_NAME --remote-repo REMOTE_REPO_NAME
```

### Arguments

- `--url`: The base URL of your Artifactory instance (e.g., https://artifactory.example.com)
- `--token`: Your Artifactory access token for authentication
- `--virtual-repo`: Name of the virtual repository you want to update
- `--remote-repo`: Name of the remote repository that should be placed after local repositories

### Example

```bash
python update_virtual_repo.py \
    --url https://artifactory.company.com \
    --token YOUR_ACCESS_TOKEN \
    --virtual-repo maven-virtual \
    --remote-repo maven-remote
```

## Security Note

- The script uses bearer token authentication
- SSL verification is disabled by default (suitable for internal/development environments)
- Never commit your access token to version control

## Error Handling

The script includes comprehensive error handling and logging:
- Validates repository types before modification
- Logs all operations with timestamps
- Provides detailed error messages for troubleshooting
- Returns appropriate exit codes (0 for success, 1 for failure)


