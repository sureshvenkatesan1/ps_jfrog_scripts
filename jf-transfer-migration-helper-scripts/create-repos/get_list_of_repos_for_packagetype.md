
# get_list_of_repos_for_packagetype.sh

This [get_list_of_repos_for_packagetype.sh](get_list_of_repos_for_packagetype.sh) script retrieves a list of 
repository keys for a specified package type 
from a JFrog Artifactory server using 
the JFrog CLI. It parses the JSON output and prints the repository keys in a list format.

## Prerequisites

- JFrog CLI installed and configured
- `jq` installed for JSON parsing

## Usage

```sh
./get_list_of_repos_for_packagetype.sh <serverid> <packageType>
```

### Parameters

- `serverid`: The Server ID of the JFrog Artifactory server.
- `packageType`: The package type to filter the repositories (e.g., `Docker`, `Npm`, `Maven`).

### Example

```sh
./get_list_of_repos_for_packagetype.sh exampledev Docker
```

### Output

The script outputs a JSON array of repository keys for the specified package type. For example:

```json
["docker-qa-local", "docker-test-local"]
```

## Script Details

The script performs the following steps:

1. Checks if the correct number of arguments are provided. If not, it displays usage information and exits.
2. Assigns input arguments (`serverid` and `packageType`) to variables.
3. Invokes the JFrog CLI to get the list of repositories for the specified package type and parses the JSON output to extract the `key` values.
4. Prints the parsed `key` values in a JSON array format.

## Error Handling

If the script is not provided with the correct number of arguments, it will display the following usage information and exit:

```sh
Usage: ./get_list_of_repos_for_packagetype.sh <serverid> <packageType>
```

