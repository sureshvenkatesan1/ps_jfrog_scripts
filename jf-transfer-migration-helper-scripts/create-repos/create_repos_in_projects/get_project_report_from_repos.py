#!/usr/bin/env python3

import os
import sys
import json
import logging
import requests
import argparse
from typing import List, Dict, Optional
from urllib.parse import urljoin
from tabulate import tabulate
from tqdm import tqdm
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('project_report.log')
    ]
)
logger = logging.getLogger(__name__)

class ArtifactoryProjectReporter:
    def __init__(self, artifactory_url: str, token: str):
        self.artifactory_url = artifactory_url
        self.access_token = token
        
        if not self.artifactory_url or not self.access_token:
            logger.error("Artifactory URL and access token are required")
            sys.exit(1)
            
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_repositories_by_type(self, repo_type: Optional[str]) -> List[Dict]:
        """Get list of repositories, optionally filtered by type"""
        endpoint = urljoin(self.artifactory_url, f'/artifactory/api/repositories')
        params = {'type': repo_type.lower()} if repo_type else {}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            repos = response.json()
            if repo_type:
                logger.info(f"Found {len(repos)} repositories of type {repo_type}")
            else:
                logger.info(f"Found {len(repos)} total repositories")
            return repos
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repositories: {str(e)}")
            return []

    def get_repo_project_details(self, repo_name: str) -> Optional[Dict]:
        """Get project assignment details for a repository"""
        endpoint = urljoin(self.artifactory_url, f'/access/api/v1/projects/_/repositories/{repo_name}')
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching project details for {repo_name}: {str(e)}")
            return None

    def get_repo_details_parallel(self, repo_name: str, repos_type_map: Dict[str, str]) -> Optional[Dict]:
        """Get repository details with type information"""
        project_details = self.get_repo_project_details(repo_name)
        if project_details:
            return {
                'repository': repo_name,
                'type': repos_type_map.get(repo_name, 'Unknown'),
                'assigned_to': project_details.get('assigned_to', 'None'),
                'shared_with_projects': project_details.get('shared_with_projects', []),
                'shared_with_all_projects': project_details.get('shared_with_all_projects', False),
                'environments': project_details.get('environments', [])
            }
        return None

    def get_project_details(self, project_key: str) -> Optional[Dict]:
        """Get project details including display name"""
        endpoint = urljoin(self.artifactory_url, f'/access/api/v1/projects/{project_key}')
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching details for project {project_key}: {str(e)}")
            return None

    def generate_report(self, repo_filter: Optional[str], output_file: str = 'project_report.json', max_parallel: int = 10):
        """Generate report based on repository name or type"""
        repos_to_check = []
        repos_type_map = {}  # Store repository types
        
        if repo_filter is None:
            # Get all repositories without type filter
            repos = self.get_repositories_by_type(None)
            repos_to_check = [repo['key'] for repo in repos]
            repos_type_map = {repo['key']: repo['type'] for repo in repos}
        elif repo_filter.lower() in ['local', 'remote', 'federated', 'virtual']:
            # Get repositories by type
            repos = self.get_repositories_by_type(repo_filter)
            repos_to_check = [repo['key'] for repo in repos]
            repos_type_map = {repo['key']: repo['type'] for repo in repos}
        else:
            # Single repository
            repos_to_check = [repo_filter]
            # Get type for single repository
            repos = self.get_repositories_by_type(None)
            repos_type_map = {repo['key']: repo['type'] for repo in repos if repo['key'] == repo_filter}

        logger.info(f"Processing {len(repos_to_check)} repositories using {max_parallel} parallel threads...")
        
        report = []
        # Process repositories in parallel with progress bar
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(self.get_repo_details_parallel, repo_name, repos_type_map): repo_name 
                for repo_name in repos_to_check
            }
            
            with tqdm(total=len(repos_to_check), desc="Fetching repository details") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    repo_name = futures[future]
                    try:
                        result = future.result()
                        if result:
                            report.append(result)
                            logger.debug(f"Processed repository: {repo_name}")
                    except Exception as e:
                        logger.error(f"Error processing repository {repo_name}: {str(e)}")
                    finally:
                        pbar.update(1)

        logger.info("Generating reports...")
        
        # Prepare data for tabular format
        table_data = []
        for entry in report:
            table_data.append([
                entry['repository'],
                entry['type'],
                entry['assigned_to'],
                ', '.join(entry['shared_with_projects']) if entry['shared_with_projects'] else 'None',
                'Yes' if entry['shared_with_all_projects'] else 'No',
                ', '.join(entry['environments']) if entry['environments'] else 'None'
            ])
        
        # Sort table data by repository name (first column)
        table_data.sort(key=lambda x: x[0].lower())  # Case-insensitive sort
        
        # Generate table with updated headers
        headers = ['Repository', 'Type', 'Assigned To', 'Shared With Projects', 'Shared With All', 'Environments']
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        
        # After creating the initial report list, add project-based organization
        projects_data = {}
        shared_with_all = []

        # Organize repositories by project assignments and sharing
        for entry in report:
            repo_name = entry['repository']
            
            # Handle repositories shared with all projects
            if entry['shared_with_all_projects']:
                shared_with_all.append({
                    'repository': repo_name,
                    'type': entry['type']
                })
            
            # Handle project assignments
            if entry['assigned_to'] != 'None':
                project_name = entry['assigned_to']
                if project_name not in projects_data:
                    projects_data[project_name] = {
                        'assigned_repos': [],
                        'shared_repos': []
                    }
                projects_data[project_name]['assigned_repos'].append({
                    'repository': repo_name,
                    'type': entry['type']
                })
            
            # Handle explicit project sharing
            for shared_project in entry['shared_with_projects']:
                if shared_project not in projects_data:
                    projects_data[shared_project] = {
                        'assigned_repos': [],
                        'shared_repos': []
                    }
                projects_data[shared_project]['shared_repos'].append({
                    'repository': repo_name,
                    'type': entry['type']
                })

        # After collecting all project data, fetch project details
        logger.info("Fetching project details...")
        projects_with_details = {}
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            futures = {
                executor.submit(self.get_project_details, project_key): project_key 
                for project_key in projects_data.keys()
            }
            
            with tqdm(total=len(projects_data), desc="Fetching project details") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    project_key = futures[future]
                    try:
                        project_details = future.result()
                        if project_details:
                            # Group repositories by type
                            assigned_by_type = {
                                'local': [],
                                'remote': [],
                                'virtual': [],
                                'federated': []
                            }
                            shared_by_type = {
                                'local': [],
                                'remote': [],
                                'virtual': [],
                                'federated': []
                            }

                            # Sort assigned repositories by type
                            for repo in projects_data[project_key]['assigned_repos']:
                                repo_type = repo['type'].lower()
                                assigned_by_type[repo_type].append(repo['repository'])

                            # Sort shared repositories by type
                            for repo in projects_data[project_key]['shared_repos']:
                                repo_type = repo['type'].lower()
                                shared_by_type[repo_type].append(repo['repository'])

                            # Create project entry with all details
                            projects_with_details[project_key] = {
                                'display_name': project_details.get('display_name', project_key),
                                'description': project_details.get('description', ''),
                                'assigned_repositories': ';'.join(sorted(
                                    repo['repository'] for repo in projects_data[project_key]['assigned_repos']
                                )),
                                'shared_repositories': ';'.join(sorted(
                                    repo['repository'] for repo in projects_data[project_key]['shared_repos']
                                )),
                                # Add type-specific repository lists
                                'assigned_repositories_local': ';'.join(sorted(assigned_by_type['local'])),
                                'assigned_repositories_remote': ';'.join(sorted(assigned_by_type['remote'])),
                                'assigned_repositories_virtual': ';'.join(sorted(assigned_by_type['virtual'])),
                                'assigned_repositories_federated': ';'.join(sorted(assigned_by_type['federated'])),
                                'shared_repositories_local': ';'.join(sorted(shared_by_type['local'])),
                                'shared_repositories_remote': ';'.join(sorted(shared_by_type['remote'])),
                                'shared_repositories_virtual': ';'.join(sorted(shared_by_type['virtual'])),
                                'shared_repositories_federated': ';'.join(sorted(shared_by_type['federated']))
                            }
                        else:
                            # If we can't get project details, create basic entry
                            projects_with_details[project_key] = {
                                'display_name': project_key,
                                'description': '',
                                'assigned_repositories': ';'.join(sorted(
                                    repo['repository'] for repo in projects_data[project_key]['assigned_repos']
                                )),
                                'shared_repositories': ';'.join(sorted(
                                    repo['repository'] for repo in projects_data[project_key]['shared_repos']
                                )),
                                # Add empty type-specific repository lists
                                'assigned_repositories_local': '',
                                'assigned_repositories_remote': '',
                                'assigned_repositories_virtual': '',
                                'assigned_repositories_federated': '',
                                'shared_repositories_local': '',
                                'shared_repositories_remote': '',
                                'shared_repositories_virtual': '',
                                'shared_repositories_federated': ''
                            }
                    except Exception as e:
                        logger.error(f"Error processing project {project_key}: {str(e)}")
                    finally:
                        pbar.update(1)

        # Update the full report structure
        full_report = {
            'repositories': report,
            'projects': projects_with_details,
            'shared_with_all_projects': [repo['repository'] for repo in shared_with_all]
        }

        # Update the project-based views to include display names
        print("\nProject-Based Repository Assignments:")
        for project_key, data in sorted(projects_with_details.items()):
            print(f"\nProject: {data['display_name']} ({project_key})")
            
            # Update the text file writing part as well
            if projects_data[project_key]['assigned_repos']:
                print("\nAssigned Repositories:")
                assigned_table = tabulate(
                    [[repo['repository'], repo['type']] for repo in projects_data[project_key]['assigned_repos']],
                    headers=['Repository', 'Type'],
                    tablefmt='grid'
                )
                print(assigned_table)
            
            if projects_data[project_key]['shared_repos']:
                print("\nShared Repositories:")
                shared_table = tabulate(
                    [[repo['repository'], repo['type']] for repo in projects_data[project_key]['shared_repos']],
                    headers=['Repository', 'Type'],
                    tablefmt='grid'
                )
                print(shared_table)

        # Update the text file writing part
        with open(output_file.replace('.json', '.txt'), 'w') as f:
            f.write("Repository Project Assignments Report:\n")
            f.write(table)
            f.write("\n\nRepositories Shared with All Projects:\n")
            f.write(tabulate(
                [[repo['repository'], repo['type']] for repo in shared_with_all],
                headers=['Repository', 'Type'],
                tablefmt='grid'
            ))
            f.write("\n\nProject-Based Repository Assignments:\n")
            for project_key, data in sorted(projects_with_details.items()):
                f.write(f"\nProject: {data['display_name']} ({project_key})\n")
                if projects_data[project_key]['assigned_repos']:
                    f.write("\nAssigned Repositories:\n")
                    f.write(tabulate(
                        [[repo['repository'], repo['type']] for repo in projects_data[project_key]['assigned_repos']],
                        headers=['Repository', 'Type'],
                        tablefmt='grid'
                    ))
                if projects_data[project_key]['shared_repos']:
                    f.write("\nShared Repositories:\n")
                    f.write(tabulate(
                        [[repo['repository'], repo['type']] for repo in projects_data[project_key]['shared_repos']],
                        headers=['Repository', 'Type'],
                        tablefmt='grid'
                    ))
                f.write("\n")

        # Save comprehensive report to JSON file
        with open(output_file, 'w') as f:
            json.dump(full_report, f, indent=2)
        logger.info(f"Report saved to {output_file}")

        return full_report

