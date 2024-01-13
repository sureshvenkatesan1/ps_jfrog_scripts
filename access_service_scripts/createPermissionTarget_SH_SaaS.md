# Create Permission Target Script for Artifactory (createPermissionTarget_SH_SaaS.sh)

This Bash script is designed to automate the process of creating and copying permission targets in JFrog Artifactory. It enables you to replicate permission targets from a source Artifactory instance to a target Artifactory instance. This script is provided by JFrog for use in conjunction with their products and services.

## Usage

To use this script, follow the sample command below:

```bash
./createPermissionTarget_SH_SaaS.sh <SOURCE_JPD_URL> <TARGET_JPD_URL> <USER_NAME> <SOURCE_JPD_AUTH_TOKEN> <TARGET_JPD_AUTH_TOKEN>
```

Replace the placeholders with the following values:
- `<SOURCE_JPD_URL>`: The URL of the source JFrog Platform Deployment (JPD) instance. Example: `https://ramkannan.jfrog.io`
- `<TARGET_JPD_URL>`: The URL of the target JPD instance where you want to create the permission targets. Example: `http://35.208.78.203:8082`
- `<USER_NAME>`: Your username in the source JPD instance. Example: `admin`
- `<SOURCE_JPD_AUTH_TOKEN>`: The identity token for authentication in the source JPD instance.
- `<TARGET_JPD_AUTH_TOKEN>`: The identity token for authentication in the target JPD instance.

## Important Notes

- This script is provided by JFrog and is intended for use with JFrog products and services.
- The script uses the `jq` command-line tool to process JSON data, so ensure that `jq` is installed on your system.
- The script will remove any existing `.txt` and `.json` files in the current directory.
- Permission targets with the name "INTERNAL" are excluded from the copying process.
- The script iterates through each permission target, downloads its JSON representation from the source, and uploads it to the target.
- The script exits on any failures during execution.
- No warranties or conditions are provided with this script, and it is used at your own risk.

## License

JFrog grants you a non-exclusive, non-transferable right to use this code solely in connection with your use of a JFrog product or service. For details, refer to the provided license information in the script.

For further assistance or information, please refer to JFrog's official documentation or support channels.