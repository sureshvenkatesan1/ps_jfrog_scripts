# Version 0.9 - Nov 5 2024

import requests
import urllib3
import time
import sys
import argparse
import concurrent.futures
from functools import partial
import json
import threading

from docutils.nodes import target

urllib3.disable_warnings()

SYSTEM_REPOS = ["TOTAL", "auto-trashcan", "jfrog-support-bundle", "jfrog-usage-logs"]
repos_to_do = []

# Single lock for all file operations
file_lock = threading.Lock()

def thread_safe_log(message, file_path):
    """Thread-safe logging to a file"""
    with file_lock:
        with open(file_path, 'a') as f:
            f.write(f"{message}\n")

def debug_request(method, url, auth=None, headers=None, data=None, json_data=None, debug=False):
    """Print equivalent curl command for a request if debug mode is enabled"""
    if not debug:
        return
        
    curl_command = f'curl -X {method} "{url}"'
    
    if headers:
        for key, value in headers.items():
            curl_command += f' -H "{key}: {value}"'
    elif auth:  # Fallback for old auth method
        if isinstance(auth, tuple):
            if auth[0] == '_token':
                curl_command += f' -H "Authorization: Bearer {auth[1]}"'
            else:
                curl_command += f' -u "{auth[0]}:{auth[1]}"'
    
    if json_data:
        json_str = json.dumps(json_data)
        json_str = json_str.replace('"', '\\"')
        curl_command += f' -d "{json_str}"'
    elif data:
        data_str = str(data).replace('"', '\\"')
        curl_command += f' -d "{data_str}"'
    
    print("\nDebug - Equivalent curl command:")
    print(curl_command)
    print()

