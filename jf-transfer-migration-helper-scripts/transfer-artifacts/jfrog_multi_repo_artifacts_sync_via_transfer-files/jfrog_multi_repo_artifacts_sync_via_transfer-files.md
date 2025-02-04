# JFrog Multi-Repository Artifacts Sync Tool

This [jfrog_multi_repo_artifacts_sync_via_transfer-files.py](jfrog_multi_repo_artifacts_sync_via_transfer-files.py) tool facilitates the bulk transfer of artifacts from multiple repositories between Artifactory instances using the JFrog CLI's transfer-files command. It provides parallel processing capabilities and robust monitoring features.

## Features

- Parallel processing of multiple repositories
- Automatic detection and restart of stuck transfers
- Comprehensive logging system with both main and individual repository logs
- Configurable thread count per transfer
- Batch processing with configurable batch size
- Progress monitoring and status tracking
- Visual separation of log events with banner lines
- Detailed command execution logging

## Prerequisites

1. Python 3.x installed
2. JFrog CLI installed and configured
3. Source and target Artifactory server configurations set up in JFrog CLI
4. A text file (`repo_list.txt`) containing repository names to transfer (one per line)

## Installation

1. Clone or download the script
2. Ensure `repo_list.txt` is in the same directory as the script
3. Make sure JFrog CLI is properly configured with both source and target server credentials

## Usage

Basic usage:
```bash
python jfrog_multi_repo_artifacts_sync_via_transfer-files.py \
  --source <SOURCE_SERVER_ID> \
  --target <TARGET_SERVER_ID>
```

Full usage with all options:
```bash
python jfrog_multi_repo_artifacts_sync_via_transfer-files.py \
  --source <SOURCE_SERVER_ID> \
  --target <TARGET_SERVER_ID> \
  [--ignore-state=<true|false>] \
  [--filestore=<true|false>] \
  [--jf-path </path/to/jf>] \
  [--threads <number>] \
  [--timeout <seconds>] \
  [--batch-size <number>]
```

### Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| --source | Yes | - | Source Artifactory server ID |
| --target | Yes | - | Target Artifactory server ID |
| --ignore-state | No | false | Whether to ignore previous transfer state |
| --filestore | No | true | Whether to transfer filestore data |
| --jf-path | No | /usr/local/bin/jf | Path to JFrog CLI executable |
| --threads | No | 50 | Number of transfer threads per repository |
| --timeout | No | 600 | Timeout in seconds for detecting stuck processes |
| --batch-size | No | 4 | Number of repositories to process in parallel |

## Monitoring Progress

The script provides two types of logs for monitoring progress:

### 1. Main Log File

Located in the script directory as `transfer_main_YYYYMMDD_HHMMSS.log`

Contains:
- Overall process start/end times
- Current batch processing status
- Repository transfer start/completion times
- Number of restart attempts per repository
- Total runtime statistics
- Exact commands being executed for each repository
- Visual separators for important events

Example main log content:
```
JFrog Transfer Process Started at 2024-03-21 10:00:00
Source: source-server, Target: target-server
--------------------------------------------------------------------------------

Found 10 repositories to process
Processing in batches of 4
--------------------------------------------------------------------------------

[2024-03-21 10:00:01] Processing batch 1 of 3
Repositories in this batch: repo1, repo2, repo3, repo4

[2024-03-21 10:00:01] Starting transfer for repository: repo1
[2024-03-21 10:00:01] Executing command for repo1:
/usr/local/bin/jf rt transfer-files source-server target-server --include-repos repo1 --ignore-state=false --filestore=true
...
```

### 2. Individual Repository Logs

Located in `logs/jfrog-sync-YYYYMMDD_HHMMSS/jfrog_<repo_name>.out`

Contains:
- Detailed transfer logs for each repository
- JFrog CLI output and error messages
- Transfer start/end times in human-readable format
- Any restart events with timestamps
- Visual separators for restart events and errors

## State Management

The script maintains separate state directories for each repository under:
```
~/[target]/.jfrog-[repo_name]/
```

This ensures clean separation of state and configuration between different repository transfers.

## Error Handling

- Automatically detects and restarts stuck transfers after the specified timeout
- Maintains count of restart attempts in the main log
- Continues processing other repositories if one fails
- Visually separates error and restart events in logs with banner lines
- Logs exact commands being retried

## Example Usage

1. Create a repo_list.txt file:
```
maven-local
docker-local
npm-remote
pypi-virtual
```

2. Run the script:
```bash
python jfrog_multi_repo_artifacts_sync_via_transfer-files.py \
  --source artifactory-1 \
  --target artifactory-2 \
  --threads 100 \
  --timeout 300 \
  --batch-size 3
```
or
```bash
python jfrog_multi_repo_artifacts_sync_via_transfer-files.py \
  --source artifactory-1 \
  --target artifactory-2 \
  --ignore-state false \
  --filestore true \
  --threads 100 \
  --timeout 300 \
  --batch-size 3
```

3. Monitor progress:
```bash
tail -f transfer_main_20240321_100000.log
```

## Best Practices

1. Start with default settings for initial testing
2. Adjust batch-size based on available system resources
3. Set appropriate timeout values based on repository sizes
4. Monitor both main and individual repository logs
5. Keep repo_list.txt organized with one repository per line
6. Review the command output in the main log to verify correct parameters

## Troubleshooting

1. Check main log file for overall status and exact commands being executed
2. Review individual repository logs for specific transfer issues
3. Increase timeout if transfers are being restarted too frequently
4. Decrease batch-size if system resources are constrained
5. Ensure JFrog CLI configurations are correct for both source and target
6. Verify the command format in the logs matches the expected JFrog CLI syntax