import subprocess
import json
import argparse
"""
python repos_mapped_to_multiple_env.py --server-id mill --repo-type remote

"""
def fetch_and_process_repositories(server_id, repo_type):
    # Step 1: Get the list of repositories
    command = f'jf rt curl "/api/repositories?type={repo_type}" --server-id={server_id} | jq -r ".[]|.key"'
    repositories = subprocess.check_output(command, shell=True).decode().splitlines()

    # Step 2: Loop through the repositories and invoke the API
    for repo_name in repositories:
        api_url = f'/api/repositories/{repo_name} --server-id={server_id}'
        command = f'jf rt curl {api_url}'
        repo_config_json = subprocess.check_output(command, shell=True).decode()
        repo_config = json.loads(repo_config_json)

        # Step 3: Check for multiple values in "environments" list
        if len(repo_config.get('environments', [])) > 1:
            print(f'Repository with multiple environments: {repo_name}')

        # Step 4: Print repository name and "environments" list
        print(f'Repository: {repo_name}')
        print(f'Environments: {repo_config.get("environments", [])}')
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and process repositories.')
    parser.add_argument('--server-id', required=True, help='The server ID (e.g., mill)')
    parser.add_argument('--repo-type', required=True, help='The repository type (e.g., remote)')

    args = parser.parse_args()
    fetch_and_process_repositories(args.server_id, args.repo_type)
