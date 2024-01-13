# Bash Script for Patching Properties of Artifacts in Target Artifactory

This Bash script is designed to patch the properties of artifacts in a target Artifactory repository based on the properties of corresponding artifacts in a source Artifactory repository.

## Usage

```bash
./patch_props_for_artifacts_in_target.sh <source-artifactory> <source-repo> <target-repo> <target-artifactory> [root-folder]
```

- <source-artifactory>: The source Artifactory server.
- <source-repo>: The source repository within the source Artifactory server.
- <target-repo>: The target repository within the target Artifactory server.
- <target-artifactory>: The target Artifactory server.
- [root-folder]: (Optional) The root folder in the source repository to start processing. If not provided, the script will process artifacts in the root of the source repository.

## Script Overview
The script performs the following steps:

- Check if the required parameters are provided.
- Generate a command to list artifacts in the source repository and their properties.
- Process each artifact:
    - Check if the artifact has properties in the source repository.
    - If properties exist, patch the properties for the corresponding artifact in the target repository.
- List all folders in the source repository.
- Process artifacts in each folder recursively, updating properties in the target repository.
- Limit parallel execution of commands (optional, currently commented out).
Please refer to the script code for detailed comments and explanations of each step.

## Notes
The script uses jq for JSON parsing and sed for string manipulation.
Failed commands are logged to `failed_commands.txt``.
Successful and all commands are logged to `all_commands.txt``.


This script generates tons of following commands to PATCH the properties of each artifact:
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

I prefer the above command insted of the followig whcih uses the bash xargs approach to run 16 such commands at a time using [runcommand_w_xargs_and_log_outcome.sh](../runcommand_in_parallel_as_bash_jobs/runcommand_w_xargs_and_log_outcome.sh):
```
./patch_props_for_artifacts_in_target.sh usvartifactory5 liquid jfrogio liquid  test | tr '\n' '\0' | xargs -0 -P 16 -I {} ./runcommand_log_outcome.sh '{}' properties_patch_failed.txt
```
