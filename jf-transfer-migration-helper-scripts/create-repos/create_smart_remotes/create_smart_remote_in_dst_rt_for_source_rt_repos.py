import requests
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Create smart remotes in destination Artifactory for source Artifactory repos'
    )
    parser.add_argument(
        '--source-url',
        required=True,
        help='Source Artifactory URL (e.g., https://source.jfrog.io)'
    )
    parser.add_argument(
        '--dest-url',
        required=True,
        help='Destination Artifactory URL (e.g., https://dest.jfrog.io)'
    )
    parser.add_argument(
        '--source-token',
        required=True,
        help='Access token for source Artifactory'
    )
    parser.add_argument(
        '--dest-token',
        required=True,
        help='Access token for destination Artifactory'
    )
    return parser.parse_args()

def get_all_remote_repositories(source_url, source_token):
    url = f"{source_url}/artifactory/api/repositories"
    headers = {
        'Authorization': f'Bearer {source_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        all_repos = response.json()
        # Filter for remote repositories based on 'type' key
        remote_repos = [repo for repo in all_repos if repo.get('type') == 'REMOTE']
        return remote_repos
    else:
        print(f"Error: Failed to get repositories. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

def create_smart_remote_repo(repo_config, source_url, dest_url, dest_token):
    if not repo_config:
        print("No repository configuration provided.")
        return

    repo_key = repo_config['key']
    url = f"{source_url}/artifactory/{repo_key}"
    headers = {
        'Authorization': f'Bearer {dest_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "rclass": "remote",
        "packageType": repo_config.get("packageType", "maven"),  # default to Maven if not specified
        "url": url,  # Use the source URL here without "smart" suffix
        "repoLayoutRef": repo_config.get("repoLayoutRef", "maven-2-default"),
        "key": f"{repo_key}-smart"  # Add the "smart" suffix to the key
    }

    # Add mandatory field for NuGet repositories using the source downloadContextPath
    if repo_config.get("packageType") == "nuget":
        # Ensure to fetch downloadContextPath from the source config, defaulting to repo_key if not found
        download_context_path = repo_config.get("downloadContextPath")
        if download_context_path is None:
            print(f"Warning: downloadContextPath not found for {repo_key}. Falling back to repo_key.")
            download_context_path = repo_key  # or handle as needed
        payload["downloadContextPath"] = download_context_path  # Use the source downloadContextPath

    response = requests.put(f"{dest_url}/artifactory/api/repositories/{repo_key}-smart", headers=headers, json=payload)
    
    if response.status_code in [200, 201]:  # Check for success (200 or 201)
        print(f"Successfully created smart remote repository: {repo_key}-smart")
    else:
        print(f"Failed to create repository {repo_key}-smart: {response.status_code} - {response.text}")

if __name__ == "__main__":
    args = parse_arguments()
    
    # Get all remote repositories from the source
    remote_repositories = get_all_remote_repositories(args.source_url, args.source_token)
    
    if not remote_repositories:
        print("No remote repositories found in the source Artifactory.")
        sys.exit(0)
        
    print(f"Found {len(remote_repositories)} remote repositories.")
    for repo in remote_repositories:
        print(f"Processing repository: {repo['key']}")
        create_smart_remote_repo(repo, args.source_url, args.dest_url, args.dest_token)