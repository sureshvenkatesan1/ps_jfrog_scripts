# JPD Configuration Comparison Script

## Overview

The [compare_2_jpd_configs_v2.py](compare_2_jpd_configs_v2.py) script compares the configurations of two JFrog Platform Deployments (JPDs) by fetching data from various endpoints and comparing the results.

The entities compared include repositories, users, groups, permissions, tokens, projects, builds, property sets, Xray watches, policies, and ignore rules.

 To compare the permisisons the script determines the appropriate permissions API endpoint based on the Artifactory version of each JPD.

## Requirements

- Python 3.x
- `requests` library (`pip install requests`)
- `tabulate` library (`pip install tabulate`)



## Usage

### Running the Script

Execute the script with the required arguments:

```sh
python3 compare_2_jpd_configs.py <jpd_url1> <jpd_token1> <jpd_url2> <jpd_token2> <output_file>
```
### Command-Line Arguments

- `jpd_url1`: URL of the first JPD.
- `jpd_token1`: Token for accessing the first JPD.
- `jpd_url2`: URL of the second JPD.
- `jpd_token2`: Token for accessing the second JPD.
- `output_file`: File to write the differences to.

### Example

```sh
python3 compare_2_jpd_configs.py https://serverid1.jfrog.io ABC123 https://serverid2.jfrog.io XYZ789 differences_output.txt
```

In this example:
- `https://serverid1.jfrog.io` is the URL of the first JPD.
- `ABC123` is the token for accessing the first JPD.
- `https://serverid2.jfrog.io` is the URL of the second JPD.
- `XYZ789` is the token for accessing the second JPD.
- `differences_output.txt` is the file where the differences will be written.

## How It Works

1. **Fetch Artifactory Version**: The script uses the API endpoint `/artifactory/api/system/version` to fetch the Artifactory version for each JPD.
2. **Determine Permissions Endpoint**: Based on the Artifactory version, the script determines the appropriate permissions API endpoint:
   - For versions `>= 7.72.0`: `/access/api/v2/permissions`
   - For versions `< 7.72.0`: `/artifactory/api/v2/security/permissions`
3. **Collect Data**: The script collects data from various endpoints for both JPDs.
4. **Compare Data**: The script compares the collected data and identifies differences.
5. **Output Differences**: The differences are displayed in tabular format and written to the specified output file.

## Log Output

The script logs the usage of the permissions API for each JPD, making it clear which API endpoint is being used for which JPD, along with the version:

```plaintext
Using permissions API '/access/api/v2/permissions' for JPD1 at 'https://serverid1.jfrog.io' with version 7.88.0
Using permissions API '/access/api/v2/permissions' for JPD2 at 'https://serverid2.jfrog.io' with version 7.88.0
```
The script outputs the differences between the two JPDs in a tabular format, including entity types, entities common to both JPDs, entities unique to each JPD, and the count difference of entities between JPDs.
An example report is in [jpd_diff.txt](output/jpd_diff.txt) and [output_v2.txt](output/output_v2.txt)

## Troubleshooting

- Ensure that the provided URLs and tokens are correct and have the necessary permissions to access the endpoints.
- If you encounter any errors, refer to the error messages printed by the script for troubleshooting. The script includes debug information to help identify issues with API calls and data parsing.