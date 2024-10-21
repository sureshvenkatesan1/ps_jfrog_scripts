import argparse
import requests

"""
Find Unshared Repositories in a JFrog Artifactory Project

This script allows you to find repositories in a JFrog Artifactory project that are not shared with the specified project.

Usage:
    python find_unshared_repositories_in_project.py --project-key <project_key> --access-token <access_token> --base-url <base_url>

Options:
    --project-key <project_key>   The key of the project you want to check for unshared repositories.
    --access-token <access_token> Your access token for authentication.
    --base-url <base_url>         The base URL of the Artifactory service (e.g., https://proservices.jfrog.io).

Example:
    python find_unshared_repositories_in_project.py --project-key my-project --access-token my-access-token --base-url https://proservices.jfrog.io

Note:
    This script retrieves information about local, remote, and virtual repositories within the specified project.
    It identifies repositories that are not shared with the project specified by '--project-key' and lists their names.

    Make sure to provide the correct 'project-key', 'access-token', and 'base-url' parameters.
"""

def get_repositories_by_type(project_key, access_token, base_url, repo_type):
    url = f"{base_url}/ui/api/v1/ui/admin/repositories/{repo_type}/info?projectKey={project_key}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch {repo_type} repository data. Status code: {response.status_code}")
        return []

    repositories = response.json()
    if repo_type == "virtual":
        # Handle virtual repositories differently
        selected_repos = []
        for repo in repositories:
            selected_repos.extend(repo.get("selectedRepos", []))
        """
        return just the "selectedRepos" list i.e [
              "p1-lr1",
              "p2-lr2"
            ]
        """
        return selected_repos
    """
    for all other repo types return the return the list of repo detail json , for example :
    [{
        "repoKey": "p1-lr1",
        "repoType": "Generic",
        "hasReindexAction": false,
        "projectKey": "p1",
        "projectName": "project1",
        "environments": [
            "DEV"
        ],
        "sharedWithProjects": [
            "p2"
        ],
        "shareWithAllProjects": false,
        "replications": false,
        "target": true,
        "sharedReadOnly": false
    }]
    """
    return repositories

import requests

def get_project_key_and_repo_type(repo_key, access_token, base_url):
    # Set up the headers with the authorization token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Create the URL based on the repo key
    url = f"{base_url}/artifactory/api/repositories/{repo_key}"

    # Send the GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract the value of the "projectKey" field
        project_key = data.get("projectKey")
        repo_type = data.get("rclass")

        if project_key is not None:
            return project_key , repo_type
        else:
            return None , repo_type
    else:
        print(f"Failed to retrieve data for repo key '{repo_key}'. Status code: {response.status_code}")
        return None




def find_unshared_repositories(project_key, access_token, base_url):
    local_repositories = get_repositories_by_type(project_key, access_token, base_url, "local")
    remote_repositories = get_repositories_by_type(project_key, access_token, base_url, "remote")
    selectedRepos_in_virtual_repositories = get_repositories_by_type(project_key, access_token, base_url, "virtual")
    federated_repositories = get_repositories_by_type(project_key, access_token, base_url, "federated")

    unshared_repositories = []
    # all repositories in the project except the virtuals
    all_repositories = local_repositories + remote_repositories +  federated_repositories



    for repo in all_repositories:
        if "sharedWithProjects" in repo and  repo["projectKey"] != project_key \
                and project_key not in repo["sharedWithProjects"] :
            print(f"Repo '{repo['repoKey']}' is unshared with '{project_key}'")
            unshared_repositories.append(repo["repoKey"])

    return (unshared_repositories , selectedRepos_in_virtual_repositories)

def check_shared_with_projects(repo_key, myproject_key , json_data):
    for item in json_data:
        if item.get("repoKey") == repo_key:
            shared_with_projects = item.get("sharedWithProjects", [])
            shareWithAllProjects = item.get("shareWithAllProjects", False)
            if (myproject_key in shared_with_projects) or (shareWithAllProjects):
                print(f"return True from check_shared_with_projects. "
                      f"item= '{item}', "
                      f"myproject_key= '{myproject_key}', "
                      f"shared_with_projects = '{shared_with_projects}' , "
                      f"shareWithAllProjects = '{shareWithAllProjects}'")
                return True
            else:
                print(f"return False from check_shared_with_projects. "
                      f"item= '{item}', "
                      f"myproject_key= '{myproject_key}', "
                      f"shared_with_projects = '{shared_with_projects}' , "
                      f"shareWithAllProjects = '{shareWithAllProjects}'")
                return False
    print(f"item {item} not in json_data = {json_data} . Return False")
    return False

