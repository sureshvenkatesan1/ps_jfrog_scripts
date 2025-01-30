#!/usr/bin/env python3

import requests
import argparse
import json
import sys
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
def setup_logging():
    logger = logging.getLogger('ArtifactorySmartRemote')
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create and configure stream handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Create and configure file handler for output.log
    output_handler = RotatingFileHandler('output.log', maxBytes=10485760, backupCount=5)
    output_handler.setFormatter(formatter)
    output_handler.setLevel(logging.INFO)
    logger.addHandler(output_handler)

    # Create and configure file handler for errors.log
    error_handler = RotatingFileHandler('errors.log', maxBytes=10485760, backupCount=5)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    return logger

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Create a remote repository in Artifactory2 and a corresponding smart remote in Artifactory1'
    )
    parser.add_argument(
        '--reponame',
        required=True,
        help='The existing remote repository name in Artifactory1'
    )
    parser.add_argument(
        '--source-url',
        required=True,
        help='URL of the Artifactory1'
    )
    parser.add_argument(
        '--dest-url',
        required=True,
        help='URL of the Artifactory2'
    )
    parser.add_argument(
        '--source-token',
        required=True,
        help='Admin Access token for Artifactory1'
    )
    parser.add_argument(
        '--dest-token',
        required=True,
        help='Admin Access token for Artifactory2'
    )
    parser.add_argument(
        '--username',
        required=True,
        help='Username to use in smart remote repository in Artifactory1'
    )
    parser.add_argument(
        '--password_rt1',
        required=True,
        help='Password to use in smart remote repository in Artifactory1'
    )
    parser.add_argument(
        '--password_rt2',
        required=True,
        help='Password to use in new remote repository in Artifactory2'
    )
    parser.add_argument(
        '--project-key',
        required=True,
        help='Project key to use as prefix for repository names (e.g., "public")'
    )
    return parser.parse_args()

def get_repository_config(source_url, source_token, repo_name):
    logger = logging.getLogger('ArtifactorySmartRemote')
    url = f"{source_url}/artifactory/api/repositories/{repo_name}"
    headers = {
        'Authorization': f'Bearer {source_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Successfully retrieved configuration for repository: {repo_name}")
        return response.json()
    else:
        error_msg = f"Error: Failed to get repository configuration. Status code: {response.status_code}. Response: {response.text}"
        logger.error(error_msg)
        sys.exit(1)

def create_remote_in_rt2(dest_url, dest_token, repo_name, repo_config, password, project_key):
    logger = logging.getLogger('ArtifactorySmartRemote')
    
    # Update the password if it's a remote repository
    if repo_config.get('rclass') == 'remote':
        repo_config['password'] = password
        logger.info(f"Updated password for repository: {repo_name}")

    # Check if reponame starts with project_key
    if not repo_name.startswith(project_key):
        repo_config.pop("projectKey", None)  # Remove 'projectKey' if it exists
        new_repo_name = repo_name
    else:       
        # Add project key prefix to repository name
        new_repo_name = f"{project_key}-{repo_name}"
        # Update the key in the config to include the project prefix
        repo_config['key'] = new_repo_name
    
    url = f"{dest_url}/artifactory/api/repositories/{new_repo_name}"
    headers = {
        'Authorization': f'Bearer {dest_token}',
        'Content-Type': 'application/json'
    }



    response = requests.put(url, headers=headers, json=repo_config)
    
    if response.status_code in [200, 201]:
        logger.info(f"Successfully created remote repository {new_repo_name} in Artifactory2")
        return True, new_repo_name
    else:
        error_msg = f"Failed to create repository {new_repo_name}: {response.status_code} - {response.text}"
        logger.error(error_msg)
        return False, None

def create_smart_remote_in_rt1(source_url, source_token, repo_name, username, password, dest_url, project_key):
    logger = logging.getLogger('ArtifactorySmartRemote')
    # Check if reponame starts with project_key
    if not repo_name.startswith(project_key):
        smart_repo_key = f"{repo_name}-smart"
    else:
        smart_repo_key = f"{project_key}-{repo_name}-smart"
    url = f"{source_url}/artifactory/api/repositories/{smart_repo_key}"
    headers = {
        'Authorization': f'Bearer {source_token}',
        'Content-Type': 'application/json'
    }

    # Get the original repo config to maintain package type and other settings
    original_config = get_repository_config(source_url, source_token, repo_name)
    logger.info(f"Creating smart remote repository with key: {smart_repo_key}")
    
    original_config["key"] = smart_repo_key
    original_config["username"] =  username
    original_config["password"] =  password
    original_config["packageType"] =  original_config.get("packageType", "maven")
    #original_config["repositoryLayoutRef"] =  original_config.get("repositoryLayoutRef", "maven-2-default")
    original_config["repoLayoutRef"] =  original_config.get("repoLayoutRef", "maven-2-default")
    original_config["curated"] =  False
    original_config["sendContext"] = True
    original_config["passThrough"] =  False
    
    if not repo_name.startswith(project_key):
        original_config.pop("projectKey", None)
        original_config["url"] = f"{dest_url}/artifactory/{repo_name}"
    else:
        original_config["projectKey"] = project_key
        original_config["url"] = f"{dest_url}/artifactory/{project_key}-{repo_name}"

    # payload = {
    #     "key": smart_repo_key,
    #     "rclass": "remote",
    #     "packageType": original_config.get("packageType", "maven"),
    #     "username": username,
    #     "password": password,
    #     "repositoryLayoutRef": original_config.get("repositoryLayoutRef", "maven-2-default")
    # }
    # # Check if reponame starts with project_key
    # if repo_name.startswith(project_key):
    #     payload["projectKey"] = project_key
    #     payload["url"] = f"{dest_url}/artifactory/{project_key}-{repo_name}"
    # else:
    #     payload["url"] = f"{dest_url}/artifactory/{repo_name}"

    # # Add mandatory field for NuGet repositories
    if original_config.get("packageType") == "nuget":
        original_config["downloadContextPath"] = original_config.get("downloadContextPath", repo_name)
        logger.info(f"Added NuGet specific configuration for repository: {smart_repo_key}")

    logger.info(f"Payload for creating smart remote repository: {json.dumps(original_config, indent=4)}")

    response = requests.put(url, headers=headers, json=original_config)
    
    if response.status_code in [200, 201]:
        logger.info(f"Successfully created smart remote repository: {smart_repo_key}")
        return True
    else:
        error_msg = f"Failed to create smart remote repository {smart_repo_key}: {response.status_code} - {response.text}"
        logger.error(error_msg)
        return False

def main():
    logger = logging.getLogger('ArtifactorySmartRemote')
    args = parse_arguments()
    logger.info(f"Starting repository creation process for: {args.reponame}")

    # Get the original repository configuration
    repo_config = get_repository_config(args.source_url, args.source_token, args.reponame)


    # Create remote repository in Artifactory2
    success, prefixed_repo_name = create_remote_in_rt2(
        args.dest_url,
        args.dest_token,
        args.reponame,
        repo_config,
        args.password_rt2,
        args.project_key
    )

    if success:
        # Create smart remote repository in Artifactory1
        create_smart_remote_in_rt1(
            args.source_url,
            args.source_token,
            args.reponame,
            args.username,
            args.password_rt1,
            args.dest_url,
            args.project_key
        )
    else:
        logger.error(f"Failed to create remote repository in Artifactory2. Skipping smart remote creation.")

if __name__ == "__main__":
    logger = setup_logging()
    main()
