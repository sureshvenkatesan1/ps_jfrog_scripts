# JPD Data Collection Script

This shell script is designed to collect data from a JFrog Platform Deployment (JPD) and generate a report. It 
retrieves various configurations and information from the specified JPD URL using JFrog CLI commands and outputs the 
collected data to a text file .

## Usage

```bash
bash ./jpd-data-collection.sh <JPD_URL> <JPD_TOKEN> <TYPE> [DETAILS]
```

- `<JPD_URL>`: URL of the JPD.
- `<JPD_TOKEN>`: Access token for authenticating with the JPD.
- `<TYPE>`: Type of JPD, either `sh` for self-hosted or `saas` for SaaS.
- `[DETAILS]`: Optional argument. Specify `true` to include detailed information in the report.

## Prerequisites

- JFrog CLI installed and configured.
- `jq` tool for parsing JSON responses.

## Disclaimer

This script is provided by JFrog and is intended for use solely in connection with JFrog products or services. It is provided 'as-is' without any warranties or conditions.

## Description

This script performs the following tasks:

1. Sets up JFrog CLI configurations for the specified JPD.
2. Retrieves system information including system ping and configuration.
3. Collects license information or URL base, license, and web server details based on the type of JPD.
4. Retrieves Artifactory version and package types currently used.
5. Retrieves repository information including local, remote, virtual, and federated repositories.
6. Retrieves storage information including binaries count, size, artifacts count, and size.
7. Identifies the largest file size and checks if it exceeds a certain threshold.
8. Finds Docker repositories with names containing '.' or '_'.
9. Collects access entities such as users, groups, permissions, and tokens.
10. Retrieves project information and associated builds.
11. Retrieves property sets and Xray configuration details including watches, policies, and ignore rules if Xray is enabled.

## Output

The script generates a report file named `jpd-data-collection.txt` containing the collected data from the JPD. The report includes various sections such as system information, license details, repository information, storage details, access entities, project details, and Xray configuration.
An example report is in [jpd-data-collection.txt](output/jpd-data-collection.txt)

## Notes

- Make sure to replace `<JPD_URL>` and `<JPD_TOKEN>` with the actual URL and token of your JPD.
- Specify the correct `<TYPE>` parameter (`sh` or `saas`) to indicate the type of JPD.
- You can optionally specify `[DETAILS]` as `true` to include detailed information in the report.