# This class defines an Artifactory object that carries its own information
# This helps with readability, re-usability, and to reduce the need to hard code information
class Artifactory:
    def __init__(self, url, auth, name, debug=False):
        self.url = url
        self.auth = auth
        self.name = name
        self.debug = debug
        print(f"\nInitializing {name} Artifactory connection:")
        print(f"URL: {url}")
        print(f"Auth type: {'Bearer token' if auth[0] == '_token' else 'Basic auth'}")
        # Create standard headers with auth
        self.headers = {
            'Authorization': f'Bearer {auth[1]}',
            'Content-Type': 'application/json'
        }
        self.storage = self.storage()
        self.repository_configurations = self.get_repository_configurations()
        self.repos = self.get_repo_list()
        self.repo_details = self.get_repo_details()
        self.local_storage, self.remote_storage, self.federated_storage = self.get_filtered_repos_storage()
        self.local_configs, self.federated_configs, self.remote_configs, self.virtual_configs = self.get_filtered_repo_configs()
        self.xray_policies = []
        self.xray_watches = []
        self.xray_ignore_rules = []

    def storage(self):
        url = self.url + "/artifactory/api/storageinfo"
        debug_request('GET', url, headers=self.headers, debug=self.debug)
        storage = requests.get(url, headers=self.headers, verify=False)
        if storage.status_code != 200:
            print(f"Error getting storage info: {storage.status_code} - {storage.text}")
            return {}
        return storage.json()

    def get_repo_list(self):
        """Get list of repository keys"""
        url = self.url + "/artifactory/api/repositories"
        debug_request('GET', url, headers=self.headers, debug=self.debug)
        repos = requests.get(url, headers=self.headers, verify=False)
        if repos.status_code != 200:
            print(f"Error getting repository list: {repos.status_code} - {repos.text}")
            return []
        return [repo["key"] for repo in repos.json()]

    def get_repo_details(self):
        """Get repository details from storage info"""
        try:
            return self.storage.get("repositoriesSummaryList", [])
        except (KeyError, AttributeError):
            return []

    def get_filtered_repos_storage(self):
        """Get filtered repository storage information"""
        l, r, f = {}, {}, {}
        for summary in self.repo_details:
            try:
                if summary["repoType"] == "LOCAL":
                    l[summary["repoKey"]] = summary
                elif summary["repoType"] == "FEDERATED":
                    f[summary["repoKey"]] = summary
                elif summary["repoType"] == "CACHE":
                    r[summary["repoKey"]] = summary
            except KeyError:
                continue
        return l, r, f

    def print_remotes_with_password(self):
        """Print remote repositories that have passwords configured"""
        for repo in self.repository_configurations.get("REMOTE", []):
            if repo.get("password", ""):
                print(repo["key"])
                thread_safe_log(repo["key"], f"./remotes_with_password_{self.name}.log")

    def print_missing_remotes_with_password(self, target_artifactory):
        """Print remote repositories with passwords that are missing in target"""
        print(f"\nChecking for remote repositories with passwords in {self.name} that are missing in {target_artifactory.name}")
        
        # Get set of remote repo keys in target
        target_remote_keys = set(target_artifactory.remote_configs.keys())
        missing_repos = []
        
        for repo in self.repository_configurations.get("REMOTE", []):
            if repo.get("password", "") and repo["key"] not in target_remote_keys:
                missing_repos.append(repo["key"])
                print(repo["key"])
                thread_safe_log(repo["key"], f"./missing_remotes_with_password_{self.name}.log")
        
        if missing_repos:
            print("\nMissing repositories with passwords (semicolon-separated):")
            missing_repos_str = ";".join(missing_repos)
            print(missing_repos_str)
            thread_safe_log("\nMissing repositories with passwords (semicolon-separated):", 
                           f"./missing_remotes_with_password_{self.name}.log")
            thread_safe_log(missing_repos_str, f"./missing_remotes_with_password_{self.name}.log")
        else:
            print("No remote repositories with passwords missing in target")

    def get_repository_configurations(self):
        repos = requests.get(self.url + "/artifactory/api/repositories/configurations", headers=self.headers, verify=False)
        return repos.json()

    def get_repo_content(self, repo_name):
        headers = {'content-type': 'text/plain', }
        query = 'items.find({"name":{"$match":"*"}, "repo":"'+repo_name+'"}).include("name", "path")'
        resp = requests.post(self.url+"/artifactory/api/search/aql", headers=headers, data=query, verify=False)
        return resp.json()["results"]

    def transform_local_to_federated(self):
        for repo in self.local_storage:
            print("Transforming local repository:", repo)
            headers = {'content-type': 'application/json', }
            resp = requests.post(self.url + "/artifactory/api/federation/migrate/{}".format(repo), headers=headers, verify=False)
            if resp.status_code != 200:
                print("Non-200 response:", resp.status_code)
                print(resp.text)
        self.local_storage, self.remote_storage,  self.federated_storage = self.get_filtered_repos_storage()

    def refresh_storage_summary(self):
        headers = {'content-type': 'application/json', }
        resp = requests.post(self.url + "/artifactory/api/storageinfo/calculate", headers=headers, verify=False)
        if resp.status_code != 202:
            print("Non-202 response:", resp.status_code)
            print(resp.text)

        self.local_storage, self.remote_storage,  self.federated_storage = self.get_filtered_repos_storage()

    def get_filtered_repo_configs(self):
        l, f, r, v = {}, {}, {}, {}

        try:
            for repo in self.repository_configurations["LOCAL"]:
                repo_name = repo["key"]
                l[repo_name] = repo
        except KeyError:
            l = {}

        try:
            for repo in self.repository_configurations["FEDERATED"]:
                repo_name = repo["key"]
                f[repo_name] = repo
        except KeyError:
            f = {}

        try:
            for repo in self.repository_configurations["REMOTE"]:
                repo_name = repo["key"]
                r[repo_name] = repo
        except KeyError:
            r = {}

        try:
            for repo in self.repository_configurations["VIRTUAL"]:
                repo_name = repo["key"]
                v[repo_name] = repo
        except KeyError:
            v = {}

        return l, f, r, v

    def load_xray_data(self):

        # Get Policies
        resp = requests.get(self.url + "/xray/api/v2/policies", headers=self.headers, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of policies:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting policies")
        self.xray_policies = resp.json()

        # Get Watches
        resp = requests.get(self.url + "/xray/api/v2/watches", headers=self.headers, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of watches:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting watches")
        self.xray_watches = resp.json()

        # Get Ignore Rules
        resp = requests.get(self.url + "/xray/api/v1/ignore_rules", headers=self.headers, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of watches:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting watches")
        self.xray_ignore_rules = resp.json()

    def delete_repository(self, repo_key):
        """Delete a single repository"""
        url = self.url + "/artifactory/api/repositories/" + repo_key
        debug_request('DELETE', url, headers=self.headers, debug=self.debug)
        resp = requests.delete(url, headers=self.headers, verify=False)
        return resp.status_code == 200, resp

    def delete_repositories_from_file(self, filename, dry_run=True):
        """Delete repositories listed in a file"""

        
        try:
            with open(filename, 'r') as f:
                repos = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return
            
        print(f"Found {len(repos)} repositories to delete")
        if dry_run:
            print("DRY RUN - Repositories that would be deleted:", repos)
            return
            
        for repo in repos:
            print(f"Deleting repository: {repo}")
            success, resp = self.delete_repository(repo)
            if success:
                print(f"Successfully deleted repository: {repo}")
                thread_safe_log(f"Deleted {repo}", './delete_repos_success.log')
            else:
                print(f"Failed to delete repository {repo}: {resp.status_code} - {resp.text}")
                thread_safe_log(f"{repo} | {resp.status_code} - {resp.text}", './delete_repos_errors.log')

    def delete_repositories_by_type(self, repo_type, dry_run=True):
        """Delete all repositories of a specific type"""

        
        repos_to_delete = []
        if repo_type == 'local':
            repos_to_delete = list(self.local_configs.keys())
        elif repo_type == 'remote':
            repos_to_delete = list(self.remote_configs.keys())
        elif repo_type == 'federated':
            repos_to_delete = list(self.federated_configs.keys())
        elif repo_type == 'virtual':
            repos_to_delete = list(self.virtual_configs.keys())
        elif repo_type == 'all':
            repos_to_delete = self.repos
        else:
            print(f"Invalid repository type: {repo_type}")
            return
            
        # Filter out system repositories
        repos_to_delete = [repo for repo in repos_to_delete if repo not in SYSTEM_REPOS]
        
        print(f"Found {len(repos_to_delete)} {repo_type} repositories to delete")
        if dry_run:
            print("DRY RUN - Repositories that would be deleted:", repos_to_delete)
            return
            
        for repo in repos_to_delete:
            print(f"Deleting repository: {repo}")
            success, resp = self.delete_repository(repo)
            if success:
                print(f"Successfully deleted repository: {repo}")
                thread_safe_log(f"Deleted {repo}", './delete_repos_success.log')
            else:
                print(f"Failed to delete repository {repo}: {resp.status_code} - {resp.text}")
                thread_safe_log(f"{repo} | {resp.status_code} - {resp.text}", './delete_repos_errors.log')

    def assign_repo_to_project(self, repo_name, project_key):
        """Assign a repository to a project"""
        url = f"{self.url}/access/api/v1/projects/_/attach/repositories/{repo_name}/{project_key}?force=true"
        debug_request('PUT', url, headers=self.headers, debug=self.debug)
        resp = requests.put(url, headers=self.headers, verify=False)
        return resp.status_code == 204, resp

    def delete_repositories_from_file_parallel(self, filename, max_workers=4, dry_run=True):
        """Delete repositories listed in a file in parallel"""

        
        try:
            with open(filename, 'r') as f:
                repos = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return
            
        print(f"Found {len(repos)} repositories to delete")
        if dry_run:
            print("DRY RUN - Repositories that would be deleted:", repos)
            return
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(self.delete_repository, repo): repo
                for repo in repos
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    success, resp = future.result()
                    if success:
                        print(f"Successfully deleted repository: {repo}")
                        thread_safe_log(f"Deleted {repo}", './delete_repos_success.log')
                    else:
                        print(f"Failed to delete repository {repo}: {resp.status_code} - {resp.text}")
                        thread_safe_log(f"{repo} | {resp.status_code} - {resp.text}", './delete_repos_errors.log')
                except Exception as e:
                    print(f"Error deleting repository {repo}: {str(e)}")
                    thread_safe_log(f"{repo} | Exception: {str(e)}", './delete_repos_errors.log')

    def delete_repositories_by_type_parallel(self, repo_type, max_workers=4, dry_run=True):
        """Delete all repositories of a specific type in parallel"""

        
        repos_to_delete = []
        if repo_type == 'local':
            repos_to_delete = list(self.local_configs.keys())
        elif repo_type == 'remote':
            repos_to_delete = list(self.remote_configs.keys())
        elif repo_type == 'federated':
            repos_to_delete = list(self.federated_configs.keys())
        elif repo_type == 'virtual':
            repos_to_delete = list(self.virtual_configs.keys())
        elif repo_type == 'all':
            repos_to_delete = self.repos
        else:
            print(f"Invalid repository type: {repo_type}")
            return
            
        # Filter out system repositories
        repos_to_delete = [repo for repo in repos_to_delete if repo not in SYSTEM_REPOS]
        
        print(f"Found {len(repos_to_delete)} {repo_type} repositories to delete")
        if dry_run:
            print("DRY RUN - Repositories that would be deleted:", repos_to_delete)
            return
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(self.delete_repository, repo): repo
                for repo in repos_to_delete
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    success, resp = future.result()
                    if success:
                        print(f"Successfully deleted repository: {repo}")
                        thread_safe_log(f"Deleted {repo}", './delete_repos_success.log')
                    else:
                        print(f"Failed to delete repository {repo}: {resp.status_code} - {resp.text}")
                        thread_safe_log(f"{repo} | {resp.status_code} - {resp.text}", './delete_repos_errors.log')
                except Exception as e:
                    print(f"Error deleting repository {repo}: {str(e)}")
                    thread_safe_log(f"{repo} | Exception: {str(e)}", './delete_repos_errors.log')

    def get_project_details(self):
        """Get detailed list of projects"""
        url = f"{self.url}/access/api/v1/projects"
        debug_request('GET', url, headers=self.headers, debug=self.debug)
        resp = requests.get(url, headers=self.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting projects: {resp.status_code} - {resp.text}")
            return []
        return resp.json()

    def print_missing_projects(self, target_artifactory):
        """Print projects that exist in this instance but not in target"""
        print(f"\nChecking for projects in {self.name} that are missing in {target_artifactory.name}")
        
        source_projects = {p["project_key"]: p for p in self.get_project_details()}
        target_projects = {p["project_key"]: p for p in target_artifactory.get_project_details()}
        
        missing_projects = []
        different_projects = []
        
        # Check for missing and different projects
        for project_key, source_project in source_projects.items():
            if project_key not in target_projects:
                missing_projects.append(project_key)
                print(f"\nProject missing in target: {project_key}")
                thread_safe_log(f"\nProject missing in target: {project_key}", 
                              f"./missing_projects_{target_artifactory.name}.log")
                thread_safe_log(f"Configuration: {json.dumps(source_project, indent=2)}", 
                              f"./missing_projects_{target_artifactory.name}.log")
            else:
                # Compare project configurations
                target_project = target_projects[project_key]
                if self._projects_are_different(source_project, target_project):
                    different_projects.append(project_key)
                    print(f"\nProject with different configuration: {project_key}")
                    thread_safe_log(f"\nProject with different configuration: {project_key}", 
                                  f"./missing_projects_{target_artifactory.name}.log")
                    thread_safe_log("Source configuration:", 
                                  f"./missing_projects_{target_artifactory.name}.log")
                    thread_safe_log(f"{json.dumps(source_project, indent=2)}", 
                                  f"./missing_projects_{target_artifactory.name}.log")
                    thread_safe_log("Target configuration:", 
                                  f"./missing_projects_{target_artifactory.name}.log")
                    thread_safe_log(f"{json.dumps(target_project, indent=2)}", 
                                  f"./missing_projects_{target_artifactory.name}.log")
        
        # Print summary
        if missing_projects:
            print("\nMissing projects (semicolon-separated):")
            missing_projects_str = ";".join(missing_projects)
            print(missing_projects_str)
            thread_safe_log("\nMissing projects (semicolon-separated):", 
                           f"./missing_projects_{target_artifactory.name}.log")
            thread_safe_log(missing_projects_str, 
                           f"./missing_projects_{target_artifactory.name}.log")
        
        if different_projects:
            print("\nProjects with different configurations (semicolon-separated):")
            different_projects_str = ";".join(different_projects)
            print(different_projects_str)
            thread_safe_log("\nProjects with different configurations (semicolon-separated):", 
                           f"./missing_projects_{target_artifactory.name}.log")
            thread_safe_log(different_projects_str, 
                           f"./missing_projects_{target_artifactory.name}.log")
        
        if not missing_projects and not different_projects:
            print("No projects missing or different in target")

    def _projects_are_different(self, project1, project2):
        """Compare two project configurations dynamically"""
        # Compare the entire project configurations
        return project1 != project2

    def check_repo_exists(self, repo_name, package_type=None):
        """
        Check if a repository exists in target Artifactory
        Args:
            repo_name: Name of the repository to check
            package_type: Package type of the repository (e.g. "docker")
        Returns:
            bool: True if repository exists, False otherwise
        """
        # For docker repos, check with hyphenated name
        if package_type == "docker":
            repo_name = repo_name.replace('_', '-').replace('.', '-')
        
        resp = requests.get(
            f"{self.url}/artifactory/api/repositories/{repo_name}",
            headers=self.headers,
            verify=False
        )
        return resp.status_code == 200

class ArtifactoryHelper:
    def __init__(self, rt1, rt2):
        self.rt1 = rt1
        self.rt2 = rt2
        self.missing_r1, self.missing_r2 = self.missing_repos()

    def missing_repos(self):
        missing_r1 = [str(repo) for repo in self.rt2.repos if repo not in self.rt1.repos]
        missing_r2 = [str(repo) for repo in self.rt1.repos if repo not in self.rt2.repos]
        return missing_r1, missing_r2

    def missing_locals(self):
        missing_r1 = [str(repo) for repo in self.rt2.local_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.local_storage if repo in self.missing_r2]
        return missing_r1, missing_r2

    def missing_federated(self):
        missing_r1 = [str(repo) for repo in self.rt2.federated_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.federated_storage if repo in self.missing_r2]
        return missing_r1, missing_r2

    def missing_remote(self):
        missing_r1 = [str(repo) for repo in self.rt2.remote_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.remote_storage if repo in self.missing_r2]
        return  missing_r1, missing_r2

    def missing_virtual(self):
        missing_r1 = [repo for repo in self.rt2.virtual_configs.keys() if repo not in self.rt1.virtual_configs.keys()]
        missing_r2 = [repo for repo in self.rt1.virtual_configs.keys() if repo not in self.rt2.virtual_configs.keys()]
        return missing_r1, missing_r2

    def common_repos(self):
        return [str(repo) for repo in self.rt2.repos if repo in self.rt1.repos and repo not in SYSTEM_REPOS]

    def repo_report(self):

        mlr1, mlr2 = self.missing_locals()
        mfr1, mfr2 = self.missing_federated()
        mrr1, mrr2 = self.missing_remote()
        mvr1, mvr2 = self.missing_virtual()

        print("************")
        print("# of Local Repos Missing for {}: {}".format(self.rt1.name, len(mlr1)))
        for repo in mlr1:
            thread_safe_log(repo, f"./missing_local_source.log")

        print("# of Local Repos Missing for {}: {}".format(self.rt2.name, len(mlr2)))
        for repo in mlr2:
            thread_safe_log(repo, f"./missing_local_target.log")
        print("************")
        print("# of Federated repos missing in {} (present in {}): {}".format(self.rt1.name, self.rt2.name, len(mfr1)))
        for repo in mfr1:
            thread_safe_log(repo, f"./missing_federated_source.log")
        print("# of Federated repos missing in {} (present in {}): {}".format(self.rt2.name, self.rt1.name, len(mfr2)))
        for repo in mfr2:
            thread_safe_log(repo, f"./missing_federated_target.log")
        print("************")
        print("# of remote Repos Missing for {}: {}".format(self.rt1.name, len(mrr1)))
        for repo in mrr1:
            thread_safe_log(repo, f"./missing_remote_source.log")
        print("# of Remote Repos Missing for {}: {}".format(self.rt2.name, len(mrr2)))
        for repo in mrr2:
            thread_safe_log(repo, f"./missing_remote_target.log")
        print("************")
        print("# of Virtual  Repos Missing in {}: {}".format(self.rt1.name, len(mvr1)))
        for repo in mvr1:
            thread_safe_log(repo, f"./missing_virtual_source.log")
        print("# of Virtual  Repos Missing in {}: {}".format(self.rt2.name, len(mvr2)))
        for repo in mvr2:
            thread_safe_log(repo, f"./missing_virtual_target.log")
        print("************")

    def local_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.local.keys():
                if self.rt1.local[repo_name]["filesCount"] != self.rt2.local[repo_name]["filesCount"] or self.rt1.local[repo_name]["usedSpace"] != self.rt2.local[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.local[repo_name]["filesCount"], self.rt1.local[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.local[repo_name]["filesCount"], self.rt2.local[repo_name]["usedSpace"]))

    def federated_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.federated.keys():

                if self.rt1.federated[repo_name]["filesCount"] != self.rt2.federated[repo_name]["filesCount"] or self.rt1.federated[repo_name]["usedSpace"] != self.rt2.federated[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.federated[repo_name]["filesCount"], self.rt1.federated[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.federated[repo_name]["filesCount"], self.rt2.federated[repo_name]["usedSpace"]))

    def remote_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.remote.keys():
                if self.rt1.federated[repo_name]["filesCount"] != self.rt2.federated[repo_name]["filesCount"] or self.rt1.federated[repo_name]["usedSpace"] != self.rt2.federated[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.federated[repo_name]["filesCount"], self.rt1.federated[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.federated[repo_name]["filesCount"], self.rt2.federated[repo_name]["usedSpace"]))

    def repo_content_diff(self, repo_name):
        r1_content = self.rt1.get_repo_content(repo_name)
        r2_content = self.rt2.get_repo_content(repo_name)
        paths_one = []
        paths_two = []

        for result in r1_content:
            path = result['path'] + "/" + result['name']  # put the repo and path of each image in a tuple
            paths_one.append(path)  # put them all on a list

        for result in r2_content:
            path = result['path'] + "/" + result['name']  # put the repo and path of each image in a tuple
            paths_two.append(path)  # put them all on a list

        one_missing = list(set(paths_one) - set(paths_two))
        two_missing = list(set(paths_two) - set(paths_one))

        return one_missing, two_missing

    def do_full_file_diff(self):
        print("************")
        print("Checking local repositories in common for full file diff")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.local.keys():
                print("************")
                print("Repository Name: {}".format(repo_name))
                print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.local[repo_name]["filesCount"], self.rt1.local[repo_name]["usedSpace"]))
                print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.local[repo_name]["filesCount"], self.rt2.local[repo_name]["usedSpace"]))
                one_missing, two_missing = self.repo_content_diff(repo_name)
                print("Instance {} is missing artifacts {}".format(self.rt1.name, one_missing))
                print("Instance {} is missing artifacts {}".format(self.rt2.name, two_missing))

    def create_missing_repos_on_target_parallel(self, repo_type, max_workers=4, environment=None):
        """Create missing repositories of specified type on target in parallel"""
        print(f"Creating missing {repo_type} repositories for {self.rt2.name}")
        error_file = f'./create_{repo_type}_errors.log'
        success_file = f'./create_{repo_type}_success.log'
        
        failed_repos = []
        
        # Get source and target configs based on repo type
        source_configs = None
        target_configs = None
        if repo_type == 'local':
            source_configs = self.rt1.local_configs
            target_configs = self.rt2.local_configs
        elif repo_type == 'remote':
            source_configs = self.rt1.remote_configs
            target_configs = self.rt2.remote_configs
        elif repo_type == 'virtual':
            source_configs = self.rt1.virtual_configs
            target_configs = self.rt2.virtual_configs
        elif repo_type == 'federated':
            source_configs = self.rt1.federated_configs
            target_configs = self.rt2.federated_configs
        
        # Get filtered list of repos to create
        repos_to_create = self.get_filtered_repos_to_create(source_configs, target_configs)
        
        print(f"Found {len(repos_to_create)} {repo_type} repositories to create")
        thread_safe_log(f"Found {len(repos_to_create)} {repo_type} repositories to create", success_file)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(self.create_single_repository, repo_name, repo_type, environment): repo_name
                for repo_name in repos_to_create.keys()
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                repo_name = future_to_repo[future]
                try:
                    resp, error = future.result()  # Now getting both response and error
                    if error:  # If there was an error
                        print(f"Error creating repository {repo_name}: {error}")
                        thread_safe_log(f"Error creating repository {repo_name}: {error}", error_file)
                        failed_repos.append(repo_name)
                    elif resp and resp.status_code != 200:  # If response exists but status is not 200
                        error_msg = f"Failed to create repository {repo_name}: {resp.status_code} - {resp.text}"
                        print(error_msg)
                        thread_safe_log(error_msg, error_file)
                        failed_repos.append(repo_name)
                except Exception as e:
                    error_msg = f"Error processing repository {repo_name}: {str(e)}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
                    failed_repos.append(repo_name)
        
        if failed_repos:
            failed_repos_str = ";".join(sorted(failed_repos))
            error_msg = f"\nFailed {repo_type} repositories (semicolon-separated):\n" + failed_repos_str
            print(error_msg)
            thread_safe_log(error_msg, error_file)
        

    # Replace individual parallel methods with calls to the unified method
    def create_missing_locals_on_target_parallel(self, max_workers=4, environment=None):
        self.create_missing_repos_on_target_parallel('local', max_workers, environment)

    def create_missing_remotes_on_target_parallel(self, max_workers=4, environment=None):
        self.create_missing_repos_on_target_parallel('remote', max_workers, environment)

    def create_missing_virtuals_on_target_parallel(self, max_workers=4, environment=None):
        self.create_missing_repos_on_target_parallel('virtual', max_workers, environment)

    def create_missing_federated_repos_on_target_parallel(self, max_workers=4, environment=None):
        self.create_missing_repos_on_target_parallel('federated', max_workers, environment)



    def update_single_repository(self, repo_name, repo_type, source_config, dry=False):
        """Update a single repository configuration in target"""
        if repo_name in SYSTEM_REPOS:
            return None
            
        # Get target config based on repo type
        target_config = None
        if repo_type == 'local':
            if repo_name not in self.rt2.local_configs:
                print(f"Repository {repo_name} does not exist in target.")
                return None
            target_config = self.rt2.local_configs[repo_name]
        elif repo_type == 'remote':
            if repo_name not in self.rt2.remote_configs:
                print(f"Repository {repo_name} does not exist in target.")
                return None
            target_config = self.rt2.remote_configs[repo_name]
        elif repo_type == 'virtual':
            if repo_name not in self.rt2.virtual_configs:
                print(f"Repository {repo_name} does not exist in target.")
                return None
            target_config = self.rt2.virtual_configs[repo_name]
        elif repo_type == 'federated':
            if repo_name not in self.rt2.federated_configs:
                print(f"Repository {repo_name} does not exist in target.")
                return None
            target_config = self.rt2.federated_configs[repo_name]
        
        # Create copies for comparison
        source_config_compare = source_config.copy()
        target_config_compare = target_config.copy()
        
        # Handle type-specific configuration comparisons
        if repo_type == 'remote':
            source_config_compare.pop('password', None)
            target_config_compare.pop('password', None)
        elif repo_type == 'federated':
            source_config_compare.pop('members', None)
            target_config_compare.pop('members', None)
        
        # Compare configurations
        if source_config_compare != target_config_compare:
            print(f"\nFound different configuration for repo {repo_name}")
            print("Source config:", json.dumps(source_config_compare, indent=2))
            print("Target config:", json.dumps(target_config_compare, indent=2))
            
            if not dry:
                update_config = source_config.copy()
                update_config["rclass"] = repo_type
                
                # Handle type-specific updates
                if repo_type == 'remote':
                    update_config["password"] = ""  # Clear password for safety
                elif repo_type == 'federated':
                    update_config["members"] = [
                        {"url": f"{self.rt1.url}/artifactory/{repo_name}", "enabled": "true"},
                        {"url": f"{self.rt2.url}/artifactory/{repo_name}", "enabled": "true"}
                    ]
                
                resp = requests.post(
                    f"{self.rt2.url}/artifactory/api/repositories/{repo_name}",
                    json=update_config,
                    headers=self.rt2.headers,
                    verify=False
                )
                return repo_name, resp
        return None

    def update_repositories_on_target_parallel(self, repo_type, dry=False, max_workers=4):
        """Update repository configurations in target in parallel"""
        print(f"\nChecking {repo_type} repository configurations...")
        error_file = f'./update_{repo_type}_errors.log'
        success_file = f'./update_{repo_type}_success.log'
        
        # Get source configs based on repo type
        source_configs = None
        if repo_type == 'local':
            source_configs = self.rt1.local_configs
        elif repo_type == 'remote':
            source_configs = self.rt1.remote_configs
        elif repo_type == 'virtual':
            source_configs = self.rt1.virtual_configs
        elif repo_type == 'federated':
            source_configs = self.rt1.federated_configs
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(self.update_single_repository, repo_name, repo_type, source_config, dry): repo_name
                for repo_name, source_config in source_configs.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                try:
                    result = future.result()
                    if result:
                        repo_name, resp = result
                        if resp.status_code != 200:
                            error_msg = f"Failed to update {repo_type} repository {repo_name}: {resp.status_code} - {resp.text}"
                            print(error_msg)
                            thread_safe_log(error_msg, error_file)
                        else:
                            success_msg = f"Successfully updated {repo_type} repository: {repo_name}"
                            print(success_msg)
                            thread_safe_log(success_msg, success_file)
                except Exception as e:
                    repo_name = future_to_repo[future]
                    error_msg = f"Error processing repository {repo_name}: {str(e)}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
        

    # Replace individual update methods with calls to the unified method
    def update_locals_on_target_parallel(self, dry=False, max_workers=4):
        self.update_repositories_on_target_parallel('local', dry, max_workers)

    def update_remotes_on_target_parallel(self, dry=False, max_workers=4):
        self.update_repositories_on_target_parallel('remote', dry, max_workers)

    def update_virtuals_on_target_parallel(self, dry=False, max_workers=4):
        self.update_repositories_on_target_parallel('virtual', dry, max_workers)

    def update_federated_repos_on_target_parallel(self, dry=False, max_workers=4):
        self.update_repositories_on_target_parallel('federated', dry, max_workers)

    def update_federated_members(self, repo_filter=False):
        print("Updating member repositories for", self.rt1.name)
        for repo_name in self.rt1.federated.keys():
            if repo_filter:
                if repo_name not in repos_to_do:
                    continue


            if repo_name not in SYSTEM_REPOS:

                repo = self.rt1.federated[repo_name]
                repo["members"] = [{"url": self.rt2.url + "/" + repo_name, "enabled": "true"}]
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt1.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    headers=self.headers, debug=self.debug)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

        print("Updating member repositories for", self.rt2.name)
        for repo_name in self.rt2.federated.keys():
            if repo_name not in SYSTEM_REPOS:

                repo = self.rt2.federated[repo_name]
                repo["members"] = [{"url": self.rt1.url + "/" + repo_name, "enabled": "true"}]
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    headers=self.headers, debug=self.debug)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

    def refresh_storage_summary(self):
        print("Refreshing storage summary for", self.rt1.name)
        self.rt1.refresh_storage_summary()
        print("Refreshing storage summary for", self.rt2.name)
        self.rt2.refresh_storage_summary()

    def federate_one(self, repo_name):
        repo = self.rt1.federated[repo_name]
        repo["members"] = [{"url": self.rt1.url + "/" + repo_name, "enabled": "true"}]
        headers = {'content-type': 'application/json', }
        repo["rclass"] = "federated"
        print("Creating repo in target")
        resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                            headers=self.headers, debug=self.debug)
        if resp.status_code != 201:
            print("Non-201 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Updating repo in source")
        repo = self.rt1.federated[repo_name]
        repo["members"] = [{"url": self.rt2.url + "/" + repo_name, "enabled": "true"}]
        headers = {'content-type': 'application/json', }
        resp = requests.post(self.rt1.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                            headers=self.headers, debug=self.debug)
        if resp.status_code != 201:
            print("Non-201 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Triggering Configuration Sync on source")
        r = requests.post(self.rt1.url + "/artifactory/api/federation/configSync/{}".format( repo["repoKey"]), headers=self.headers, verify=False)
        if resp.status_code != 200:
            print("Non-200 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Triggering Full Sync on source")
        r = requests.post(self.rt1.url + "/artifactory/api/federation/fullSync/{}".format( repo["repoKey"]), headers=self.headers, verify=False)
        if resp.status_code != 200:
            print("Non-200 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

    def federate_all(self, repo_filter=False):
        for repo_name in self.rt1.federated.keys():
            if repo_filter:
                if repo_name not in repos_to_do:
                    continue

            if repo_name not in SYSTEM_REPOS:
                self.federate_one(repo_name)



    # Xray stuff
    def update_all_xray_data(self):
        self.rt1.load_xray_data()
        self.rt2.load_xray_data()

    def report_watches_policies(self):

        self.update_all_xray_data()

        print("Doing", len(self.rt1.xray_policies), "policies.")
        for policy in self.rt1.xray_policies:
            policy_name = policy["name"]
            rt2_policy = requests.get(self.rt2.url + "/xray/api/v2/policies/" + policy_name, headers=self.headers,
                                      verify=False)
            if rt2_policy.status_code == 404:
                print("Policy", policy_name, "doesn't exist in target Artifactory")
            elif rt2_policy.status_code == 200:
                # The policy may still be different (author, creation date, and modification date will
                target_policy = rt2_policy.json()
                if target_policy["rules"] == policy["rules"]:
                    # Rules are the same
                    try:
                        if target_policy["description"] == policy["description"]:
                            print("Policy", policy_name, "already exists. They are the same")
                        else:
                            print("Policy", policy_name, "already exists. Descriptions are not the same, needs updating.")
                    except KeyError:
                        # Sometimes there is no description. that's fine.
                        print("Policy", policy_name, "already exists. They are the same")
                else:
                    print("Policy", policy_name, "already exists. Rules are the not same, needs updating.")

            else:
                print("Error for policy", policy_name, "unexpected status code", rt2_policy.status_code)

        print("Doing", len(self.rt1.xray_watches), "watches.")
        for watch in self.rt1.xray_watches:
            watch_name = watch["general_data"]["name"]
            rt2_watch = requests.get(self.rt2.url + "/xray/api/v2/watches/" + watch_name, headers=self.headers, verify=False)
            if rt2_watch.status_code == 404:
                print("Watch", watch_name,  "doesn't exist in target Artifactory")

            elif rt2_watch.status_code == 200:
                target_watch = rt2_watch.json()
                is_diff = False
                try:
                    target_res = []
                    for i in target_watch["project_resources"]["resources"]:
                        target_res.append(i["name"])

                    source_res = []
                    for i in watch["project_resources"]["resources"]:
                        source_res.append(i["name"])

                    target_res = set(target_res)
                    source_res = set(source_res)
                    diff = source_res-target_res

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_watch["assigned_policies"] != watch["assigned_policies"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_watch["watch_recipients"] != watch["watch_recipients"]:
                        is_diff = True
                except KeyError:
                    pass

                if is_diff:
                    print("Watch", watch_name, "already exists, but it's not the same. Needs update.")
                else:
                    print("Watch", watch_name, "already exists.")

            else:
                print("Error for watch", watch_name, "unexpected status code", rt2_watch.status_code)

        print("Doing", len(self.rt1.xray_ignore_rules["data"]), "ignore rules.")

        for rule in self.rt1.xray_ignore_rules["data"]:
            rule_id = rule["id"]
            rt2_rule = requests.get(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, headers=self.headers,
                                     verify=False)
            if rt2_rule.status_code == 404:
                print("Rule", rule_id, "doesn't exist in target Artifactory")

            elif rt2_rule.status_code == 200:
                target_rule = rt2_rule.json()
                is_diff = False
                try:
                    target_comps = []
                    for i in target_rule["components"]:
                        target_comps.append(i["name"])

                    source_comps = []
                    for i in rule["components"]:
                        source_comps.append(i["name"])

                    target_comps = set(target_comps)
                    source_comps = set(source_comps)
                    diff = source_comps - target_comps

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["licenses"] != rule["licenses"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["watches"] != rule["watches"]:
                        is_diff = True
                except KeyError:
                    pass

                if is_diff:
                    print("Rule", rule_id, "already exists, but it's not the same. Needs update.")
                else:
                    print("Rule", rule_id, "already exists.")

            else:
                print("Error for rule", rule_id, "unexpected status code", rt2_rule.status_code)

    def create_missing_and_update_policies(self):
        self.update_all_xray_data()
        for policy in self.rt1.xray_policies:
            policy_name = policy["name"]
            rt2_policy = requests.get(self.rt2.url + "/xray/api/v2/policies/" + policy_name, headers=self.headers, verify=False)
            if rt2_policy.status_code == 404:
                print("Policy", policy_name, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v2/policies", json=policy,
                                    headers=self.headers)
                if resp.status_code == 200:
                    print(resp.text)
                else:
                    print("Non 200 status code", resp.status_code)
                    print(resp.text)
            elif rt2_policy.status_code == 200:
                # The policy may still be different (author, creation date, and modification date will
                target_policy = rt2_policy.json()
                if target_policy["rules"] == policy["rules"]:
                    # Rules are the same
                    try:
                        if target_policy["description"] == policy["description"]:
                            print("Policy", policy_name, "already exists. They are the same")
                        else:
                            print("Policy", policy_name,
                                  "already exists. Descriptions are not the same, needs updating.")
                            headers = {'content-type': 'application/json', }
                            resp = requests.put(self.rt2.url + "/xray/api/v2/policies/" + policy_name, json=policy,
                                                headers=self.headers)

                            if resp.status_code == 200:
                                print("Success updating", policy_name)
                            else:
                                print("Non 200 status code while updating", policy_name)
                    except KeyError:
                        # Sometimes there is no description. that's fine.
                        print("Policy", policy_name, "already exists. They are the same")
                else:
                    print("Policy", policy_name, "already exists. Rules are the not same, needs updating.")
                    headers = {'content-type': 'application/json', }
                    resp = requests.put(self.rt2.url + "/xray/api/v2/policies/" + policy_name, json=policy,
                                         headers=self.headers)

                    if resp.status_code == 200:
                        print("Success updating", policy_name)
                    else:
                        print("Non 200 status code", resp.status_code ,"while updating", policy_name)

            else:
                print("Error for policy", policy_name, "unexpected status code", rt2_policy.status_code)

    def create_missing_and_update_watches(self):
        self.update_all_xray_data()
        for watch in self.rt1.xray_watches:
            watch_name = watch["general_data"]["name"]
            rt2_watch = requests.get(self.rt2.url + "/xray/api/v2/watches/" + watch_name, headers=self.headers, verify=False)
            if rt2_watch.status_code == 404:
                print("Watch", watch_name, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v2/watches", json=watch,
                                    headers=self.headers)
                if resp.status_code == 201:
                    print(resp.text)
                else:
                    print("Non 201 status code", resp.status_code)
                    print(resp.text)
            elif rt2_watch.status_code == 200:
                target_watch = rt2_watch.json()
                is_different = False

                try:
                    target_res = []
                    for i in target_watch["project_resources"]["resources"]:
                        target_res.append(i["name"])

                    source_res = []
                    for i in watch["project_resources"]["resources"]:
                        source_res.append(i["name"])

                    target_res = set(target_res)
                    source_res = set(source_res)
                    diff = source_res-target_res

                    if len(diff) != 0:
                        is_different = True

                except KeyError:
                    pass

                try:
                    if target_watch["watch_recipients"] != watch["watch_recipients"]:
                        is_different = True
                except KeyError:
                    # print("No watch recipients")
                    pass
                try:
                    if target_watch["assigned_policies"] != watch["assigned_policies"]:
                        is_different = True
                except KeyError:
                    pass
                    # print("No assigned policies")

                if is_different:
                    print("Watch", watch_name, "already exists, but it's not the same. Needs update.")
                    headers = {'content-type': 'application/json', }
                    resp = requests.put(self.rt2.url + "/xray/api/v2/watches/" + watch_name, json=watch,
                                        headers=self.headers)
                    if resp.status_code == 200:
                        print("Success updating", watch_name)
                    else:
                        print("Non 200 status code", resp.status_code, "while updating", watch_name)
                else:
                    print("Watch", watch_name, "already exists.")

            else:
                print("Error for watch", watch_name, "unexpected status code", rt2_watch.status_code)

    def create_missing_and_update_ignore_rules(self):
        self.update_all_xray_data()
        for rule in self.rt1.xray_ignore_rules["data"]:
            rule_id = rule["id"]
            rt2_rule = requests.get(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, headers=self.headers,
                                    verify=False)
            if rt2_rule.status_code == 404:
                print("Ignore Rule", rule_id, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v1/ignore_rules", json=rule,
                                    headers=self.headers)
                if resp.status_code == 201:
                    print("Success creating", rule_id)
                else:
                    print("Non 201 status code", resp.status_code,  "for Ignore Rule", rule_id)
                    print(resp.text)
            elif rt2_rule.status_code == 200:
                target_rule = rt2_rule.json()
                is_diff = False
                try:
                    target_comps = []
                    for i in target_rule["components"]:
                        target_comps.append(i["name"])

                    source_comps = []
                    for i in rule["components"]:
                        source_comps.append(i["name"])

                    target_comps = set(target_comps)
                    source_comps = set(source_comps)
                    diff = source_comps - target_comps

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["licenses"] != rule["licenses"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["watches"] != rule["watches"]:
                        is_diff = True
                except KeyError:
                    pass
                    # print("No assigned policies")

                if is_diff:
                    print("Ignore Rule", rule_id, "already exists, but it's not the same. Needs update.")
                    headers = {'content-type': 'application/json', }
                    print("Deleting Ignore Rule in Target:", rule_id)
                    resp = requests.delete(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, json=rule,
                                        headers=self.headers)
                    if resp.status_code == 204:
                        print("Success udeleting", rule_id)
                    else:
                        print("Non 200 status code", resp.status_code, "while deleting", rule_id)
                    print("Creating Ignore Rule in Target:", rule_id)
                    headers = {'content-type': 'application/json', }
                    resp = requests.post(self.rt2.url + "/xray/api/v1/ignore_rules", json=rule,
                                         headers=self.headers)
                    if resp.status_code == 201:
                        print("Success creating", rule_id)
                    else:
                        print("Non 201 status code", resp.status_code, "for Ignore Rule", rule_id)
                        print(resp.text)

                else:
                    print("Ignore Rule", rule_id, "already exists.")

            else:
                print("Error for Ignore Rule", rule_id, "unexpected status code", rt2_rule.status_code)

    # Projects stuff
    def get_projects(self):
        """Get list of projects from source"""
        url = f"{self.rt1.url}/access/api/v1/projects"
        debug_request('GET', url, headers=self.rt1.headers, debug=self.rt1.debug)
        resp = requests.get(url, headers=self.rt1.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting projects: {resp.status_code} - {resp.text}")
            return []
        return [project["project_key"] for project in resp.json()]

    def create_project(self, project_data):
        """Create project in target"""
        url = f"{self.rt2.url}/access/api/v1/projects"
        debug_request('POST', url, headers=self.rt2.headers, json_data=project_data, debug=self.rt2.debug)
        resp = requests.post(url, headers=self.rt2.headers, json=project_data, verify=False)
        return resp.status_code == 201, resp

    def update_project(self, project_key, project_data):
        """Update existing project in target"""
        url = f"{self.rt2.url}/access/api/v1/projects/{project_key}"
        debug_request('PUT', url, headers=self.rt2.headers, json_data=project_data, debug=self.rt2.debug)
        resp = requests.put(url, headers=self.rt2.headers, json=project_data, verify=False)
        return resp.status_code == 200, resp

    def sync_projects(self):
        """Sync all projects from source to target"""
        print("\nSyncing projects...")
        
        # Get projects from both instances
        source_projects = {p["project_key"]: p for p in self.rt1.get_project_details()}
        target_projects = {p["project_key"]: p for p in self.rt2.get_project_details()}
        
        # Track failed operations
        failed_projects = []
        
        # Process each source project
        for project_key, source_project in source_projects.items():
            if project_key not in target_projects:
                # Create missing project
                print(f"Creating project: {project_key}")
                success, resp = self.create_project(source_project)
                if success:
                    success_msg = f"Created project: {project_key}"
                    print(success_msg)
                    thread_safe_log(success_msg, './sync_projects_success.log')
                else:
                    error_msg = f"Failed to create project {project_key}: {resp.status_code} - {resp.text}"
                    print(error_msg)
                    thread_safe_log(error_msg, './sync_projects_errors.log')
                    failed_projects.append(project_key)
            else:
                # Check if project needs updating
                target_project = target_projects[project_key]
                if source_project != target_project:
                    print(f"Updating project: {project_key}")
                    success, resp = self.update_project(project_key, source_project)
                    if success:
                        success_msg = f"Updated project: {project_key}"
                        print(success_msg)
                        thread_safe_log(success_msg, './sync_projects_success.log')
                    else:
                        error_msg = f"Failed to update project {project_key}: {resp.status_code} - {resp.text}"
                        print(error_msg)
                        thread_safe_log(error_msg, './sync_projects_errors.log')
                        failed_projects.append(project_key)
        
        # Print summary of failed operations
        if failed_projects:
            failed_projects_str = ";".join(failed_projects)
            print("\nFailed projects (semicolon-separated):")
            print(failed_projects_str)
            thread_safe_log("\nFailed projects (semicolon-separated):", './sync_projects_errors.log')
            thread_safe_log(failed_projects_str, './sync_projects_errors.log')
        
        return failed_projects

    # Environments stuff
    def get_global_environments(self):
        """Get global environments from source"""
        url = f"{self.rt1.url}/access/api/v1/environments"
        debug_request('GET', url, headers=self.rt1.headers, debug=self.rt1.debug)
        resp = requests.get(url, headers=self.rt1.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting global environments: {resp.status_code} - {resp.text}")
            return []
        return resp.json()

    def create_global_environment(self, env_data):
        """Create global environment in target"""
        url = f"{self.rt2.url}/access/api/v1/environments"
        debug_request('POST', url, headers=self.rt2.headers, json_data=env_data, debug=self.rt2.debug)
        resp = requests.post(url, headers=self.rt2.headers, json=env_data, verify=False)
        return resp.status_code == 201, resp

    def get_project_environments(self, project_key):
        """Get environments for a specific project"""
        url = f"{self.rt1.url}/access/api/v1/projects/{project_key}/environments"
        debug_request('GET', url, headers=self.rt1.headers, debug=self.rt1.debug)
        resp = requests.get(url, headers=self.rt1.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting environments for project {project_key}: {resp.status_code} - {resp.text}")
            return []
        return resp.json()

    def create_project_environment(self, project_key, env_data):
        """Create project environment in target"""
        url = f"{self.rt2.url}/access/api/v1/projects/{project_key}/environments"
        debug_request('POST', url, headers=self.rt2.headers, json_data=env_data, debug=self.rt2.debug)
        resp = requests.post(url, headers=self.rt2.headers, json=env_data, verify=False)
        return resp.status_code == 201, resp

    def sync_environments(self):
        """Sync all environments from source to target"""
        print("\nSyncing environments...")
        error_file = f'./sync_environments_errors.log'
        success_file = f'./sync_environments_success.log'

        # Sync global environments
        print("\nSyncing global environments...")
        source_global_envs = self.get_global_environments()
        target_global_envs = []
        try:
            target_global_envs = requests.get(f"{self.rt2.url}/access/api/v1/environments", 
                                            headers=self.rt2.headers, verify=False).json()
        except:
            pass

        target_env_names = [env["name"] for env in target_global_envs]
        
        for env in source_global_envs:
            if env["name"] not in target_env_names:
                print(f"Creating global environment: {env['name']}")
                success, resp = self.create_global_environment(env)
                if success:
                    thread_safe_log(f"Created global environment: {env['name']}", success_file)
                else:
                    error_msg = f"Failed to create global environment {env['name']}: {resp.status_code} - {resp.text}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)

        # Sync project environments
        print("\nSyncing project environments...")
        projects = self.get_projects()
        
        for project_key in projects:
            print(f"\nProcessing project: {project_key}")
            source_project_envs = self.get_project_environments(project_key)
            target_project_envs = []
            try:
                target_project_envs = requests.get(f"{self.rt2.url}/access/api/v1/projects/{project_key}/environments", 
                                                 headers=self.rt2.headers, verify=False).json()
            except:
                pass

            target_env_names = [env["name"] for env in target_project_envs]
            
            for env in source_project_envs:
                if env["name"] not in target_env_names:
                    print(f"Creating environment {env['name']} in project {project_key}")
                    success, resp = self.create_project_environment(project_key, env)
                    if success:
                        thread_safe_log(f"Created environment {env['name']} in project {project_key}", success_file)
                    else:
                        error_msg = f"Failed to create environment {env['name']} in project {project_key}: {resp.status_code} - {resp.text}"
                        print(error_msg)
                        thread_safe_log(error_msg, error_file)


    def assign_environment_to_repos(self, environment, repo_name=None, repo_type=None, max_workers=4, artifactory_instance='target'):
        """
        Assign environment to repositories with optional filtering by name or type
        artifactory_instance: 'source' or 'target' to specify which instance to modify
        """
        # Select which Artifactory instance to modify
        artifactory = self.rt1 if artifactory_instance == 'source' else self.rt2
        print(f"\nAssigning environment '{environment}' to repositories in {artifactory.name}...")
        error_file = f'./assign_environment_errors.log'
        success_file = f'./assign_environment_success.log'
        
        failed_repos = []
        repos_to_update = {}

        # Handle single repository case
        if repo_name:
            print(f"Looking for repository '{repo_name}' in {artifactory.name}...")
            for configs in [artifactory.local_configs, artifactory.remote_configs, 
                           artifactory.virtual_configs, artifactory.federated_configs]:
                if repo_name in configs:
                    repos_to_update[repo_name] = {'config': configs[repo_name], 'type': configs[repo_name].get('rclass', 'unknown')}
                    break
            if not repos_to_update:
                print(f"Repository {repo_name} not found in {artifactory.name}")
                return
        
        # Handle repository type case
        elif repo_type:
            print(f"Finding all {repo_type} repositories in {artifactory.name}...")
            if repo_type == 'local':
                repos_to_update.update({name: {'config': config, 'type': 'local'} 
                                      for name, config in artifactory.local_configs.items()
                                      if name not in SYSTEM_REPOS})
            elif repo_type == 'remote':
                repos_to_update.update({name: {'config': config, 'type': 'remote'}
                                      for name, config in artifactory.remote_configs.items()
                                      if name not in SYSTEM_REPOS})
            elif repo_type == 'virtual':
                repos_to_update.update({name: {'config': config, 'type': 'virtual'}
                                      for name, config in artifactory.virtual_configs.items()
                                      if name not in SYSTEM_REPOS})
            elif repo_type == 'federated':
                repos_to_update.update({name: {'config': config, 'type': 'federated'}
                                      for name, config in artifactory.federated_configs.items()
                                      if name not in SYSTEM_REPOS})
            elif repo_type == 'all':
                print("Finding all repositories...")
                repos_to_update.update({name: {'config': config, 'type': 'local'}
                                      for name, config in artifactory.local_configs.items()
                                      if name not in SYSTEM_REPOS})
                repos_to_update.update({name: {'config': config, 'type': 'remote'}
                                      for name, config in artifactory.remote_configs.items()
                                      if name not in SYSTEM_REPOS})
                repos_to_update.update({name: {'config': config, 'type': 'virtual'}
                                      for name, config in artifactory.virtual_configs.items()
                                      if name not in SYSTEM_REPOS})
                repos_to_update.update({name: {'config': config, 'type': 'federated'}
                                      for name, config in artifactory.federated_configs.items()
                                      if name not in SYSTEM_REPOS})
        
        print(f"Found {len(repos_to_update)} repositories to update")
        thread_safe_log(f"Found {len(repos_to_update)} repositories to update", success_file)
        
        def update_single_repo(repo_name, repo_info):
            repo_config = repo_info['config'].copy()
            repo_config["environments"] = [environment]
            repo_config["rclass"] = repo_info['type']
            
            resp = requests.post(
                f"{artifactory.url}/artifactory/api/repositories/{repo_name}",
                json=repo_config,
                headers=artifactory.headers,
                verify=False
            )
            return repo_name, resp
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(update_single_repo, repo_name, repo_info): repo_name
                for repo_name, repo_info in repos_to_update.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                try:
                    result = future.result()
                    if result:
                        repo_name, resp = result
                        if resp.status_code != 200:
                            error_msg = f"Failed to update environment for repository {repo_name}: {resp.status_code} - {resp.text}"
                            print(error_msg)
                            thread_safe_log(error_msg, error_file)
                            failed_repos.append(repo_name)
                        else:
                            success_msg = f"Successfully assigned environment '{environment}' to repository: {repo_name}"
                            print(success_msg)
                            thread_safe_log(success_msg, success_file)
                except Exception as e:
                    repo_name = future_to_repo[future]
                    print(f"Error processing repository {repo_name}: {str(e)}")
                    thread_safe_log(f"{repo_name} | Exception: {str(e)}", error_file)
                    failed_repos.append(repo_name)
        
        if failed_repos:
            failed_repos_str = ";".join(sorted(failed_repos))
            print("\nFailed repositories (semicolon-separated):")
            print(failed_repos_str)
            thread_safe_log("\nFailed repositories (semicolon-separated):", error_file)
            thread_safe_log(failed_repos_str, error_file)
        

    # PropertySet stuff
    def get_property_sets(self):
        """Get property sets from source"""
        url = f"{self.rt1.url}/artifactory/api/propertysets"
        debug_request('GET', url, headers=self.rt1.headers, debug=self.rt1.debug)
        resp = requests.get(url, headers=self.rt1.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting property sets: {resp.status_code} - {resp.text}")
            return []
        return resp.json()

    def get_property_set_details(self, property_set_name):
        """Get details of a specific property set from source"""
        url = f"{self.rt1.url}/artifactory/api/propertysets/{property_set_name}"
        debug_request('GET', url, headers=self.rt1.headers, debug=self.rt1.debug)
        resp = requests.get(url, headers=self.rt1.headers, verify=False)
        if resp.status_code != 200:
            print(f"Error getting property set details for {property_set_name}: {resp.status_code} - {resp.text}")
            return None
        return resp.json()

    def create_property_set(self, property_set_name, property_set_data):
        """Create property set in target"""
        url = f"{self.rt2.url}/artifactory/api/propertysets"
        
        # Ensure the property set data has the correct name
        property_set_data["name"] = property_set_name
        
        debug_request('POST', url, headers=self.rt2.headers, json_data=property_set_data, debug=self.rt2.debug)
        resp = requests.post(url, headers=self.rt2.headers, json=property_set_data, verify=False)
        
        return resp.status_code in [200, 201], resp

    def sync_property_sets(self):
        """Sync all property sets from source to target"""
        print("\nSyncing property sets...")
        error_file = f'./sync_propertysets_errors.log'
        success_file = f'./sync_propertysets_success.log'

        # Get source property sets
        source_property_sets = self.get_property_sets()
        
        # Get target property sets
        target_property_sets = []
        try:
            target_property_sets = requests.get(f"{self.rt2.url}/artifactory/api/propertysets", 
                                              headers=self.rt2.headers, verify=False).json()
        except:
            pass

        # Extract property set names from target
        target_property_set_names = set()
        if isinstance(target_property_sets, list):
            for prop_set in target_property_sets:
                if isinstance(prop_set, dict) and 'name' in prop_set:
                    target_property_set_names.add(prop_set['name'])
                elif isinstance(prop_set, str):
                    target_property_set_names.add(prop_set)
        
        # Track failed property sets
        failed_property_sets = []

        # Process source property sets
        for prop_set in source_property_sets:
            # Handle both dictionary and string cases
            property_set_name = prop_set['name'] if isinstance(prop_set, dict) else prop_set
            
            if property_set_name not in target_property_set_names:
                print(f"Processing property set: {property_set_name}")
                
                # Get detailed configuration of the property set
                property_set_data = self.get_property_set_details(property_set_name)
                if property_set_data is None:
                    error_msg = f"Failed to get details for property set: {property_set_name}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
                    failed_property_sets.append(property_set_name)
                    continue

                # Create property set in target
                success, resp = self.create_property_set(property_set_name, property_set_data)
                if success:
                    success_msg = f"Created property set: {property_set_name}"
                    print(success_msg)
                    thread_safe_log(success_msg, success_file)
                else:
                    error_msg = f"Failed to create property set {property_set_name}: {resp.status_code} - {resp.text}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
                    failed_property_sets.append(property_set_name)
            else:
                print(f"Property set already exists in target: {property_set_name}")

        # Print summary of failed property sets
        if failed_property_sets:
            failed_sets_str = ";".join(failed_property_sets)
            print("\nFailed property sets (semicolon-separated):")
            print(failed_sets_str)
            thread_safe_log("\nFailed property sets (semicolon-separated):", error_file)
            thread_safe_log(failed_sets_str, error_file)


    def get_filtered_repos_to_create(self, source_configs, target_configs):
        """
        Filter repositories that need to be created, excluding existing ones
        Args:
            source_configs: Dictionary of source repository configurations
            target_configs: Dictionary of target repository configurations
        Returns:
            dict: Filtered dictionary of repositories to create
        """
        repos_to_create = {}
        
        for repo_name, repo_config in source_configs.items():
            if repo_name not in SYSTEM_REPOS and repo_name not in target_configs:
                # Check if repo exists in target (handling docker repo names)
                if not self.rt2.check_repo_exists(repo_name, repo_config.get("packageType")):
                    repos_to_create[repo_name] = repo_config
                else:
                    print(f"Repository {repo_name} already exists in target, skipping creation")
        
        return repos_to_create

    def create_single_repository(self, repo_name, repo_type, environment=None):
        """Create a single repository of specified type on target"""
        print(f"\nCreating single {repo_type} repository: {repo_name}")
        error_file = f'./create_{repo_type}_errors.log'
        success_file = f'./create_{repo_type}_success.log'
        
        # Get source configuration based on repo type
        source_config = None
        if repo_type == 'local':
            if repo_name not in self.rt1.local_configs:
                print(f"Error: Repository {repo_name} not found in source")
                return None, "Repository not found in source"
            source_config = self.rt1.local_configs[repo_name]
        elif repo_type == 'remote':
            if repo_name not in self.rt1.remote_configs:
                print(f"Error: Repository {repo_name} not found in source")
                return None, "Repository not found in source"
            source_config = self.rt1.remote_configs[repo_name]
        elif repo_type == 'virtual':
            if repo_name not in self.rt1.virtual_configs:
                print(f"Error: Repository {repo_name} not found in source")
                return None, "Repository not found in source"
            source_config = self.rt1.virtual_configs[repo_name]            
        elif repo_type == 'federated':
            if repo_name not in self.rt1.federated_configs:
                print(f"Error: Repository {repo_name} not found in source")
                return None, "Repository not found in source"
            source_config = self.rt1.federated_configs[repo_name]
        
        repo = source_config.copy()
        project_key = repo.pop("projectKey", None)
        
        # Set common properties
        repo["rclass"] = repo_type
        repo["dockerApiVersion"] = "V2"
        repo["packageType"] = repo.get("packageType", "maven")
        repo["repoLayoutRef"] = repo.get("repoLayoutRef", "maven-2-default")
        
        if environment:
            repo["environments"] = [environment]
            
        # Handle type-specific configurations
        if repo_type == 'remote':
            repo["password"] = ""  # Clear password for safety
        elif repo_type == 'virtual':
            # Check for dependent repositories
            if "repositories" in repo:
                missing_deps = []
                for dep_repo in repo["repositories"]:
                    if not self.rt2.check_repo_exists(dep_repo, repo["packageType"]):
                        missing_deps.append(dep_repo)
                        print(f"Warning: Dependent repository {dep_repo} for virtual repo {repo_name} does not exist")
                
                if missing_deps:
                    error_msg = f"Cannot create virtual repository {repo_name} - missing dependent repositories: {', '.join(missing_deps)}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
                    return None, error_msg
        elif repo_type == 'federated':
            repo["members"] = [{"url": f"{self.rt1.url}/artifactory/{repo_name}", "enabled": "true"}]
            
        # Create repository
        resp = requests.put(
            f"{self.rt2.url}/artifactory/api/repositories/{repo_name}",
            json=repo,
            headers=self.rt2.headers,
            verify=False
        )
        # If creation fails with illegal character error for Docker repos, try with hyphens
        if (resp.status_code == 400 and 
            repo["packageType"] == "docker"):
            
            error_msg = f"Docker repository creation failed: {repo_name}"
            print(error_msg)
            thread_safe_log(error_msg, error_file)
            thread_safe_log(f"Response: {resp.status_code} - {resp.text}", error_file)
            
            # Replace underscores or dots with hyphens in repo name and config
            new_repo_name = repo_name.replace('_', '-').replace('.', '-')
            repo["key"] = new_repo_name
            
            print(f"Retrying with modified name: {new_repo_name}")
            
            # Check if repository with hyphenated name already exists
            if self.rt2.check_repo_exists(new_repo_name, repo["packageType"]):
                error_msg = f"Repository {new_repo_name} already exists in target"
                print(error_msg)
                thread_safe_log(error_msg, error_file)
                return None, error_msg
            
            # Retry with modified name
            resp = requests.put(
                f"{self.rt2.url}/artifactory/api/repositories/{new_repo_name}",
                json=repo,
                headers=self.rt2.headers,
                verify=False
            )
            
            # Update repo_name for further processing if successful
            if resp.status_code == 200:
                repo_name = new_repo_name
        
        if resp.status_code == 200:
            success_msg = f"Successfully created {repo_type} repository: {repo_name}"
            print(success_msg)
            thread_safe_log(success_msg, success_file)
            
            if project_key:
                success, assign_resp = self.rt2.assign_repo_to_project(repo_name, project_key)
                if not success:
                    error_msg = f"Warning: Repository {repo_name} created but failed to assign to project {project_key}: {assign_resp.status_code} - {assign_resp.text}"
                    print(error_msg)
                    thread_safe_log(error_msg, error_file)
                else:
                    success_msg = f"Successfully assigned repository {repo_name} to project {project_key}"
                    print(success_msg)
                    thread_safe_log(success_msg, success_file)
            return resp, None
        else:
            error_msg = f"Failed to create {repo_type} repository {repo_name}: {resp.status_code} - {resp.text}"
            print(error_msg)
            thread_safe_log(error_msg, error_file)
            return None, error_msg

    # Replace the old individual create methods with calls to create_single_repository
    def create_single_local_on_target(self, repo_name, environment=None):
        self.create_single_repository(repo_name, 'local', environment)
        
    def create_single_remote_on_target(self, repo_name, environment=None):
        self.create_single_repository(repo_name, 'remote', environment)
        
    def create_single_virtual_on_target(self, repo_name, environment=None):
        self.create_single_repository(repo_name, 'virtual', environment)
        
    def create_single_federated_on_target(self, repo_name, environment=None):
        self.create_single_repository(repo_name, 'federated', environment)



def parse_args():
    parser = argparse.ArgumentParser(
        description='Sync repositories between Artifactory instances'
    )
    
    # Required arguments
    parser.add_argument(
        '--source-url',
        required=True,
        help='Source Artifactory URL'
    )
    parser.add_argument(
        '--source-token',
        required=True,
        help='Source Artifactory access token'
    )
    parser.add_argument(
        '--target-url',
        required=True,
        help='Target Artifactory URL'
    )
    parser.add_argument(
        '--target-token',
        required=True,
        help='Target Artifactory access token'
    )

    # Command argument
    parser.add_argument(
        'command',
        choices=[
            'report',
            'remotes_with_password_source',
            'remotes_with_password_target',
            'refresh_storage_summary',
            'sync_environments',
            'sync_property_sets',
            'sync_projects',
            'list_missing_projects_source',
            'list_missing_projects_target',
            'create_missing_locals_on_target',
            'create_missing_remotes_on_target',
            'create_missing_virtuals_on_target',
            'create_missing_federated_on_target',
            'update_locals_on_target_dry',
            'update_locals_on_target',
            'update_remotes_on_target_dry',
            'update_remotes_on_target',
            'update_federated_repos_on_target_dry',
            'update_federated_repos_on_target',
            'update_virtuals_on_target',
            'update_virtuals_on_target_dry',                        
            'delete_repos_from_file',
            'delete_repos_by_type',            
            'xray_report',
            'sync_xray_policies',
            'sync_xray_watches',
            'sync_xray_ignore_rules',
            'assign_environment',
            'create_single_local',
            'create_single_remote', 
            'create_single_virtual',
            'create_single_federated'
        ],
        help='Command to execute'
    )

    # Add arguments for delete operations
    parser.add_argument(
        '--repo-list-file',
        help='File containing repository keys to delete (one per line)'
    )

    # Single repo-type argument for all operations (delete, assign, etc.)
    parser.add_argument(
        '--repo-type',
        choices=['local', 'remote', 'federated', 'virtual', 'all'],
        help='Type of repositories to process (for delete or assign operations)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List repositories that would be deleted without actually deleting them'
    )

    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel workers for repository creation (default: 4)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output including curl commands'
    )

    # Add environment argument
    parser.add_argument(
        '--environment',
        help='Environment to assign to repositories'
    )

    parser.add_argument(
        '--repo-name',
        help='Repository name for single repository operations like create repo or assign environment to (optional)'
    )

    parser.add_argument(
        '--artifactory',
        choices=['source', 'target'],
        default='target',
        help='Which Artifactory instance to modify (default: target)'
    )

    return parser.parse_args()

def main():
    args = parse_args()

    # Create authentication tuples for each instance
    if args.source_token.startswith('Bearer '):
        source_token = args.source_token[7:]  # Remove 'Bearer ' prefix
    else:
        source_token = args.source_token

    if args.target_token.startswith('Bearer '):
        target_token = args.target_token[7:]  # Remove 'Bearer ' prefix
    else:
        target_token = args.target_token

    source_auth = ('_token', source_token)
    target_auth = ('_token', target_token)

    if args.debug:
        print("\nSource URL:", args.source_url)
        print("Target URL:", args.target_url)
        print("Source token type:", "Bearer token" if args.source_token.startswith('Bearer ') else "Access token")
        print("Target token type:", "Bearer token" if args.target_token.startswith('Bearer ') else "Access token")

    # Initialize the objects that help us interact
    source = Artifactory(args.source_url, source_auth, "source", debug=args.debug)
    target = Artifactory(args.target_url, target_auth, "target", debug=args.debug)
    helper = ArtifactoryHelper(source, target)

    # Execute the requested command
    if args.command == "report":
        helper.repo_report()

    elif args.command == "remotes_with_password_source":
        source.print_missing_remotes_with_password(target)

    elif args.command == "remotes_with_password_target":
        target.print_remotes_with_password()

    elif args.command == "refresh_storage_summary":
        helper.refresh_storage_summary()

    elif args.command == "sync_environments":
        helper.sync_environments()

    elif args.command == "sync_property_sets":
        helper.sync_property_sets()

    elif args.command == "sync_projects":
        helper.sync_projects()

    elif args.command == "create_missing_federated_on_target":
        helper.create_missing_federated_repos_on_target_parallel(max_workers=args.max_workers, environment=args.environment)

    elif args.command == "create_missing_remotes_on_target":
        helper.create_missing_remotes_on_target_parallel(args.max_workers, environment=args.environment)

    elif args.command == "create_missing_virtuals_on_target":
        helper.create_missing_virtuals_on_target_parallel(max_workers=args.max_workers, environment=args.environment)

    elif args.command == "create_missing_locals_on_target":
        helper.create_missing_locals_on_target_parallel(args.max_workers, environment=args.environment)

    elif args.command == "list_missing_projects_source":
        target.print_missing_projects(source)

    elif args.command == "list_missing_projects_target":
        source.print_missing_projects(target)

    elif args.command == "update_locals_on_target_dry":
        helper.update_locals_on_target_parallel(dry=True, max_workers=args.max_workers)
    
    elif args.command == "update_locals_on_target":
        helper.update_locals_on_target_parallel(dry=False, max_workers=args.max_workers)
    
    elif args.command == "update_remotes_on_target_dry":
        helper.update_remotes_on_target_parallel(dry=True, max_workers=args.max_workers)
    
    elif args.command == "update_remotes_on_target":
        helper.update_remotes_on_target_parallel(dry=False, max_workers=args.max_workers)
    
    elif args.command == "update_federated_repos_on_target_dry":
        helper.update_federated_repos_on_target_parallel(dry=True, max_workers=args.max_workers)
    
    elif args.command == "update_federated_repos_on_target":
        helper.update_federated_repos_on_target_parallel(dry=False, max_workers=args.max_workers)

    elif args.command == "update_virtuals_on_target":
        helper.update_virtuals_on_target_parallel(dry=False, max_workers=args.max_workers)

    elif args.command == "update_virtuals_on_target_dry":
        helper.update_virtuals_on_target_parallel(dry=True, max_workers=args.max_workers)

    elif args.command == "delete_repos_from_file":
        if not args.repo_list_file:
            print("Error: --repo-list-file is required for delete_repos_from_file command")
            sys.exit(1)
        target.delete_repositories_from_file_parallel(args.repo_list_file, args.max_workers, args.dry_run)

    elif args.command == "delete_repos_by_type":
        if not args.repo_type:
            print("Error: --repo-type is required for delete_repos_by_type command")
            sys.exit(1)
        target.delete_repositories_by_type_parallel(args.repo_type, args.max_workers, args.dry_run)

    elif args.command == "xray_report":
        helper.report_watches_policies()

    elif args.command == "sync_xray_policies":
        helper.create_missing_and_update_policies()

    elif args.command == "sync_xray_watches":
        helper.create_missing_and_update_watches()

    elif args.command == "sync_xray_ignore_rules":
        helper.create_missing_and_update_ignore_rules()

    elif args.command == "assign_environment":
        if not args.environment:
            print("Error: --environment is required for assign_environment command")
            sys.exit(1)
        
        # For target operations, ensure target details are provided
        if args.artifactory == 'target' and (not args.target_url or not args.target_token):
            print("Error: --target-url and --target-token are required for target operations")
            sys.exit(1)
            
        helper.assign_environment_to_repos(
            environment=args.environment,
            repo_name=args.repo_name,
            repo_type=args.repo_type,
            max_workers=args.max_workers,
            artifactory_instance=args.artifactory
        )

    elif args.command == "create_single_local":
        if not args.repo_name:
            print("Error: --repo-name is required for create_single_local command")
            sys.exit(1)
        helper.create_single_local_on_target(args.repo_name, args.environment)
        
    elif args.command == "create_single_remote":
        if not args.repo_name:
            print("Error: --repo-name is required for create_single_remote command")
            sys.exit(1)
        helper.create_single_remote_on_target(args.repo_name, args.environment)
        
    elif args.command == "create_single_virtual":
        if not args.repo_name:
            print("Error: --repo-name is required for create_single_virtual command")
            sys.exit(1)
        helper.create_single_virtual_on_target(args.repo_name, args.environment)
        
    elif args.command == "create_single_federated":
        if not args.repo_name:
            print("Error: --repo-name is required for create_single_federated command")
            sys.exit(1)
        helper.create_single_federated_on_target(args.repo_name, args.environment)



if __name__ == '__main__':
    main()