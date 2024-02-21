# Bash Script for Patching Properties of Artifacts in Target Artifactory

This Bash script is designed to patch the properties of artifacts in a target Artifactory repository based on the properties of corresponding artifacts in a source Artifactory repository ( if they are different)

### Prerequisites

- **bash**: Ensure you have Bash installed on your system.
- **jq**: This script uses `jq` to parse JSON responses. Make sure `jq` is installed and accessible in your environment.
- **JFrog CLI**: The script relies on `jf` commands for interacting with Artifactory repositories. Make sure you have JFrog CLI installed and configured.

## Usage
To generate the jq commands:
```
bash ./patch_props_for_artifacts_in_target.sh <source-artifactory> <source-repo> <target-artifactory> <target-repo>  [root-folder]
```
To generate and execute the jq commands using [runcommand_in_parallel_and_log_outcome.sh](../runcommand_in_parallel_as_bash_jobs/runcommand_in_parallel_and_log_outcome.sh):
```
bash ./patch_props_for_artifacts_in_target.sh <source-artifactory> <source-repo> <target-artifactory> <target-repo>  [root-folder] | bash ./runcommand_in_parallel_and_log_outcome.sh properties_patch_failed.txt 16
```

- `source-artifactory`: The source Artifactory server.
- `source-repo`: The source repository within the source Artifactory server.
- `target-artifactory`: The target Artifactory server.
- `target-repo`: The target repository within the target Artifactory server.
- `[root-folder]`: (Optional) The root folder in the source repository to start processing. If not provided, the script will process artifacts from the root of the source repository.

## Script Overview
The script performs the following steps:

- The script retrieves artifacts from the target repository and their properties using JFrog CLI.
- It compares the properties of these artifacts with their counterparts in the source repository.
- If differences are found, it patches the properties of the target artifacts to match those of the source artifacts.
- The script logs failed commands to `failed_commands.txt`.

## Notes
The script uses jq for JSON parsing and sed for string manipulation.
Failed commands are logged to `failed_commands.txt``.



This script generates tons of following commands to PATCH the properties of each artifact with the property differs 
in source and target artifactory instances:
```
" jf rt curl -k -sL -XPATCH -H \"Content-Type: application/json\" \"/api/metadata/$target_repo/$line?atomicProperties=1\" --server-id $target_artifactory -d \"$escaped_modified_json\" "
```

You can run these generated commands in parallel without using the unix `parallel` utility.

For example to run 16 such commands at a time run  using
[runcommand_in_parallel_and_log_outcome.sh](../runcommand_in_parallel_as_bash_jobs/runcommand_in_parallel_and_log_outcome.sh)
:
```
./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test | ./runcommand_in_parallel_and_log_outcome.sh properties_patch_failed.txt 16

```

Other way to run this:
```
bash ./patch_props_for_artifacts_already_in_target/patch_props_for_artifacts_in_target.sh \
soleng app1-docker-dev-local proservicesone test-docker

```
Output will be similar to the following:
```
jf rt curl -k -sL -XPATCH -H "Content-Type: application/json" "/api/metadata/test-docker/hello-world/5.7/manifest.json?atomicProperties=1" --server-id proservicesone -d "{\"props\": {\"artifactory.content-type\":[\"application/vnd.docker.distribution.manifest.v2+json\"],\"docker.manifest\":[\"5.7\"],\"docker.manifest.digest\":[\"sha256:01433e86a06b752f228e3c17394169a5e21a0995f153268a9b36a16d4f2b2184\"],\"docker.manifest.type\":[\"application/vnd.docker.distribution.manifest.v2+json\"],\"docker.repoName\":[\"hello-world\"],\"sha256\":[\"01433e86a06b752f228e3c17394169a5e21a0995f153268a9b36a16d4f2b2184\"]}}"
Properties are identical, skipping patching for artifact: hello-world/5.7/sha256__18e5af7904737ba5ef7fbbd7d59de5ebe6c4437907bd7fc436bf9b3ef3149ea9
Properties are identical, skipping patching for artifact: hello-world/5.7/sha256__93288797bd35d114f2d788e5abf4fae518a5bd299647daf4ede47acc029d66c5
```

You can even run it for a subfolder as follows:
```
bash ./patch_props_for_artifacts_already_in_target/patch_props_for_artifacts_in_target.sh \
soleng app1-docker-dev-local proservicesone test-docker hello-world/5.7
```
Then these "jf" commands in the output can be executed as:
```
bash /tmp/ps_jfrog_scripts/jf-transfer-migration-helper-scripts/patch_props_for_artifacts_already_in_target/patch_props_for_artifacts_in_target.sh \
soleng app1-docker-dev-local proservicesone test-docker hello-world/5.7 | bash /tmp/ps_jfrog_scripts/jf-transfer-migration-helper-scripts/runcommand_in_parallel_as_bash_jobs/runcommand_in_parallel_and_log_outcome.sh properties_patch_failed.txt 16
```
In the output you should see output similar to:
```
Command successful: jf rt curl -k -sL -XPATCH -H "Content-Type: application/json" "/api/metadata/test-docker/hello-world/5.7/manifest.json?atomicProperties=1" --server-id proservicesone -d "{\"props\": {\"artifactory.content-type\":[\"application/vnd.docker.distribution.manifest.v2+json\"],\"docker.manifest\":[\"5.7\"],\"docker.manifest.digest\":[\"sha256:01433e86a06b752f228e3c17394169a5e21a0995f153268a9b36a16d4f2b2184\"],\"docker.manifest.type\":[\"application/vnd.docker.distribution.manifest.v2+json\"],\"docker.repoName\":[\"hello-world\"],\"sha256\":[\"01433e86a06b752f228e3c17394169a5e21a0995f153268a9b36a16d4f2b2184\"]}}"
Command successful: Properties are identical, skipping patching for artifact: hello-world/5.7/sha256__18e5af7904737ba5ef7fbbd7d59de5ebe6c4437907bd7fc436bf9b3ef3149ea9
Command successful: Properties are identical, skipping patching for artifact: hello-world/5.7/sha256__93288797bd35d114f2d788e5abf4fae518a5bd299647daf4ede47acc029d66c5
```
---

I prefer the above command instead of the followig which uses the bash xargs approach to run 16 such commands at a 
time using [runcommand_w_xargs_and_log_outcome.sh](../runcommand_in_parallel_as_bash_jobs/runcommand_w_xargs_and_log_outcome.sh):
```
./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test | tr '\n' '\0' | xargs -0 -P 16 -I {} ./runcommand_log_outcome.sh '{}' properties_patch_failed.txt
```
