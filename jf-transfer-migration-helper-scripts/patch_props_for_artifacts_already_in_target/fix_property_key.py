# To run:
#
# Create a virtual environment using Python 3.12+ and populate it:
#
# Linux:
#   python -m venv jfrog
#   source jfrog/bin/activate
#   pip install requests
#
# Windows:
#   python -m venv jfrog
#   jfrog/Scripts/activate
#   pip install requests
#
# Then run:
#
# python fix_property_key.py --jpd-url url --access-token token --input file [--commit]
#
# The `--commit` flag causes changes to actually be commited. If not specified, it's a dry run.

# Purpose: To workaround 
# RTDEV-30673 Push Replication turns "_" to "__" when found in property name. Sof fix these property keys back from  "__" to "_"
# Any new such property keys and its replacement can be added to the REPLACEMENTS dictionary.

import argparse
import logging
import sys
import json
from pathlib import Path

import requests

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

REPLACEMENTS = {
    "git__commit": "git_commit",
    "git__branch": "git_branch"
}


def get_affected_artifacts(input_file: Path) -> list[str]:
    """
    Given an input file, reads a list of artifacts.
    Currently, this function expects the file to contain a JSON, which is the result of an AQL query
    such as:

    curl -u <user>:<password> -X POST "https://example.jfrog.io/artifactory/api/search/aql" \
        -H "Content-Type: text/plain" \
        -d 'items.find({
            "repo": {"$eq": "bsc-central-ci"},
            "property.key": {"$eq": "git__branch"},
            "property.key": {"$eq": "git__commit"}
        })'

    :param input_file: path to file
    :return: list of strings, each one is the full path to an artifact

    Other aql variations to search for the artifacts with property keys in REPLACEMENTS :
    
    jf rt curl "/api/search/aql" \
    -H "Content-Type: text/plain" \
    --server-id=psazuse \
    -d 'items.find({
    "repo": {"$eq": "request-wip-generic-local"},
    "$or":
     [
        {"property.key": {"$eq": "git__branch"}},
        {"property.key": {"$eq": "git__commit"}}
    ]
    })' 


    """
    with input_file.open("r") as f:
        contents = json.load(f)
    return [f"{entry['repo']}/{entry['path']}/{entry['name']}" for entry in contents["results"]]


def process_property(name: str) -> str:
    """
    Given the name of a propery, returns an updated property name.
    :param name: property's name
    :return: A potentially-updated property name
    """
    return REPLACEMENTS.get(name, name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jpd-url", required=True)
    parser.add_argument("--access-token", required=True)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--commit", action="store_true", default=False)
    args = parser.parse_args()

    affected_artifacts: list[str] = get_affected_artifacts(args.input)

    for artifact_repo_path in affected_artifacts:
        logger.info("Handling item: %s", artifact_repo_path)

        response = requests.get(
                f"{args.jpd_url}/artifactory/api/storage/{artifact_repo_path}?properties",
                headers={
                    "Authorization": f"Bearer {args.access_token}"
                }, verify=False)
        response.raise_for_status()
        properties = response.json()["properties"]
        updated_properties = {}
        updated = False
        for name, value in properties.items():
            updated_name = process_property(name)
            updated_properties[updated_name] = value
            # If property's name has been updated, we'll need to PATCH at the end.
            if updated_name != name:
                logger.info("Will rename: %s -> %s", name, updated_name)
                updated_properties[name] = None
                updated = True

        if updated:
            if args.commit:
                logger.info("Updating artifact: %s", artifact_repo_path)
                response = requests.patch(
                        f"{args.jpd_url}/artifactory/api/metadata/{artifact_repo_path}",
                        params={
                            "recursiveProperties": "0"
                        },
                        headers={
                            "Authorization": f"Bearer {args.access_token}"
                        },
                        json={
                            "props": updated_properties
                        },
                        verify=False
                )
                response.raise_for_status()
            else:
                logger.info("(Dry run, not updating artifact: %s)", artifact_repo_path)


if __name__ == "__main__":
    main()
