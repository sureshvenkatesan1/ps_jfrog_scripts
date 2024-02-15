
"""
python generate_script_to_fix_repoDiff.py "/Users/sureshv/myCode/bitbucket-ps/ps_jfrog_scripts/jf-transfer-migration-helper-scripts/before-migration-helper
-scripts/transfer-artifacts-in-sub_folders_in_parallel/migrate_n_subfolders_in_parallel.sh" \
filepaths_nometadatafiles.txt \

<source-artifactory> <source-repo> <target-artifactory> <target-repo> \
<transfer yes/no> \
[migrateFolderRecursively yes/no] [semicolon separated exclude_folders] [parallel_count]
"""

# Now, process the non-empty URIs
# scripts = []
# for uri in uris:
#     script_args = [source_artifactory, source_repo, target_artifactory, target_repo, transfer]
#     if migrate_recursively is not None:
#         script_args.append(migrate_recursively)
#     if exclude_folders is not None:
#         script_args.append(exclude_folders)
#     if parallel_count is not None:
#         script_args.append(parallel_count)
#     script_args.append(uri)
#     script = f'{script_path} {" ".join(map(str, script_args))}'
#     scripts.append(script)
#
# # Write the generated scripts to the output file
# if outfile is None:
#     outfile = "output_script.bat"
#
# with open(outfile, "w") as outfile:
#     for script in scripts:
#         outfile.write(script + "\n")

import argparse
import subprocess
import os
import json

def execute_artifact_migration(workdir, source_repo, line, source_artifactory, target_repo, target_artifactory, escaped_modified_json):
    # Save the current directory to a variable
    current_dir = os.getcwd()

    os.makedirs(workdir, exist_ok=True)
    os.chdir(workdir)
    print(f"In execute_artifact_migration escaped_modified_json is: {escaped_modified_json}")
    # Check if the length of the trimmed $escaped_modified_json is greater than 1 , i.e artifact has a property
    if escaped_modified_json and 'props' in escaped_modified_json and len(escaped_modified_json['props']) >= 1:
        # Serialize the dictionary to a JSON string
        json_data_str = json.dumps(escaped_modified_json)

        # Construct the curl command with the JSON data string
        curl_command = f'jf rt curl -k -sL -XPATCH -H "Content-Type: application/json" "/api/metadata/{target_repo}/{line}?atomicProperties=1" --server-id {target_artifactory} -d \'{json_data_str}\''

        # Add the curl command to the list of commands
        commands = [
            f"jf rt dl {source_repo}/{line} . --threads=8 --server-id {source_artifactory}",
            f"jf rt u {line} {target_repo}/{line} --threads=8 --server-id {target_artifactory}",
            curl_command,
            f"rm -rf {line}"
            ]
    else:
        print(f"Not uploading properties: {escaped_modified_json}")
        commands = [
            f"jf rt dl {source_repo}/{line} . --threads=8 --server-id {source_artifactory}",
            f"jf rt u {line} {target_repo}/{line} --threads=8 --server-id {target_artifactory}",
            f"rm -rf {line}"
        ]


    # Execute the commands
    any_command_failed = False
    for command in commands:
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            any_command_failed = True
            with open(os.path.join(current_dir, "failed_commands_file.txt"), "a") as f:
                f.write(f"Command failed: {command} , for: {source_repo}/{line}\n")

    # If all commands succeeded, log the success message once for each artifact
    if not any_command_failed:
        with open(os.path.join(current_dir, "successful_commands_file.txt"), "a") as f:
            f.write(f"All commands succeeded for: {source_repo}/{line}\n")

    os.chdir(current_dir)  # Return to the saved directory i.e "$OLDPWD"

def get_escaped_modified_json(source_repo, line, source_artifactory):
    # Construct the command to run
    command = [
        "jf", "rt", "curl", "-s", "-k", "-XGET",
        f"/api/storage/{source_repo}/{line}?properties",
        "--server-id", source_artifactory
    ]

    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Result is: {result}")

        # Parse the JSON output
        prop_output = json.loads(result.stdout)
        json_data = prop_output.get("properties")
        print(f"json_data is: {json_data}")
        escaped_modified_json = {"props": json_data}
        print(f"escaped_modified_json is: {escaped_modified_json}")
        return escaped_modified_json
        # # Check if the artifact has properties
        # if 'errors' in prop_output and prop_output['errors'][0]['status'] != 404:
        #     json_data = prop_output.get("properties")
        #     if json_data:
        #         # Construct the modified JSON data
        #         escaped_modified_json = {"props": json_data}
        #         return escaped_modified_json
    except subprocess.CalledProcessError as e:
        # Handle command execution errors
        print(f"Error executing command: {e}")
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"Error parsing JSON output: {e}")

    return None  # Return None if no properties or error occurred
def generate_script(input_file, source_artifactory, source_repo, target_artifactory, target_repo,
                    transfer, migrate_recursively=None, exclude_folders=None, parallel_count=None, outfile=None):
    # Define flags to indicate which section we're currently in
    in_source_files_section = False
    in_file_stats_section = False

    # Initialize the list to store non-empty URIs
    uris = []

    with open(input_file, 'r') as file:
        # Iterate through each line in the file
        for line in file:
            # Strip leading/trailing whitespace
            line = line.strip()

            # Check if we're in the source files section
            if line.startswith("Files present in the source repository and are missing in the target repository:"):
                in_source_files_section = True
                in_file_stats_section = False
                continue
            # Check if we're in the file stats section
            elif line.startswith("FILE STATS"):
                in_source_files_section = False
                in_file_stats_section = True
                continue

            # If we're in the source files section and the line is not empty, append it to the uris list
            if in_source_files_section and line and "******************************" not in line:
                escaped_modified_json = get_escaped_modified_json(source_repo, line, source_artifactory)
                if escaped_modified_json:
                    print("Escaped modified JSON xxxxx:", escaped_modified_json)
                else:
                    print("No properties found or error occurred.")
                execute_artifact_migration("workdir", source_repo, line, source_artifactory, target_repo,
                                    target_artifactory, escaped_modified_json)


def main():
    parser = argparse.ArgumentParser(description='Generate migration scripts for each file.')
    # parser.add_argument('script_path', type=str, help='Path to the script to run.')
    parser.add_argument('input_file', type=str, help='Path to the input file containing file paths.')

    parser.add_argument('source_artifactory', type=str, help='Source Artifactory URL.')
    parser.add_argument('source_repo', type=str, help='Source repository name.')
    parser.add_argument('target_artifactory', type=str, help='Target Artifactory URL.')
    parser.add_argument('target_repo', type=str, help='Target repository name.')
    parser.add_argument('transfer', type=str, help='Transfer yes/no.')
    parser.add_argument('--migrate_recursively', type=str, help='MigrateFolderRecursively yes/no.')
    parser.add_argument('--exclude_folders', type=str, help='Semicolon-separated exclude folders.')
    parser.add_argument('--parallel_count', type=int, help='Parallel count.')
    parser.add_argument('--outfile', type=str, help='Output file to write the generated scripts.')
    args = parser.parse_args()

    # generate_script(args.script_path, args.input_file, args.source_artifactory, args.source_repo,
    #                 args.target_artifactory, args.target_repo, args.transfer, args.migrate_recursively,
    #                 args.exclude_folders, args.parallel_count, args.outfile)
    generate_script(args.input_file, args.source_artifactory, args.source_repo,
                    args.target_artifactory, args.target_repo, args.transfer, args.migrate_recursively,
                    args.exclude_folders, args.parallel_count, args.outfile)

if __name__ == "__main__":
    main()


