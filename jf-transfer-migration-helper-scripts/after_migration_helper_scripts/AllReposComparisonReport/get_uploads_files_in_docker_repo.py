import os
import subprocess
import argparse
import json
"""
Usage:
python get_uploads_files_in_docker_repo.py frogs-docker-dev-local soleng output

"""

def get_docker_repo_all_uploads_files_count_and_total_size(repo_key, artifactory_server_id, output_dir):
    # Define the AQL query as a string
    # aql_query = f'\'items.find({{"repo": "{repo_key}", "$or": [{{"path": {{"$match": ".jfrog"}}}}, {{"path": {{"$match": "*_uploads"}}}}]}})\''
    aql_query = f'''items.find(
        {{ "repo": "{repo_key}",
             "$or": [
                {{"path": {{"$match": ".jfrog"}}}},
                {{"path": {{"$match": "*_uploads"}}}}
            ]
        }}
    )'''
    # Create a text file to store the AQL query
    # aql_query_file = os.path.join(output_dir,"query_file.txt")
    # with open(aql_query_file, "w") as query_file:
    #     query_file.write(aql_query)
    # Create the command as a list
    # command = [
    #     "jf", "rt", "curl", "-s",
    #     "-XPOST", "/api/search/aql", '-H' , "Content-Type: text/plain",
    #     "-d", f"@{aql_query_file}",
    #     "-L", "--server-id", artifactory_server_id
    # ]

    command = [
        "jf", "rt", "curl", "-s",
        "-XPOST", "/api/search/aql", '-H' , "Content-Type: text/plain",
        "-d", aql_query,
        "-L", "--server-id", artifactory_server_id
    ]

    print("Executing command:", " ".join(command))
    results_file = os.path.join(output_dir, f"{repo_key}.json")
    try:
        with open(results_file, "w") as output:
            # result = subprocess.run(command, capture_output=True, text=True, check=True)
            # print("cURL output:", result.stdout)
            subprocess.run(command, stdout=output, stderr=subprocess.PIPE, text=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Command failed with error:", e.stderr)

    # Parse the JSON data
    data = load_json_file(results_file)
    # Initialize total size to 0 and item count to 0
    total_size = 0
    item_count = 0

    # Iterate through the "results" array and sum up the "size" values
    for result in data["results"]:
        total_size += result["size"]
        item_count += 1

    # Create a tuple with item count and total size
    result_tuple = (item_count, total_size)

    # Print the result tuple
    print(f"Result Tuple for {repo_key}:", result_tuple)
    return result_tuple

# Load the contents of the JSON files
def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)
def main():
    parser = argparse.ArgumentParser(description="Retrieve Docker repository uploads information from Artifactory.")
    parser.add_argument("repo_key", help="The repository key")
    parser.add_argument("artifactory_server_id", help="The Artifactory server ID")
    parser.add_argument("output_dir", help="Output directory for JSON file")

    args = parser.parse_args()

    get_docker_repo_all_uploads_files_count_and_total_size(args.repo_key, args.artifactory_server_id, args.output_dir)

if __name__ == "__main__":
    main()
