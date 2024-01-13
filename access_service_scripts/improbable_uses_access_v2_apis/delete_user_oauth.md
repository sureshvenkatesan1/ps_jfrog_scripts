# Delete User Script for JFrog Artifactory (delete_user_oauth.sh)

This Bash script is designed to automate the process of deleting user accounts from a JFrog Artifactory instance. It allows you to remove specific user accounts based on certain criteria. This script is provided by JFrog for use in conjunction with their products and services.

## Usage

To use this script, follow the sample command below:

```bash
./delete_user_oauth.sh <JPD_URL> <JPD_AUTH_TOKEN>
```

Replace the placeholders with the following values:
- `<JPD_URL>`: The URL of the JFrog Platform Deployment (JPD) instance where you want to delete user accounts. Example: `https://ramkannan.jfrog.io`
- `<JPD_AUTH_TOKEN>`: The identity token for authentication in the JPD instance.

## Important Notes

- This script is provided by JFrog and is intended for use with JFrog products and services.
- The script uses the `jq` command-line tool to process JSON data, so ensure that `jq` is installed on your system.
- The script will remove any existing `.txt` and `.json` files in the current directory.
- User accounts with the realm "internal" and matching the specified criteria (in this case, having email domains containing "@skyral.io") will be deleted.
- The script iterates through each matching user account and sends a DELETE request to remove the user from the JPD instance.
- The script exits on any failures during execution.
- No warranties or conditions are provided with this script, and it is used at your own risk.

## License

JFrog grants you a non-exclusive, non-transferable right to use this code solely in connection with your use of a JFrog product or service. For details, refer to the provided license information in the script.

For further assistance or information, please refer to JFrog's official documentation or support channels.