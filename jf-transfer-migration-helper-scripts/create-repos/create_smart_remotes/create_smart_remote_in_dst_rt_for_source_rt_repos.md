# Smart Remote Repository Creation Script

This [create_smart_remote_in_dst_rt_for_source_rt_repos.py(create_smart_remote_in_dst_rt_for_source_rt_repos.py) script automates the process of creating smart remote repositories in a destination JFrog Artifactory instance based on remote repositories in a source JFrog Artifactory instance.

## Description

The script `create_smart_remote_in_dst_rt_for_source_rt_repos.py` performs the following operations:
1. Fetches all remote repositories from the source Artifactory instance
2. For each remote repository found, creates a corresponding smart remote repository in the destination Artifactory
3. Maintains the same package type and repository layout configurations
4. Appends "-smart" suffix to the repository key in the destination instance

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- Access tokens for both source and destination Artifactory instances
- Admin privileges on both Artifactory instances

## Usage

```bash
python create_smart_remote_in_dst_rt_for_source_rt_repos.py \
  --source-url https://source.jfrog.io \
  --dest-url https://dest.jfrog.io \
  --source-token YOUR_SOURCE_TOKEN \
  --dest-token YOUR_DEST_TOKEN
```

### Command Line Arguments

- `--source-url`: URL of the source Artifactory instance
- `--dest-url`: URL of the destination Artifactory instance
- `--source-token`: Access token for the source Artifactory
- `--dest-token`: Access token for the destination Artifactory

## Example

If you have a remote repository named "maven-central" in your source Artifactory, the script will:
1. Detect the repository and its configuration
2. Create a new smart remote repository named "maven-central-smart" in the destination Artifactory
3. Configure it to point to the source repository's URL

## Error Handling

The script includes error handling for:
- Failed repository fetching
- Repository creation failures
- Missing download context paths
- Invalid credentials or access tokens

## Security Notes

- Never store access tokens in the script file
- Use environment variables or secure credential management systems
- Ensure HTTPS is used for both Artifactory instances
