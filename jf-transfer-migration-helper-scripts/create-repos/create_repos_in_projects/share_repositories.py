import json
import requests
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_repositories_by_type(repo_type, token, base_url):
    """Get repositories of specific type using JFrog API"""
    url = f"{base_url}/repositories?type={repo_type}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        return [repo['key'] for repo in response.json()]
    else:
        logging.error(f"Failed to get {repo_type} repositories: {response.status_code} - {response.text}")
        return []

def share_repository_with_project(repo_key, project_name, token, base_url):
    url = f"{base_url}/{project_name}/repositories/{repo_key}/share"
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"})
    return response.status_code, response.json()

def share_repository_with_all(repo_key, token, base_url):
    url = f"{base_url}/repositories/{repo_key}/share-all"
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"})
    return response.status_code, response.json()

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Share repositories with projects")
    parser.add_argument('--project_report', required=True, help='Path to the project_report.json file')
    parser.add_argument('--token', required=True, help='Authorization token for JFrog API')
    parser.add_argument('--base_url', required=True, help='Base URL for JFrog API')
    parser.add_argument('--project_name', help='Specific project name to process')
    parser.add_argument('--repo_key', help='Specific repository key to process')
    parser.add_argument('--repo_type', choices=['local', 'remote', 'virtual', 'federated'],
                      help='Repository type to process (local, remote, virtual, or federated)')

    args = parser.parse_args()
    
    with open(args.project_report, 'r') as file:
        project_data = json.load(file)

    # If repo_type is specified, get repositories of that type
    repo_type_filter = None
    if args.repo_type:
        logging.info(f"Getting repositories of type: {args.repo_type}")
        repo_type_filter = get_repositories_by_type(args.repo_type, args.token, args.base_url)
        logging.info(f"Found {len(repo_type_filter)} repositories of type {args.repo_type}")

    if args.project_name:
        logging.info(f"Processing specific project: {args.project_name}")
        details = project_data.get(args.project_name)
        if details:
            repo_types_map = {
                'local': "shared_repositories_local",
                'remote': "shared_repositories_remote",
                'virtual': "shared_repositories_virtual",
                'federated': "shared_repositories_federated"
            }
            
            # Process only specified repo type if provided
            if args.repo_type:
                repos = details.get(repo_types_map[args.repo_type], [])
                filtered_repos = [repo for repo in repos if repo in repo_type_filter]
                
                if args.repo_type == 'virtual' and details.get("shared_with_all_projects"):
                    for repo in filtered_repos:
                        status_code, response = share_repository_with_all(repo, args.token, args.base_url)
                        logging.info(f"Shared {repo} with all projects: {status_code} - {response}")
                else:
                    for repo in filtered_repos:
                        status_code, response = share_repository_with_project(repo, args.project_name, args.token, args.base_url)
                        logging.info(f"Shared {repo} with project {args.project_name}: {status_code} - {response}")
            else:
                # Original processing logic for all repo types
                # Share local repositories
                for repo in details.get("shared_repositories_local", []):
                    status_code, response = share_repository_with_project(repo, args.project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {args.project_name}: {status_code} - {response}")

                # Share remote repositories
                for repo in details.get("shared_repositories_remote", []):
                    status_code, response = share_repository_with_project(repo, args.project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {args.project_name}: {status_code} - {response}")

                # Share federated repositories
                for repo in details.get("shared_repositories_federated", []):
                    status_code, response = share_repository_with_project(repo, args.project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {args.project_name}: {status_code} - {response}")

                # Share with all projects if applicable
                if details.get("shared_with_all_projects"):
                    for repo in details.get("shared_repositories_virtual", []):
                        status_code, response = share_repository_with_all(repo, args.token, args.base_url)
                        logging.info(f"Shared {repo} with all projects: {status_code} - {response}")
        else:
            logging.warning(f"No details found for project: {args.project_name}")

    elif args.repo_key:
        logging.info(f"Processing specific repository: {args.repo_key}")
        for project_name, details in project_data.items():
            if args.repo_key in details.get("shared_repositories_local", []):
                status_code, response = share_repository_with_project(args.repo_key, project_name, args.token, args.base_url)
                logging.info(f"Shared {args.repo_key} with project {project_name}: {status_code} - {response}")

            if details.get("shared_with_all_projects"):
                status_code, response = share_repository_with_all(args.repo_key, args.token, args.base_url)
                logging.info(f"Shared {args.repo_key} with all projects: {status_code} - {response}")

    else:
        logging.info("Processing all projects.")
        for project_name, details in project_data.items():
            repo_types_map = {
                'local': "shared_repositories_local",
                'remote': "shared_repositories_remote",
                'virtual': "shared_repositories_virtual",
                'federated': "shared_repositories_federated"
            }
            
            # Process only specified repo type if provided
            if args.repo_type:
                repos = details.get(repo_types_map[args.repo_type], [])
                filtered_repos = [repo for repo in repos if repo in repo_type_filter]
                
                if args.repo_type == 'virtual' and details.get("shared_with_all_projects"):
                    for repo in filtered_repos:
                        status_code, response = share_repository_with_all(repo, args.token, args.base_url)
                        logging.info(f"Shared {repo} with all projects: {status_code} - {response}")
                else:
                    for repo in filtered_repos:
                        status_code, response = share_repository_with_project(repo, project_name, args.token, args.base_url)
                        logging.info(f"Shared {repo} with project {project_name}: {status_code} - {response}")
            else:
                # Original processing logic for all repo types
                # Share local repositories
                for repo in details.get("shared_repositories_local", []):
                    status_code, response = share_repository_with_project(repo, project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {project_name}: {status_code} - {response}")

                # Share remote repositories
                for repo in details.get("shared_repositories_remote", []):
                    status_code, response = share_repository_with_project(repo, project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {project_name}: {status_code} - {response}")

                # Share federated repositories
                for repo in details.get("shared_repositories_federated", []):
                    status_code, response = share_repository_with_project(repo, project_name, args.token, args.base_url)
                    logging.info(f"Shared {repo} with project {project_name}: {status_code} - {response}")

                # Share with all projects if applicable
                if details.get("shared_with_all_projects"):
                    for repo in details.get("shared_repositories_virtual", []):
                        status_code, response = share_repository_with_all(repo, args.token, args.base_url)
                        logging.info(f"Shared {repo} with all projects: {status_code} - {response}")

if __name__ == "__main__":
    main()