def find_repo_is_unshared_with_my_project(project_key_for_repo_key,
                                          repo_key, repo_type, access_token,
                                          base_url,myproject_key):

    url = f"{base_url}/ui/api/v1/ui/admin/repositories/{repo_type}/info?projectKey={project_key_for_repo_key}"
    headers = {"Authorization": f"Bearer {access_token}"}
    unshared_repositories = []
    selected_repos = []

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch {repo_type} repository data. Status code: {response.status_code}")
        return unshared_repositories , selected_repos
    else:
        repositories = response.json()
        print(f"{base_url}/ui/api/v1/ui/admin/repositories/{repo_type}/info?projectKey={project_key_for_repo_key} "
              f"response is {repositories}")
        if not check_shared_with_projects(repo_key, myproject_key , repositories) and project_key_for_repo_key != myproject_key:
            print(f"---Repo '{repo_key}' is unshared with '{myproject_key}' . Here is '{project_key_for_repo_key}'")
            unshared_repositories.append(repo_key)
        if repo_type == "virtual":
            for repo in repositories:
                if repo.get("repoKey") == repo_key:
                    selected_repos.extend(repo.get("selectedRepos", []))

    return (unshared_repositories , selected_repos)

def find_selectedRepos_in_virtual_unshared_with_my_project( access_token, base_url, selected_repos, myproject_key):
    unshared_repositories = []

    for repo_key in selected_repos:
        project_key_for_repo_key , repo_type = get_project_key_and_repo_type(repo_key, access_token, base_url)
        print(f"{repo_key}'s project is {project_key_for_repo_key} and repo_type is  {repo_type}")

        #repo can be assigned max to only one project
        if project_key_for_repo_key is not None:
            print(f"Project Key for repo '{repo_key}': {project_key_for_repo_key}")
            sub_unshared_repos, sub_selected_repos = find_repo_is_unshared_with_my_project(project_key_for_repo_key,
                                                                                           repo_key, repo_type,
                                                                                           access_token,
                                                                                        base_url, myproject_key)
            unshared_repositories.extend(sub_unshared_repos)
            if sub_selected_repos:
                find_selectedRepos_in_virtual_unshared_with_my_project(access_token, base_url, sub_selected_repos, myproject_key)
            else:
                print(f"There are no sub_selected_repos .. ending recursion")
        else:
            print(f"No project key found for repo '{repo_key}'. So we cannot find the 'sharedWithProjects' for this "
                  f"repo ")
            unshared_repositories.extend(repo_key)

    return unshared_repositories

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find unshared repositories in a project")
    parser.add_argument("--project-key", required=True, help="The project key")
    parser.add_argument("--access-token", required=True, help="Your access token")
    parser.add_argument("--base-url", required=True, help="Base URL of the Artifactory service (e.g., https://proservices.jfrog.io)")

    args = parser.parse_args()

    project_key = args.project_key
    access_token = args.access_token
    base_url = args.base_url

    unshared_repositories, selectedRepos_in_virtual_repositories = find_unshared_repositories(project_key, access_token, base_url)

    if unshared_repositories:
        print("Repositories not shared with", project_key)
        for repo_key in unshared_repositories:
            print(repo_key)
    elif selectedRepos_in_virtual_repositories:
        print(f"Check if the following 'selectedRepos' in the Virtual Repositories are shared with the projectKey {project_key} :")
        print("*" * 30 + "\n")
        unshared_repos = find_selectedRepos_in_virtual_unshared_with_my_project( access_token, base_url,
                                                          selectedRepos_in_virtual_repositories, project_key)
        if unshared_repos:
            # Print the banner
            print("*" * 30 + "\n")
            print("Repositories not shared with", project_key)
            for repo_key in unshared_repos:
                print(repo_key)
        else:
            print(f"{unshared_repos} is empty")
    else:
        print("All repositories are shared with", project_key)
