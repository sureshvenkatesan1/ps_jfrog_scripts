import requests
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Delete repositories from JFrog Artifactory that match a specific suffix'
    )
    parser.add_argument(
        '--artifactory-url',
        required=True,
        help='Artifactory URL (e.g., https://artifactory.example.com/artifactory)'
    )
    parser.add_argument(
        '--access-token',
        required=True,
        help='Access token for Artifactory authentication'
    )
    parser.add_argument(
        '--suffix',
        default='-smart',
        help='Suffix to match for repository deletion (default: -smart)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List repositories that would be deleted without actually deleting them'
    )
    return parser.parse_args()

def delete_remote_repositories_with_suffix(artifactory_url, access_token, suffix='-smart', dry_run=True):
    # URL to get repositories
    url = f"{artifactory_url}/api/repositories"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get the list of all repositories
    print(f"Fetching repositories from: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        all_repos = response.json()
        print(f"Total repositories retrieved: {len(all_repos)}")
        
        # Filter for repositories that end with the specified suffix
        repos_to_delete = [repo for repo in all_repos if repo['key'].endswith(suffix)]
        print(f"Repositories matching suffix '{suffix}': {[repo['key'] for repo in repos_to_delete]}")
        
        if dry_run:
            print("\nDRY RUN - No repositories will be deleted")
            return
        
        if not repos_to_delete:
            print(f"No repositories found with suffix: {suffix}")
            return
            
        for repo in repos_to_delete:
            delete_url = f"{artifactory_url}/api/repositories/{repo['key']}"
            print(f"Deleting repository: {repo['key']} at {delete_url}")
            
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code == 200:
                print(f"Successfully deleted repository: {repo['key']}")
            else:
                print(f"Failed to delete repository {repo['key']}: {delete_response.status_code} - {delete_response.text}")
    else:
        print(f"Error retrieving repositories: {response.status_code} - {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_arguments()
    delete_remote_repositories_with_suffix(
        args.artifactory_url,
        args.access_token,
        args.suffix,
        args.dry_run
    )