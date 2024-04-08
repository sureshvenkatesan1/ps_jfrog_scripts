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
            return None, None, None
        # entity_data = response.text
        # print(f"Response for {entity_type} from {entity_url}:\n{entity_data}")
        try:
            entity_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for {entity_type} from {entity_url}: {e}")
            return None, None, None

        entity_names = []
        json_data = {}

        if entity_type in ["Users", "Groups", "Permissions", "Tokens"]:
            for item in entity_data.get(entity_type.lower(), []):
                entity_name = item.get("username" if entity_type == "Users" else "group_name" if entity_type == "Groups" else "token_id" if entity_type == "Tokens" else "name")
                entity_names.append(entity_name)
                json_data[entity_name] = item
        elif entity_type == "Projects":
            for project in entity_data:
                project_key = project["project_key"]
                entity_names.append(project_key)
                json_data[project_key] = project
        elif entity_type.startswith("Builds"):
            for build in entity_data.get("builds", []):
                entity_name = unquote(build["uri"][1:])
                entity_names.append(entity_name)
                json_data[entity_name] = build
        elif entity_type == "Property Sets":
            for property_set in entity_data:
                property_set_name = property_set["name"]
                entity_names.append(property_set_name)
                json_data[property_set_name] = property_set
        elif entity_type.startswith("Xray"):
            entity_names, _, json_data = get_xray_entity_names(entity_type, entity_data)
        elif entity_type == "Repository Layouts":
            for layout in entity_data:
                layout_name = layout["name"]
                entity_names.append(layout_name)
                json_data[layout_name] = layout
        elif entity_type.endswith("Repositories"):
            for repository in entity_data:
                repository_key = repository["key"]
                entity_names.append(repository_key)
                json_data[repository_key] = repository

        count = len(entity_names)
        return entity_names, count, json_data

    def get_xray_entity_names(entity_type, entity_data):
        entity_names = []
        json_data = {}

        if entity_type == "Xray Watches":
            for item in entity_data:
                entity_name = item["general_data"]["name"]
                entity_names.append(entity_name)
                json_data[entity_name] = item
        elif entity_type == "Xray Policies":
            for item in entity_data:
                entity_name = item["name"]
                entity_names.append(entity_name)
                json_data[entity_name] = item
        elif entity_type == "Xray Ignore Rules":
            for item in entity_data["data"]:
                entity_name = item["id"]
                entity_names.append(entity_name)
                json_data[entity_name] = item

        return entity_names, len(entity_names), json_data

    def get_project_builds(project_key):
        project_builds_url = f"{jpd_url}/artifactory/api/build?project={project_key}"
        response = requests.get(project_builds_url, headers=headers)
        if not response.ok:
            print(f"Failed to fetch data for Builds in Project '{project_key}' from {project_builds_url}. Status code: {response.status_code}")
            return None, None, None
        try:
            project_builds_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for Builds in Project '{project_key}' from {project_builds_url}: {e}")
            return None, None, None

        project_build_names = []
        builds_json_data = {}

        for build in project_builds_data.get("builds", []):
            entity_name = unquote(build["uri"][1:])
            project_build_names.append(entity_name)
            builds_json_data[entity_name] = build

        count_of_project_builds = len(project_build_names)

        return project_build_names, count_of_project_builds, builds_json_data

    data = {}

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
        entity_names, count, json_data = get_entity_names(entity_type, jpd_url + entity_url)
        if entity_type == "Projects":
            if entity_names is not None:
                for project_key in entity_names:
                    project_build_names, count_of_project_builds, builds_json_data = get_project_builds(project_key)
                    if project_build_names:
                        data[f"Builds in Project '{project_key}'"] = (project_build_names, count_of_project_builds, builds_json_data)
        else:
            if entity_names is not None:
                data[entity_type] = (entity_names, count, json_data)

    return data


# Function to compare data from two JPDs

