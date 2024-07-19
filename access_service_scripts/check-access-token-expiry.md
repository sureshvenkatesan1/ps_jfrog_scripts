
# Check Access Token Expiry

[check-access-token-expiry.py](check-access-token-expiry.py) checks the expiry dates of access tokens in a JFrog Platform Deployment (JPD) and lists 
those that are set to expire within a specified number of days. 

## Requirements

- Python 3.x
- `requests` library



## Usage

Run the script using the command line and provide the required arguments.

### Arguments

- `--source-jpd-url` (required): The URL of the source JPD.
- `--jpd-token` (required): The JPD access token.
- `--days-left` (required): The number of days left for token expiry.
- `--filename` (optional): The output filename where the list of tokens expiring within the specified days will be saved. Default is `token_less_days.txt`.
- `--include-subject` (optional): Include the last part of the subject in the output file.

### Example
If you want to print the token without subject in the output file:
```sh
python check-access-token-expiry.py --source-jpd-url "https://psemea.jfrog.io" --jpd-token "your_token" --days-left 30 --filename "token_less_30_days.txt"
```

If you want to print the token subject in the output file:
```sh
python check-access-token-expiry.py --source-jpd-url "https://psemea.jfrog.io" --jpd-token "your_token" --days-left 30 --filename "token_less_30_days.txt" --include-subject
```

### Script Details

1. The script sends a request to retrieve all tokens from the specified JPD URL.
2. For each token, it checks the expiry date.
3. If a token is set to expire within the specified number of days, its ID (and optionally the last part of the subject) are written to the specified output file in a tab-separated format.

### Notes

- Ensure that the provided JPD token has the necessary permissions to access the tokens API.
- The script will create or overwrite the specified output file with the list of token IDs that are expiring within the specified number of days.

