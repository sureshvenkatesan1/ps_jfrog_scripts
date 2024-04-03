import argparse
import requests
import json
from tabulate import tabulate
from urllib.parse import unquote

"""
Usage:
python compare_2_jpd_configs.py https://psazuse.jfrog.io $psazuse_token https://psemea.jfrog.io $psemea_token > jpd_diff.txt
"""

# Function to collect data from a JPD
def collect_data(jpd_url, jpd_token):
    headers = {"Authorization": f"Bearer {jpd_token}"}

    # Function to get entity names
    def get_entity_names(entity_type, entity_url):
        response = requests.get(entity_url, headers=headers)
        if not response.ok:
            try:
                error_message = response.json()["errors"][0]["message"]
                print(f"Failed to fetch data for {entity_type} from {entity_url}. Error message: {error_message}")
            except (json.JSONDecodeError, KeyError, IndexError):
                print(f"Failed to fetch data for {entity_type} from {entity_url}. Status code: {response.status_code}")
            return None, None        
        # entity_data = response.text
        # print(f"Response for {entity_type} from {entity_url}:\n{entity_data}")
        try:
            entity_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for {entity_type} from {entity_url}: {e}")
            return None, None
        if entity_type in ["Users", "Groups", "Permissions", "Tokens"]:
            entity_names = [item["username" if entity_type == "Users" else "group_name" if entity_type == "Groups" else "token_id" if entity_type == "Tokens" else "name"] for item in entity_data.get(entity_type.lower(), [])]
            count = len(entity_names)
        elif entity_type == "Projects":
            entity_names = [project["project_key"] for project in entity_data]
            count = len(entity_names)
        elif entity_type.startswith("Builds"):
            # entity_names = [build["uri"] for build in entity_data.get("builds", [])]
            # Extract URIs from entity_data and decode them
            entity_names = [unquote(build["uri"][1:]) for build in entity_data.get("builds", [])]
            count = len(entity_names)
        elif entity_type == "Property Sets":
            entity_names = [property_set["name"] for property_set in entity_data]
            count = len(entity_names)
        elif entity_type == "Repository Layouts":
            entity_names = [layout["name"] for layout in entity_data]
            count = len(entity_names)
        elif entity_type.startswith("Xray"):
            entity_names, count = get_xray_entity_names(entity_type, entity_data)
        elif entity_type.endswith("Repositories"):
            entity_names = [repository["key"] for repository in entity_data]
            count = len(entity_names)
        else:
            entity_names = []
            count = 0
        return entity_names, count

    # Function to get Xray entity names
    def get_xray_entity_names(entity_type, entity_data):
        if entity_type == "Xray Watches":
            entity_names = [item["general_data"]["name"] for item in entity_data]
        elif entity_type == "Xray Policies":
            entity_names = [item["name"] for item in entity_data]
        elif entity_type == "Xray Ignore Rules":
            entity_names = [item["id"] for item in entity_data["data"]]
        else:
            entity_names = []
        count = len(entity_names)
        return entity_names, count

    # Function to get builds for a project
    def get_project_builds(project_key):
        project_builds_url = f"{jpd_url}/artifactory/api/build?project={project_key}"
        return get_entity_names(f"Builds in Project '{project_key}'", project_builds_url)
    
    data = {}

    # Collecting data for each entity type
    entity_types = [
        ("Local Repositories", "/artifactory/api/repositories?type=local"),
        ("Remote Repositories", "/artifactory/api/repositories?type=remote"),
        ("Virtual Repositories", "/artifactory/api/repositories?type=virtual"),
        ("Federated Repositories", "/artifactory/api/repositories?type=federated"),
        ("Repository Layouts", "/artifactory/api/admin/repolayouts"),
        ("Users", "/access/api/v2/users"),
        ("Groups", "/access/api/v2/groups"),
        ("Permissions", "/access/api/v2/permissions"),
        ("Tokens", "/access/api/v1/tokens"),
        ("Projects", "/access/api/v1/projects"),
        ("Builds", "/artifactory/api/build"),
        ("Property Sets", "/artifactory/api/propertysets"),
        ("Xray Watches", "/xray/api/v2/watches"),
        ("Xray Policies", "/xray/api/v2/policies"),
        ("Xray Ignore Rules", "/xray/api/v1/ignore_rules"),
    ]

    for entity_type, entity_url in entity_types:
        if entity_type == "Projects":
            entity_names, count  = get_entity_names(entity_type, jpd_url + entity_url)
            if entity_names is not None:
                for project_key in entity_names:
                    project_build_names , count_of_project_builds = get_project_builds(project_key)
                    if project_build_names is not None:
                        data[f"Builds in Project '{project_key}'"] = (project_build_names , count_of_project_builds)
        else:
            entity_names, count  = get_entity_names(entity_type, jpd_url + entity_url)
            if entity_names is not None:
                data[entity_type] = (entity_names, count)
    return data

# Function to compare data from two JPDs
# def compare_data(data1, data2):
#     differences = {}
#     for entity_type in data1:
#         entities1 = set(data1[entity_type][0])
#         entities2 = set(data2[entity_type][0])
#         unique_to_data1 = entities1 - entities2
#         unique_to_data2 = entities2 - entities1
#         count_difference = abs(data1[entity_type][1] - data2[entity_type][1])
#         differences[entity_type] = (entities1, entities2, unique_to_data1, unique_to_data2, count_difference)
#     return differences

def compare_data(data1, data2):
    differences = {}
    
    # Find unique entity types in data1
    for entity_type in data1:
        entities1 = set(data1[entity_type][0])
        if entity_type in data2:
            entities2 = set(data2[entity_type][0])
        else:
            entities2 = set()
        unique_to_data1 = entities1 - entities2
        unique_to_data2 = entities2 - entities1
        count_difference = abs(data1[entity_type][1] - data2.get(entity_type, ([], 0))[1])
        differences[entity_type] = (sorted(entities1), sorted(entities2), sorted(unique_to_data1), sorted(unique_to_data2), count_difference)
    
    # Find unique entity types in data2
    for entity_type in data2:
        if entity_type not in data1:
            entities2 = set(data2[entity_type][0])
            entities1 = set()
            unique_to_data1 = set()
            unique_to_data2 = entities2
            count_difference = data2[entity_type][1]
            differences[entity_type] = (sorted(entities1), sorted(entities2), sorted(unique_to_data1), sorted(unique_to_data2), count_difference)
    
    return differences


# Function to display data differences in tabular format
def display_differences(differences):
    table_data = []
    for entity_type, (entities1, entities2, unique_to_data1, unique_to_data2, count_difference) in differences.items():
        table_data.append([entity_type, "\n".join(entities1), "\n".join(entities2), "\n".join(unique_to_data1), "\n".join(unique_to_data2), count_difference])
    print(tabulate(table_data, headers=["Entity Type", "All JPD1 items","All JPD2 items","Unique to JPD 1", "Unique to JPD 2", "Count Difference"], tablefmt="grid"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JFrog Platform Data Comparison Script")
    parser.add_argument("jpd_url1", help="URL of the first JPD")
    parser.add_argument("jpd_token1", help="Token for accessing the first JPD")
    parser.add_argument("jpd_url2", help="URL of the second JPD")
    parser.add_argument("jpd_token2", help="Token for accessing the second JPD")
    args = parser.parse_args()

    # Collect data from both JPDs
    data1 = collect_data(args.jpd_url1, args.jpd_token1)
    data2 = collect_data(args.jpd_url2, args.jpd_token2)

    # Compare the data
    differences = compare_data(data1, data2)

    # Display differences
    display_differences(differences)