"""
def compare_data(data1, data2):
    differences = {}

    # Find unique entity types in data1
    for entity_type, (entities1, _, json_data1) in data1.items():
        if entity_type in data2:
            entities2, _, json_data2 = data2[entity_type]
        else:
            entities2 = []
            json_data2 = {}
        unique_to_data1 = set(entities1) - set(entities2)
        unique_to_data2 = set(entities2) - set(entities1)

        entity_diffs = []
        common_entities = set(entities1) & set(entities2)
        for entity in common_entities:
            differing_properties = []
            # Check for differing properties in json_data1[entity]
            for prop in json_data1[entity]:
                if prop not in json_data2[entity] or json_data1[entity][prop] != json_data2[entity][prop]:
                    differing_properties.append(prop)
            # Check for properties in json_data2[entity] that are not in json_data1[entity]
            for prop in json_data2[entity]:
                if prop not in json_data1[entity]:
                    differing_properties.append(prop)
            entity_diffs.append((entity, differing_properties))

        count_difference = abs(len(entities1) - len(entities2))
        differences[entity_type] = (sorted(entities1), sorted(entities2), sorted(unique_to_data1), sorted(unique_to_data2), count_difference, entity_diffs)

    # Find unique entity types in data2
    for entity_type, (entities2, _, _) in data2.items():
        if entity_type not in data1:
            unique_to_data2 = entities2
            count_difference = len(entities2)
            differences[entity_type] = ([], sorted(entities2), [], sorted(unique_to_data2), count_difference, [])

    return differences
"""

def compare_data(data1, data2):
    differences = {}

    # Find unique entity types in data1
    for entity_type, (entities1, _, json_data1) in data1.items():
        if entity_type in data2:
            entities2, _, json_data2 = data2[entity_type]
        else:
            entities2 = []
            json_data2 = {}
        unique_to_data1 = set(entities1) - set(entities2)
        unique_to_data2 = set(entities2) - set(entities1)

        entity_diffs = {}
        common_entities = set(entities1) & set(entities2)
        for entity in common_entities:
            differing_properties = []
            # Check for differing properties in json_data1[entity]
            for prop in json_data1[entity]:
                if prop not in json_data2[entity] or json_data1[entity][prop] != json_data2[entity][prop]:
                    differing_properties.append((prop, (json_data1[entity][prop], json_data2[entity].get(prop, None))))
            # Check for properties in json_data2[entity] that are not in json_data1[entity]
            for prop in json_data2[entity]:
                if prop not in json_data1[entity]:
                    differing_properties.append((prop, (None, json_data2[entity][prop])))
            entity_diffs[entity] = dict(differing_properties)
        count_difference = abs(len(entities1) - len(entities2))
        differences[entity_type] = (sorted(entities1), sorted(entities2), sorted(unique_to_data1), sorted(unique_to_data2), count_difference, entity_diffs)

    # Find unique entity types in data2
    for entity_type, (entities2, _, _) in data2.items():
        if entity_type not in data1:
            unique_to_data2 = entities2
            count_difference = len(entities2)
            differences[entity_type] = ([], sorted(entities2), [], sorted(unique_to_data2), count_difference, {})

    return differences



# Function to display data differences in tabular format
def display_differences(differences):
    table_data = []
    for entity_type, (entities1, entities2, unique_to_data1, unique_to_data2, count_difference, property_differences) in differences.items():
        properties_diff_info = ""
        if isinstance(property_differences, dict):
            for entity, attrs in property_differences.items():
                attr_info = []
                for attr, values in attrs.items():
                    if isinstance(values[0], dict) and isinstance(values[1], dict):
                        values = [json.dumps(value, indent=4) for value in values]
                    attr_info.append(f"{attr}: {values[0]} -> {values[1]}")
                if attr_info:
                    properties_diff_info += f"{entity}:\n    " + "\n    ".join(attr_info) + "\n"
        table_data.append([entity_type, "\n".join(entities1), "\n".join(entities2), "\n".join(unique_to_data1), "\n".join(unique_to_data2), properties_diff_info, count_difference])
    print(tabulate(table_data, headers=["Entity Type", "All JPD1 items", "All JPD2 items", "Unique to JPD 1", "Unique to JPD 2", "Property Differences", "Count Difference"], tablefmt="grid"))


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
