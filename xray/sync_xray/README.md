# Sync XRAY Policies, Watches and Ignore rules.
This folder has scripts that can be used to sync XRAY policies, watches and ignore rules from source JPD to Target JPD

## Pre-Condition
1. Install JF CLI (https://jfrog.com/getcli/)
2. Add Source and Target Artifactory to JF CLI using "jf config add" command

## Sync Policies
The policies from both global and project are synced. So Before Running the policy sync, make sure projects must be synced between two JPDs
```
./policy.sh source-server target-server
```

## Sync watches 
Watches from both global and project are synced. So Before Running the watch sync, make sure Policies, Repo's, builds and RB  must be synced between two JPDs
```
./watches.sh source-server target-server
```

## Sync ignore rules
Before Running the Ignore Rules sync, both policies and watches must be synced between JPDs

```
./Ignore_rules.sh source-server target-server
```
