#!/bin/bash
set -e  # Exit on any failures

if [ $# -lt 4 ]; then
    echo "Usage: $0 <source> <target> <source_repo> <target_repo>"
    exit 1
fi

SOURCEART="${1}"
TARGETART="${2}"
SOURCEREPO="${3}"
TARGETREPO="${4}"

# Define the output directory
output_dir="output"
mkdir -p "${output_dir}"

function fetch_repository_data() {
    local ARTIFACTORY="$1"
    local REPO="$2"
    local OUTPUT_FILE="$3"

    jf rt curl -X GET "/api/storage/$REPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L --server-id="$ARTIFACTORY" > "$OUTPUT_FILE"
}

function clean_and_format_paths() {
    local INPUT_FILE="$1"
    local OUTPUT_FILE="$2"

    sed -n '/uri/p' "$INPUT_FILE" | sed 's/[<>,]//g' | sed '/https\|http/d' | sed 's/ //g' | sed 's/[",]//g' | sed 's/uri://g' > "$OUTPUT_FILE"
}

function add_prefix_to_paths() {
    local PREFIX="$1"
    local INPUT_FILE="$2"
    local OUTPUT_FILE="$3"

    awk -v prefix="$PREFIX" '{print prefix $0}' "$INPUT_FILE" > "$OUTPUT_FILE"
}

function display_file_extension_count() {
    local INPUT_FILE="$1"

    echo
    echo
    echo "Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository. Please note that if there are SHA files in these repositories which will have no extension, then the entire URL will be seen in the output. The SHA files will be seen for docker repositories whose layers are named as per their SHA value. "
    echo
    grep -E ".*\.[a-zA-Z0-9]*$" "$INPUT_FILE" | sed -e 's/.*\(\.[a-zA-Z0-9]*\)$/\1/' | sort | uniq -c | sort -n
}

function filter_unwanted_paths() {
    local INPUT_FILE="$1"
    local OUTPUT_FILE="$2"

    sed '/maven-metadata.xml/d; /Packages.bz2/d; /.*gemspec.rz$/d; /Packages.gz/d; /Release/d; /.*json$/d; /Packages/d; /by-hash/d; /filelists.xml.gz/d; /other.xml.gz/d; /primary.xml.gz/d; /repomd.xml/d; /repomd.xml.asc/d; /repomd.xml.key/d' "$INPUT_FILE" > "$OUTPUT_FILE"
}

# Fetch data from repositories
fetch_repository_data "$SOURCEART" "$SOURCEREPO" "${output_dir}/source.log"
fetch_repository_data "$TARGETART" "$TARGETREPO" "${output_dir}/target.log"

# Compare and clean paths

jq -s 'map(.files[] | {uri})' "${output_dir}/source.log" > "${output_dir}/source_files.json"
jq -s 'map(.files[] | {uri})' "${output_dir}/target.log" > "${output_dir}/target_files.json"

jq -s '[ .[0][] | .uri ] as $doc1_fields | [ .[1][] | .uri ] as $doc2_fields | ($doc1_fields - $doc2_fields) | join("\n")' "${output_dir}/source_files.json" "${output_dir}/target_files.json" | jq -r '@text' >  "${output_dir}/cleanpaths.txt"


# Add prefix to paths
prefix="$SOURCEART/$SOURCEREPO"
add_prefix_to_paths "$prefix" "${output_dir}/cleanpaths.txt" "${output_dir}/filepaths_uri.txt"

# Display file extension count
display_file_extension_count "${output_dir}/filepaths_uri.txt"

# Filter unwanted paths
filter_unwanted_paths "${output_dir}/filepaths_uri.txt" "${output_dir}/filepaths_nometadatafiles.txt"

# Clean up
#rm "${output_dir}/source.log" "${output_dir}/target.log" "${output_dir}/diff_output.txt" "${output_dir}/cleanpaths.txt"
