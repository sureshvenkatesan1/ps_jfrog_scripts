
# find_docker_repos_exceeding_64_char_subdomain_setmeup_limit.py

This [find_docker_repos_exceeding_64_char_subdomain_setmeup_limit.py](find_docker_repos_exceeding_64_char_subdomain_setmeup_limit.py) filters Docker repository names to ensure they comply with AWS Route 53's limit on the length of top-level domains. AWS Route 53 restricts the length of the top-level domain to 64 characters, meaning the combined length of the server name and repository name (`<servername-reponame>`) cannot exceed 64 characters.

## Features

- Loads repository names from a JSON file.
- Prepends a customer name to each repository name.
- Filters out repository names that exceed the 64-character limit when combined with the customer name.
- Outputs the list of repositories that exceed the limit along with their lengths.

## Requirements

- Python 3.x

## Installation

1. Clone this repository or download the script.

2. Ensure you have Python 3.x installed.

## Usage

1. Prepare a JSON file containing a list of repository names. Example `repos.json`:

    ```json
    [
        "repo1",
        "repo2",
        "very-long-repository-name-that-will-exceed-the-limit"
    ]
    ```

2. Run the script with the JSON file and customer name as arguments:

    ```bash
    python find_docker_repos_exceeding_64_char_subdomain_setmeup_limit.py repos.json customername
    ```

3. The script will output the repositories that exceed the 64-character limit when combined with the customer name.

    Example output:

    ```plaintext
    AWS Route 53 restricts the length of the top-level domain to 64 characters. This means that the combined length of the server name and repository name (<servername-reponame>) cannot exceed 64 characters.
    Here are the repos that have this limit:
    Repository: very-long-repository-name-that-will-exceed-the-limit , Subdomain: customername-very-long-repository-name-that-will-exceed-the-limit, Length: 80
    ```

