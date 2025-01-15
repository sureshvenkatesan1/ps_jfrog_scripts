# Create Smart Remote Repository Script

This script facilitates the creation of remote repositories across two Artifactory instances. It performs two main operations:
1. Creates a remote repository in Artifactory2 using the configuration from an existing repository in Artifactory1
2. Creates a corresponding smart remote repository in Artifactory1 that points to the newly created repository in Artifactory2

## Prerequisites

- Python 3.6 or higher
- `requests` library

## Installation

1. Create and activate a virtual environment:

```bash
# Linux/Mac
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

2. Install required packages:

```bash
pip install requests
```

## Usage

The script requires several parameters to be passed as command-line arguments:

```bash
python create_smart_remote_in_rt1_and_remote_in_rt2.py \
    --reponame <repository-name> \
    --source-url <artifactory1-url> \
    --dest-url <artifactory2-url> \
    --source-token <artifactory1-token> \
    --dest-token <artifactory2-token> \
    --username <username-for-smart-remote> \
    --password_rt1 <password-for-smart-remote> \
    --password_rt2 <password-for-new-remote>
```

### Parameters

- `--reponame`: Name of the existing remote repository in Artifactory1
- `--source-url`: URL of Artifactory1 (e.g., https://artifactory1.example.com)
- `--dest-url`: URL of Artifactory2 (e.g., https://artifactory2.example.com)
- `--source-token`: Admin access token for Artifactory1
- `--dest-token`: Admin access token for Artifactory2
- `--username`: Username to use in the smart remote repository in Artifactory1
- `--password_rt1`: Password to use in the smart remote repository in Artifactory1
- `--password_rt2`: Password to use in the new remote repository in Artifactory2

### Example

```bash
python create_smart_remote_in_rt1_and_remote_in_rt2.py \
    --reponame maven-central \
    --source-url https://artifactory1.company.com \
    --dest-url https://artifactory2.company.com \
    --source-token eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiw... \
    --dest-token eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiw... \
    --username admin \
    --password_rt1 password123 \
    --password_rt2 password456
```

This example will:
1. Create a remote repository named `maven-central` in Artifactory2 using the configuration from Artifactory1
2. Create a smart remote repository named `maven-central-smart` in Artifactory1 that points to the new repository in Artifactory2

## Logging

The script includes comprehensive logging functionality:

- All operations are logged to both console output and `output.log`
- Errors are additionally logged to `errors.log`
- Log files use rotation with a maximum size of 10MB and keep up to 5 backup files

### Log Files

- `output.log`: Contains all INFO level and above messages
- `errors.log`: Contains only ERROR level messages

## Error Handling

The script includes robust error handling:
- Validates all required parameters
- Checks HTTP response status codes
- Logs detailed error messages
- Exits gracefully with appropriate error messages when critical operations fail

## Note

Ensure that:
1. Both Artifactory instances are accessible from the machine running the script
2. The provided access tokens have sufficient permissions to create repositories
3. The repository name exists in Artifactory1
4. The username and passwords provided meet the security requirements of both Artifactory instances
