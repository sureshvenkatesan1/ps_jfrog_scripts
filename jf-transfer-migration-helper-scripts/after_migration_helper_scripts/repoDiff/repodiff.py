import os
import argparse
import subprocess
import json
from datetime import datetime


# Fetch artifacts list  from the  repository in the given artifactory.
def fetch_repository_data(artifactory, repo, output_file):
    # Got the storage API params from RTDEV-34024
    command = [
        "jf", "rt", "curl",
        "-X", "GET",
        f"/api/storage/{repo}/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1",
        "-L", "--server-id", artifactory
    ]
    print("Executing command:", " ".join(command))
    try:
        with open(output_file, "w") as output:
            subprocess.run(command, stdout=output, stderr=subprocess.PIPE, text=True, check=True)
        print("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Command failed with error:", e.stderr)

# Load the contents of the JSON files
def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

# Write the unique URIs to a file in the output folder
def write_unique_uris(output_file, unique_uris,total_size):
    file_extension_counts = {}
    with open(output_file, 'w') as uri_file:
        uri_file.write("******************************\n")
        uri_file.write("Files present in the source repository and are missing in the target repository:\n")
        uri_file.write("******************************\n\n")
        for uri in unique_uris:
            uri_file.write(uri + '\n')
            # Generate the count of files sorted by extension
            file_extension = os.path.splitext(uri)[1]
            file_extension_counts[file_extension] = file_extension_counts.get(file_extension, 0) + 1

        # Generate and print the count of files sorted by extension to console
        print("******************************\n")
        print("        FILE STATS\n")
        print("******************************\n\n")
        print("Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository:")
        for extension, count in sorted(file_extension_counts.items()):
            print(f"{extension}: {count}")

        print("Total Unique URIs in source:", len(unique_uris))
        print("Total Size:", total_size)

        # Generate and print the count of files sorted by extension to the output_file
        uri_file.write("******************************\n")
        uri_file.write("        FILE STATS\n")
        uri_file.write("******************************\n\n")
        uri_file.write("Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository:\n")
        uri_file.write(f"Total Unique URIs in source: {len(unique_uris)}\n")
        uri_file.write(f"Total Size: {total_size}\n")

        for extension, count in sorted(file_extension_counts.items()):
            uri_file.write(f"{extension}: {count}\n")


# Write the unique URIs "with repo prefix" to a file in the output folder
def write_unique_uris_with_repo_prefix(output_file, unique_uris, source_rt_repo_prefix):
    with open(output_file, 'w') as uri_file:
        for uri in unique_uris:
            uri_file.write(source_rt_repo_prefix + uri + '\n')

# Filter and write the unique URIs "without unwanted files" , to a file in the output folder
def write_filepaths_nometadata(unique_uris,filepaths_nometadata_file,):
    with  open(filepaths_nometadata_file, "w") as filepaths_nometadata:
        for uri in unique_uris:
            file_name = uri.strip()
            if any(keyword in file_name for keyword in ["maven-metadata.xml", "Packages.bz2", ".gemspec.rz",
                                                       "Packages.gz", "Release", ".json", "Packages", "by-hash", "filelists.xml.gz", "other.xml.gz", "primary.xml.gz", "repomd.xml", "repomd.xml.asc", "repomd.xml.key"]):
                print(f"Excluded: as keyword in {file_name}")
            else:
                print(f"Writing: {file_name}")
                filepaths_nometadata.write(file_name + '\n')


#  Get the download stats for every artifact uri in the unique_uris list from the source artifactory. But this takes
#  a long time - 1+ hour for 13K artifacts. So use the write_artifact_stats_from_source_data function instead.
def write_artifact_stats_sort_desc(artifactory, repo, unique_uris, output_file):
    artifact_info = []
    total_commands = len(unique_uris)

    for i, uri in enumerate(unique_uris, start=1):
        full_uri = f"/api/storage/{repo}/{uri.lstrip('/')}?stats"
        command = [
            "jf", "rt", "curl",
            "-X", "GET",
            full_uri,
            "-L", "--server-id", artifactory
        ]

        print(f"Executing command {i}/{total_commands}: {' '.join(command)}")

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            print("Command executed successfully.")

            # Parse the JSON response
            response_data = json.loads(result.stdout)

            # Extract relevant information
            last_downloaded = response_data["lastDownloaded"]
            timestamp_utc = datetime.utcfromtimestamp(last_downloaded / 1000.0).strftime('%Y-%m-%d %H:%M:%S UTC')

            # Append to the list
            artifact_info.append((uri, last_downloaded, timestamp_utc))
        except subprocess.CalledProcessError as e:
            print("Command failed with error:", e.stderr)

    # Sort the artifact_info list in descending order of lastDownloaded
    sorted_artifact_info = sorted(artifact_info, key=lambda x: x[1], reverse=True)

    # Write the headers to the output file
    with open(output_file, 'w') as out_file:
        out_file.write("lastDownloaded\tTimestamp (Epoch Millis)\tURI\n")

        # Write the values for each artifact in a single line
        for uri, last_downloaded, timestamp_utc in sorted_artifact_info:
            out_file.write(f"{last_downloaded}\t{timestamp_utc}\t{uri}\n")

