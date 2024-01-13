# Artifactory Subfolder Migration

This script is designed to generate a bash script to run screen commands for migrating subfolders  from a source repository to a target repository. It does this by first retrieving a list of subfolders of a given folder from the source repository using the Artifactory REST API, and then generating screen commands to migrate each subfolder in parallel.

## Prerequisites
Before using this script, ensure you have the following prerequisites in place:

Python 3.x installed on your system.

jf CLI: You need the jf CLI tool for interacting with Artifactory. Make sure it's installed and configured correctly.

## Usage

You can use this script by providing the following command-line arguments:

```bash
python generate_screen_commands_for_subfolders.py \
    --source_jpd SOURCE_JPD \
    --source_repo SOURCE_REPO \
    --target_jpd TARGET_JPD \
    --target_repo TARGET_REPO \
    --root_folder ROOT_FOLDER \
    --path_to_migrate_subfolder_script PATH_TO_MIGRATE_SUBFOLDER_SCRIPT \
    --max_subfolders_to_migrate_in_parallel MAX_SUBFOLDERS_TO_MIGRATE_IN_PARALLEL \
    --outdir OUTDIR

```
where:

--source_jpd: Source server ID.  
--source_repo: Source repository.  
--target_jpd: Target server ID.  
--target_repo: Target repository.  
--root_folder:  The root folder containing subfolders to migrate.  
--path_to_migrate_subfolder_script: (Optional) The path to the [migrate_n_subfolders_in_parallel.sh](../transfer-artifacts-in-sub_folders_in_parallel/migrate_n_subfolders_in_parallel.sh) script used for migrating subfolders.  
--outdir (optional): Output directory for the generated screen commands Bash script. Default is the current directory.

## Example:
```
python generate_screen_commands_for_subfolders.py \
--source_jpd  usvartifactory5 \
--source_repo merlin \
--target_jpd jfrogio \
--target_repo merlin \
--root_folder BoseCorp \
--path_to_migrate_subfolder_script "/app/sureshv/migrate_n_subfolders_in_parallel.sh" \
--max_subfolders_to_migrate_in_parallel 18 \
--outdir "/app/sureshv/merlin"
```
Here BoseCorp is a folder under merlin repository.
In the  "/app/sureshv/merlin" you will find the  generated script similar to [merlin_generated_screen_cmds.sh](output/merlin_generated_screen_cmds.sh) .

This will generate screen commands to migrate subfolders from the merlin repository in the usvartifactory5 Artifactory server to the merlin repository in the jfrogio Artifactory server. The screen commands will be saved in a Bash script file in the specified output directory.

Make sure to replace the placeholders with your actual values.

## Script Description
The script performs the following tasks:

- Executes a JFrog CLI (jf) command to fetch subfolder information from Artifactory.
- Parses the JSON response to obtain a list of subfolders.
- Generates screen commands for migrating subfolders in parallel. If there are more subfolders you can specify the number of subfolders to migrate in parallel
- Creates a Bash script that runs these screen commands with a maximum number of concurrent jobs.

## Running the Script
To run the script, follow these steps:

- Ensure you meet the prerequisites mentioned above.
- Use the provided command-line arguments to execute the script.
- The python script will generate a Bash script with screen commands for migrating subfolders.
- Execute the generated Bash script using nohup to initiate the migration process.
```
nohup bash /app/sureshv/merlin/merlin_generated_screen_cmds.sh &
```
I can see the screen commands that are running using:
```
screen -ls

Output:
There are screens on:
        21233.merlin-session81  (Detached)
        21135.merlin-session79  (Detached)
        28910.merlin-session77  (Detached)
        15518.merlin-session70  (Detached)
        15457.merlin-session69  (Detached)
        18991.merlin-session67  (Detached)
        18942.merlin-session66  (Detached)
        4322.merlin-session64   (Detached)
        17881.merlin-session62  (Detached)
        8140.merlin-session58   (Detached)
        8057.merlin-session55   (Detached)
        7940.merlin-session50   (Detached)
        7832.merlin-session49   (Detached)
        7767.merlin-session47   (Detached)
        7775.merlin-session48   (Detached)
        7724.merlin-session46   (Detached)
        7673.merlin-session44   (Detached)
        7653.merlin-session43   (Detached)
        7614.merlin-session41   (Detached)
```
So I know that out of the 106 subfolders under `BoseCorp` folder it is now migrating the above numbered folders i.e 41 - 81 ( so the folders for 1-40 and those that you do not see in 41 - 81 have already been migrated and it is yet to do 82-106 folders)

To see the number of artifacts per folder that have been successfully migrated , run:
```
find /app/sureshv/merlin -type f -name "successful_*" | xargs -I {} wc -l {}
```
or  

to see only the log file names run:  
```
find /app/sureshv/merlin -type f -name "successful_*" | xargs -I {} wc -l {} | awk '$1 > 1 {print $2}'
```
Also transfer failures can be be checked using:
```
find /app/sureshv/merlin -type f -name "failed_*" | xargs -I {} wc -l {}  

or

find /app/sureshv/merlin -type f -name "failed_*" | xargs -I {} wc -l {} | awk '$1 > 1 {print $2}'
```

If for any reson you want to stop all the transfers , first get the  process ID that the `nohup` is running using and kill it:
```
ps -ef | grep merlin_generated_screen_cmds.sh
```
Then kill all the screen sessions using the following where `merlin` is the name of the repository:

```
session_ids=$(screen -ls | awk '/\.merlin-/{print $1}')
for session_id in $session_ids; do
    screen -X -S "$session_id" quit
done
```