def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate a report of repository project assignments in Artifactory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                    # Get report for all repositories
  %(prog)s --repo-name aanch-deb-local       # Get report for specific repository
  %(prog)s --repo-type local                 # Get report for local repositories
  %(prog)s --repo-type virtual               # Get report for virtual repositories
  %(prog)s --repo-type remote --parallel 20  # Process 20 repositories in parallel
  %(prog)s --repo-type all --project-key myproject  # Get semicolon-separated list of repos for project
        '''
    )
    
    # Optional arguments group for repo filtering
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--repo-name',
        help='Name of a specific repository to check'
    )
    group.add_argument(
        '--repo-type',
        choices=['local', 'remote', 'federated', 'virtual', 'all'],
        help='Type of repositories to check'
    )
    
    # Other optional arguments
    parser.add_argument(
        '--artifactory-url',
        default=os.getenv('ARTIFACTORY_URL'),
        help='Artifactory URL (default: from ARTIFACTORY_URL env var)'
    )
    parser.add_argument(
        '--token',
        default=os.getenv('MYTOKEN2'),
        help='Access token (default: from MYTOKEN2 env var)'
    )
    parser.add_argument(
        '--output',
        default='project_report.json',
        help='Output JSON file path (default: project_report.json)'
    )
    parser.add_argument(
        '--parallel',
        type=int,
        default=10,
        help='Number of repositories to process in parallel (default: 10)'
    )
    
    parser.add_argument(
        '--project-key',
        help='Project key to filter repositories (used with --repo-type all)'
    )
    
    args = parser.parse_args()
    
    # Validate required parameters
    if not args.artifactory_url:
        parser.error("Artifactory URL must be provided either via --artifactory-url or ARTIFACTORY_URL environment variable")
    if not args.token:
        parser.error("Access token must be provided either via --token or MYTOKEN2 environment variable")
    
    # Add validation for project-key
    if args.project_key and args.repo_type != 'all':
        parser.error("--project-key can only be used with --repo-type all")
    
    return args

def main():
    args = parse_args()
    
    reporter = ArtifactoryProjectReporter(args.artifactory_url, args.token)
    
    # If no repo filter is provided, get all repositories
    if not args.repo_name and not args.repo_type:
        repo_filter = None
    else:
        repo_filter = args.repo_name if args.repo_name else args.repo_type
    
    # If project key is provided with --repo-type all, handle specially
    if args.repo_type == 'all' and args.project_key:
        report = reporter.generate_report(None, args.output, args.parallel)
        
        # Get repositories for the specified project
        project_data = report.get('projects', {}).get(args.project_key, {})
        if project_data:
            print(f"\nRepositories for project {args.project_key}:")
            print("\nAssigned repositories by type:")
            for repo_type in ['local', 'remote', 'virtual', 'federated']:
                repos = project_data.get(f'assigned_repositories_{repo_type}')
                if repos:
                    print(f"{repo_type.upper()}: {repos}")
            
            print("\nShared repositories by type:")
            for repo_type in ['local', 'remote', 'virtual', 'federated']:
                repos = project_data.get(f'shared_repositories_{repo_type}')
                if repos:
                    print(f"{repo_type.upper()}: {repos}")

            # Add new section for all non-virtual assigned repositories
            non_virtual_repos = []
            for repo_type in ['local', 'remote', 'federated']:
                repos = project_data.get(f'assigned_repositories_{repo_type}')
                if repos:
                    non_virtual_repos.extend(repos.split(';'))
            
            if non_virtual_repos:
                print("\nAll assigned non-virtual repositories:")
                print(';'.join(sorted(non_virtual_repos)))
        else:
            logger.error(f"No data found for project {args.project_key}")
    else:
        reporter.generate_report(repo_filter, args.output, args.parallel)

if __name__ == "__main__":
    main()