#  Get the download stats for every artifact uri in the unique_uris list from the mdTimestamps.artifactory.stats in the
#  source_data json itself.
# If the artifact was never downloaded use a default timestamp of "Jan 1 , 1900"  UTC .
def write_artifact_stats_from_source_data(source_data, unique_uris, output_file):
    artifact_info = []

    for uri in unique_uris:
        # Find the corresponding entry in source_data by matching the "uri"
        matching_entry = next((item for item in source_data['files'] if item['uri'] == uri), None)

        if matching_entry:
            # Extract the "artifactory.stats" timestamp if available, otherwise use a default timestamp of "Jan 1 , 1900"
            # timestamp_utc = response_data["mdTimestamps"].get("artifactory.stats") or response_data["lastModified"]
            timestamp_utc = matching_entry["mdTimestamps"].get("artifactory.stats", "1900-01-01T00:00:00.000Z")

            # Append to the list
            artifact_info.append((uri, timestamp_utc))
        else:
            # If no matching entry is found, use a default timestamp
            artifact_info.append((uri, "1900-01-01T00:00:00.000Z"))

    # Sort the artifact_info list in descending order of timestamp_utc
    sorted_artifact_info = sorted(artifact_info, key=lambda x: x[1], reverse=True)

    # Write the headers to the output file
    with open(output_file, 'w') as out_file:
        out_file.write("Download Timestamp\tURI\n")

        # Write the values for each artifact in a single line
        for uri, timestamp_utc in sorted_artifact_info:
            out_file.write(f"{timestamp_utc}\t{uri}\n")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Check if repo in target Artifactory has all the artifacts from "
                                                 "repo in source Artifactory.")
    parser.add_argument("--source-artifactory", required=True, help="Source Artifactory ID")
    parser.add_argument("--target-artifactory", required=True, help="Target Artifactory ID")
    parser.add_argument("--source-repo", required=True, help="Source repository name")
    parser.add_argument("--target-repo", required=True, help="Target repository name")
    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    output_dir = "test/output"
    os.makedirs(output_dir, exist_ok=True)

    # Fetch data from repositories
    source_log_file = os.path.join(output_dir, "source.log")
    fetch_repository_data(args.source_artifactory, args.source_repo, source_log_file)
    #
    target_log_file = os.path.join(output_dir, "target.log")
    fetch_repository_data(args.target_artifactory, args.target_repo, target_log_file)

    # Load the contents of the JSON files
    source_data = load_json_file(source_log_file)
    target_data = load_json_file(target_log_file)

    # Extract the "uri" values from both source and target files
    source_uris = {item['uri'] for item in source_data['files']}
    target_uris = {item['uri'] for item in target_data['files']}

    # Find the unique URIs and calculate the total size
    unique_uris = source_uris - target_uris
    total_size = sum(item['size'] for item in source_data['files'] if item['uri'] in unique_uris)

    # Write the unique URIs to a file in the output folder
    unique_uris_file = os.path.join(output_dir, "cleanpaths.txt")
    write_unique_uris(unique_uris_file, unique_uris,total_size)

    # Write the unique URIs "with repo prefix" to a file in the output folder
    prefix = f"{args.source_artifactory}/artifactory/{args.source_repo}"
    filepaths_uri_file=os.path.join(output_dir, "filepaths_uri.txt")
    write_unique_uris_with_repo_prefix(filepaths_uri_file,unique_uris,prefix)

    # fetch artifact statistics, extract the relevant information, and sort the lines in descending order of the lastDownloaded timestamp
    # to a file in the output folder
    filepaths_uri_stats_file=os.path.join(output_dir, "filepaths_uri_lastDownloaded_desc.txt")
    # write_artifact_stats_sort_desc(args.source_artifactory, args.source_repo, unique_uris, filepaths_uri_stats_file)
    write_artifact_stats_from_source_data( source_data, unique_uris,
                                        filepaths_uri_stats_file)

    # Filter and write the unique URIs "without unwanted files" , to a file in the output folder
    filepaths_nometadata_file = os.path.join(output_dir, "filepaths_nometadatafiles.txt")
    write_filepaths_nometadata(unique_uris,filepaths_nometadata_file)



if __name__ == "__main__":
    main()
