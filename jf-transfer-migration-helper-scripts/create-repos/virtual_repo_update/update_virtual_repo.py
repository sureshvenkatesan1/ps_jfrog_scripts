import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import sys
from typing import Dict, List
import argparse
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArtifactoryRepoManager:
    def __init__(self, artifactory_url: str, access_token: str):
        self.artifactory_url = artifactory_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        self.session = requests.Session()
        # Disable SSL verification for the session
        self.session.verify = False
        self.session.headers.update(self.headers)

    def get_repo_config(self, repo_name: str) -> Dict:
        """Get repository configuration."""
        url = f"{self.artifactory_url}/artifactory/api/repositories/{repo_name}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repository configuration for {repo_name}: {str(e)}")
            raise

    """
    Update virtual repository configuration.

    This method updates the repository list in the specified virtual
    repository configuration by moving the specified remote repository
    after all local repositories. The repository list is updated by
    sending a POST request to the repositories/{virtual_repo} endpoint
    with the modified repository configuration.

    :param virtual_repo: The name of the virtual repository to update.
    :param remote_repo: The name of the remote repository to move after
    local repositories.
    :return: True if the update was successful, False otherwise.
    """
    def update_virtual_repo(self, virtual_repo: str, remote_repo: str) -> bool:
        """Update virtual repository configuration."""
        try:
            # Get current virtual repo configuration
            repo_config = self.get_repo_config(virtual_repo)
            
            if repo_config.get('rclass') != 'virtual':
                logger.error(f"{virtual_repo} is not a virtual repository")
                return False

            # Get current repository list
            current_repos = repo_config.get('repositories', [])
            
            # Get repository types and create new repository list
            local_repos = []
            other_repos = []
            
            for repo in current_repos:
                try:
                    repo_info = self.get_repo_config(repo)
                    if repo_info.get('rclass') == 'local':
                        local_repos.append(repo)
                    elif repo != remote_repo:  # Don't add remote_repo here to avoid duplicates
                        other_repos.append(repo)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Could not get repository info for {repo}: {str(e)}")
                    other_repos.append(repo)

            # Create new repository list with remote_repo after local repos
            new_repos = local_repos + [remote_repo] + other_repos
            
            # Update repository configuration
            repo_config['repositories'] = new_repos
            
            # Send update request
            update_url = f"{self.artifactory_url}/artifactory/api/repositories/{virtual_repo}"
            response = self.session.post(update_url, json=repo_config)
            response.raise_for_status()
            
            logger.info(f"Successfully updated {virtual_repo} configuration")
            logger.info(f"New repository order: {new_repos}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update repository configuration: {str(e)}")
            return False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Update Artifactory virtual repository configuration'
    )
    parser.add_argument(
        '--url',
        required=True,
        help='Artifactory URL (e.g., https://artifactory.example.com)'
    )
    parser.add_argument(
        '--token',
        required=True,
        help='Artifactory access token'
    )
    parser.add_argument(
        '--virtual-repo',
        required=True,
        help='Name of the virtual repository to update'
    )
    parser.add_argument(
        '--remote-repo',
        required=True,
        help='Name of the remote repository to add after local repositories'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    try:
        repo_manager = ArtifactoryRepoManager(args.url, args.token)
        success = repo_manager.update_virtual_repo(args.virtual_repo, args.remote_repo)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 