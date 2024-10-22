# Compare 2 JPD Configs

The [compare_2_jpd_configs_v1.py](compare_2_jpd_configs_v1.py) script is designed to compare configurations between two JFrog Platform Deployments (JPDs) configurations.
It collects data from specified JPDs and displays the differences in a tabular format.

## Usage

```bash
python compare_2_jpd_configs_v1.py https://psazuse.jfrog.io $psazuse_token https://psemea.jfrog.io $psemea_token > jpd_diff.txt
```

Replace `$psazuse_token` and `$psemea_token` with your access tokens for the respective JPDs.

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)
- `tabulate` library (`pip install tabulate`)

## Description

This script retrieves configuration data from various entities in the specified JPDs and compares them. The entities include repositories, users, groups, permissions, tokens, projects, builds, property sets, Xray watches, policies, and ignore rules.

## Script Logic

- The script collects data from both JPDs specified via URLs and access tokens.
- It compares the collected data between the two JPDs.
- The differences are displayed in a tabular format showing entities common to both JPDs, entities unique to each JPD, and the count difference of entities between JPDs.

## Arguments

- `jpd_url1`: URL of the first JPD
- `jpd_token1`: Token for accessing the first JPD
- `jpd_url2`: URL of the second JPD
- `jpd_token2`: Token for accessing the second JPD

## Output

The script outputs the differences between the two JPDs in a tabular format, including entity types, entities common to both JPDs, entities unique to each JPD, and the count difference of entities between JPDs.
An example report is in [jpd_diff.txt](output/jpd_diff.txt)