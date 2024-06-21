import argparse
import re
"""
The input file contains:
output/BigData-Datalake/cleanpaths.txt:Total Unique URIs in source: 1
output/Xlr8r-debian-local/cleanpaths.txt:Total Unique URIs in source: 2
output/aa-debian-local/cleanpaths.txt:Total Unique URIs in source: 35

The output from:
python generate_repo_list_for_cleanpaths_to_process.py --input-file input.txt

is:
BigData-Datalake;Xlr8r-debian-local;aa-debian-local

"""
def main(input_file_path):
    # Initialize a list to hold repository names
    repo_names = []

    # Read the input file
    with open(input_file_path, 'r') as file:
        for line in file:
            # Use a regular expression to extract the repository name from the line
            match = re.match(r'output/([^/]+)/cleanpaths.txt', line)
            if match:
                repo_names.append(match.group(1))

    # Join the repository names with a semicolon
    result = ";".join(repo_names)

    # Print the result
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a semicolon-separated list of repository names from an input file.')
    parser.add_argument('--input-file', type=str, required=True, help='Path to the input file.')

    args = parser.parse_args()
    main(args.input_file)
