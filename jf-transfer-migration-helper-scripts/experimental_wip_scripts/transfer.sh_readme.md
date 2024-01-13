The `runtask()` method in the https://git.jfrog.info/projects/PROFS/repos/ps_jfrog_scripts/browse/transfer-artifacts/transfer.sh Bash script is a function that performs a series of actions related to transferring or viewing files between two Artifactory servers (source and target) based on the parameters provided to the script.

Here's a breakdown of what the `runtask()` function does step by step:

1. It uses the `jf rt curl` command to make an HTTP POST request to the Artifactory API on the source server (`$SOURCE_ID`) to search for items in a specific repository (`$1`). The search criteria are specified using AQL (Artifactory Query Language). The results of this search include information about files in the repository, such as their paths, names, and SHA256 checksums.

2. It processes the JSON response from the source server using `jq`. Specifically, it extracts the `path`, `name`, and `sha256` fields for each item in the result and formats this information as a string containing the path, name, and SHA256 checksum, separated by a comma.

3. It removes any leading "./" from the paths using `sed` and redirects the formatted output to a file named "a."

4. It repeats the same process for the target server (`$TARGET_ID`) and stores the results in a file named "b."

5. It uses the `join` command to find the differences between the contents of files "a" and "b," effectively identifying files that exist in the source but not in the target.

6. It further processes the results to format them correctly, removing the SHA256 checksum, and stores the final list of files in a file named "c."

7. Depending on the value of the `TRANSFERONLY` variable:
   - If it is set to "no," the script prints the differences between source and target repositories (files that exist only in the source).
   - If it is set to "yes," the script iterates through the lines in the "c" file and constructs a series of `jf rt` commands for downloading (`jf rt dl`) from the source server, uploading (`jf rt u`) to the target server, and then removing the local file (`rm -f`). These commands are echoed but commented out, so they won't be executed directly.

8. The function checks the value of `TRANSFERONLY` and provides an error message if it is neither "yes" nor "no."

9. Finally, it cleans up temporary files "a," "b," and "c" by removing them.

The function is called within a loop that iterates over repositories on the source server, invoking `runtask` for each repository. The purpose of the script is to identify and potentially transfer files from the source Artifactory server to the target Artifactory server based on the specified criteria. It can be used for synchronization or backup purposes.
=================
Improve on https://git.jfrog.info/projects/PROFS/repos/ps_jfrog_scripts/browse/transfer-artifacts/transfer.sh
cd /Users/sureshv/Documents/From_Customer/Bose/tests/aql

jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $SOURCE_ID --data "items.find({\"repo\": \"$REPO\",\"type\": \"file\",\"path\" : \".conan\"}).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | sed  's/\.\///'

# for path sureshv-liquid-test/_/autoconf/
SOURCE_ID=bosesaas
REPO=sureshv-liquid-test
jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $SOURCE_ID --data "items.find(   {
      \"repo\":  {\"\$eq\":\"$REPO\"},
      \"path\": {\"\$match\": \"_/autoconf/*\"},
      \"type\": \"file\"

    }).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))' | wc -l

jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id bosesh --data "items.find({\"repo\": {\"\$eq\":\"sureshv-liquid-test\"}, \"path\": {\"\$match\": \"_/autoconf/*\"}, \"type\": \"file\"}).include(\"repo\",\"path\",\"name\",\"sha256\")"

jf rt curl -s -XPOST -H 'Content-Type: text/plain' /api/search/aql --server-id bosesh --data 'items.find(   {
      "repo":  {"$eq":"sureshv-liquid-test"},
      "path": {"$match": "_/autoconf/*"},
      "type": "file"

    }).include("repo","path","name","sha256")'


jf rt curl  -k -XGET "/api/storage/$REPO?list&deep=1&depth=1&listFiles=1" --server-id $SOURCE_ID
=========
SOURCE_ID=bosesh
REPO=sureshv-liquid-generic
jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id $SOURCE_ID --data "items.find(   {
      \"repo\":  {\"\$eq\":\"$REPO\"},
      \"path\": {\"\$match\": \"test/*\"},
      \"type\": \"file\"

    }).include(\"repo\",\"path\",\"name\",\"sha256\")" | jq '.results[]|(.path +"/"+ .name+","+(.sha256|tostring))'

jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id bosesh --data 'items.find({"repo": {"$eq":"sureshv-liquid-generic"}, "path": {"$match": "test/CastleFrontDoorUtility/*"}, "type": "file"}).include("repo","path","name","sha256")'

jf rt curl -s -XPOST -H 'Content-Type: text/plain' api/search/aql --server-id bosesh --data 'items.find({"repo": {"$eq":"sureshv-liquid-generic"}, "path": {"$match": "test/*"}, "type": "file"}).include("repo","path","name","sha256")'