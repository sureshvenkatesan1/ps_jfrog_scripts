# Artifactory Build Transfer Script

[buildMigrate.sh](buildMigrate.sh) This script facilitates the migration of builds from one JFrog Artifactory server to another. It allows you to specify the source and target Artifactory servers, along with optional parameters for customization.

## Prerequisites

Before using this script, ensure that you have the following:

1. [JFrog CLI](https://www.jfrog.com/getcli/) installed and configured with access to both source and target Artifactory servers.

## Usage
```bash
./buildMigrate.sh <source_server_name> <target_server_name> [diff_for_buildname] [diff_for_buildnumber] [createdafter]
```

## Configuration

You need to configure the script with the following variables:

- `source_server_name`: The name of the source Artifactory server.
- `target_server_name`: The name of the target Artifactory server.
- `diff_for_buildname` (optional): Set this to `true` if you want to compare build names between source and target 
  servers, otherwise set it to `false`. Default is `false`.
- `diff_for_buildnumber` (optional): Set this to `true` if you want to compare build numbers within the same build name, 
  otherwise set it to `false`. Default is `true`.
- `createdafter` (optional): Specify a date in the format "YYYY-MM-DD" to filter builds created after this date , 
  for example `"2023-03-21"`. BY default this parameter is empty,  so all builds will be considered.

## Usage

1. Make the script executable:

   ```bash
   chmod +x buildMigrate.sh
   ```

2. Execute the script:


  Below command migrates builds from the Artifactory server named psapac to the server named ramkannan, comparing build 
  names and not comparing build numbers, and including builds created after March 21, 2023.
   ```
   ./buildMigrate.sh psapac ramkannan true false "2023-03-21"
   ```
To migrate all the builds just use:
   ```bash
   ./buildMigrate.sh psapac ramkannan
  ``` 
## Functionality

- The script performs health checks on the source and target Artifactory servers using `jf rt ping`.

- If `diff_for_buildname` is set to `true`, it compares build names between source and target servers and generates a list of different build names.

- If `createdafter` is specified, the script filters builds created after the given date and transfers them to the target server. Otherwise, it transfers all builds.

- If `diff_for_buildnumber` is set to `true`, it compares build numbers within the same build name and transfers only the different build numbers.

- The script iterates through the build names and build numbers, transferring build information  from the source to the target Artifactory server.

## Notes

- The script uses `jq` for JSON parsing and manipulation, so make sure you have it installed on your system.

- The transferred build information is saved as JSON files in the current directory.

- The script will remove any existing `.txt` and `.json` files in the current directory before execution.

- Make sure to customize the script according to your specific requirements and validate its functionality in your environment before using it in production.

- This script is provided as-is and may require adjustments or enhancements to suit your exact use case.