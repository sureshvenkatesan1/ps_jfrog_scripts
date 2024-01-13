#! /bin/bash
# this uses same logic as in https://github.com/jfrog/artifactory-scripts/blob/master/replicationDiff/replicationDiff.sh
set -x
### Exit the script on any failures
## define variables
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

jf rt curl -X GET "/api/storage/$SOURCEREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L --server-id="${SOURCEART}"> "${output_dir}/source.log"

jf rt curl -X GET "/api/storage/$TARGETREPO/?list&deep=1&listFolders=0&mdTimestamps=1&statsTimestamps=1&includeRootPath=1" -L --server-id="${TARGETART}"> "${output_dir}/target.log"

diff --new-line-format="" --unchanged-line-format=""  "${output_dir}/source.log" "${output_dir}/target.log" > "${output_dir}/diff_output.txt"
sed -n '/uri/p' "${output_dir}/diff_output.txt" | sed 's/[<>,]//g' | sed '/https/d' | sed '/http/d' | sed  's/ //g' | sed 's/[",]//g' | sed 's/uri://g' > "${output_dir}/cleanpaths.txt"
prefix=$SOURCEART/$SOURCEREPO
awk -v prefix="$prefix" '{print prefix $0}' "${output_dir}/cleanpaths.txt" > "${output_dir}/filepaths_uri.txt"

echo
echo
echo "Here is the count of files sorted according to the file extension that are present in the source repository and are missing in the target repository. Please note that if there are SHA files in these repositories which will have no extension, then the entire URL will be seen in the output. The SHA files will be seen for docker repositories whose layers are named as per their SHA value. "
echo
grep -E ".*\.[a-zA-Z0-9]*$" "${output_dir}/filepaths_uri.txt" | sed -e 's/.*\(\.[a-zA-Z0-9]*\)$/\1/' "${output_dir}/filepaths_uri.txt" | sort | uniq -c | sort -n
sed '/maven-metadata.xml/d' "${output_dir}/filepaths_uri.txt" |  sed '/Packages.bz2/d' | sed '/.*gemspec.rz$/d' |  sed '/Packages.gz/d' | sed '/Release/d' | sed '/.*json$/d' | sed '/Packages/d' | sed '/by-hash/d' | sed '/filelists.xml.gz/d' | sed '/other.xml.gz/d' | sed '/primary.xml.gz/d' | sed '/repomd.xml/d' | sed '/repomd.xml.asc/d' | sed '/repomd.xml.key/d' > "${output_dir}/filepaths_nometadatafiles.txt"
#rm source.log target.log diff_output.txt cleanpaths.txt
echo "done"