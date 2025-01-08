# Delete Smart Repositories Script

This[delete_smart_repos.py](delete_smart_repos.py) script provides functionality to safely delete repositories from a JFrog Artifactory instance that match a specific suffix (default: '-smart'). It includes a dry-run mode by default for safety.

## Description

The script `delete_smart_repos.py` performs the following operations:
1. Connects to a specified JFrog Artifactory instance
2. Retrieves a list of all repositories
3. Identifies repositories that end with the specified suffix
4. In dry-run mode (default), lists repositories that would be deleted without making changes
5. When not in dry-run mode, deletes the identified repositories

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Access token with admin privileges for the Artifactory instance

## Usage

```bash
# Dry run (default) - shows what would be deleted without making changes
python delete_smart_repos.py \
  --artifactory-url https://artifactory.example.com/artifactory \
  --access-token YOUR_ACCESS_TOKEN


# Dry run Delete repositories with a different suffix
python delete_smart_repos.py \
  --artifactory-url https://artifactory.example.com/artifactory \
  --access-token YOUR_ACCESS_TOKEN \
  --suffix "custom-suffix"

# Actually delete repositories with suffix '-smart' (disable dry-run)
python delete_smart_repos.py \
  --artifactory-url https://artifactory.example.com/artifactory \
  --access-token YOUR_ACCESS_TOKEN \
  --dry-run false

### Command Line Arguments

- `--artifactory-url` (Required): URL of the Artifactory instance
- `--access-token` (Required): Access token for Artifactory authentication
- `--suffix` (Optional): Suffix to match for repository deletion (default: '-smart')
- `--dry-run` (Optional): Flag to preview deletions without executing them (default: True)

## Safety Features

1. **Dry Run Mode**: Enabled by default to prevent accidental deletions
2. **Confirmation**: Lists all repositories that would be deleted before proceeding
3. **Error Handling**: Proper error messages and status codes for troubleshooting

## Example Output

```
Fetching repositories from: https://artifactory.example.com/artifactory/api/repositories
Total repositories retrieved: 25
Repositories matching suffix '-smart': ['maven-central-smart', 'npm-remote-smart']

DRY RUN - No repositories will be deleted
```

## Security Notes

- Never commit access tokens to version control
- Use HTTPS URLs for Artifactory instances
- Ensure proper access controls and permissions
