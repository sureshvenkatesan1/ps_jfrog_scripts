
# Usage: python delta_items_to_transfer.py --repo nanag-npm

import subprocess
import json
import argparse
import os

# Set JFROG_CLI_LOG_LEVEL environment variable
os.environ['JFROG_CLI_LOG_LEVEL'] = 'DEBUG'

# Define command-line arguments
parser = argparse.ArgumentParser(description='Execute Artifactory AQL query with JFrog CLI')
parser.add_argument('--repo', required=True, help='Artifactory repository name')
args = parser.parse_args()

# AQL query
aql_query = f'''
items.find(
    {{
        "$and":[
            {{"modified":{{"$gte":"2021-01-13T03:02:01Z"}}}},
            {{"repo":"{args.repo}","type":"file"}}
        ]
    }}
)
.include("repo","path","name","type","modified","size")
.sort({{"$asc":["modified"]}})
.offset(0)
.limit(10000)
'''

# Run JFrog CLI command and capture the output
command = [
    "jf",
    "rt",
    "curl",
    "-s",
    "-XPOST",
    "/api/search/aql",
    "-H",
    "Content-Type: text/plain",
    "-d",
    aql_query,
]

try:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    
    # Print the captured stdout and stderr
    print("STDOUT:")
    print(result.stdout)
    
    print("STDERR:")
    print(result.stderr)
    
    print(result.stdout)
    result_json = json.loads(result.stdout)
    for item in result_json['results']:
        path = item['path']
        name = item['name']
        # Process the path and name as needed
        # Example: Printing them to the console
        print(f"{path}/{name}")
except subprocess.CalledProcessError as e:
    print(f"Error: {e.returncode}\n{e.stdout}")
    print(f"STDERR: {e.stderr}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")
