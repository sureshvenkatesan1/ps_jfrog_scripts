
Get the build name for a project with projectKey = aa1

```text
jf rt curl -s -XGET "/api/build?project=aa1" --server-id=soleng
```
Output:
```text
{
  "builds" : [ {
    "uri" : "/slash-jenkins-app-maven-sonar",
    "lastStarted" : "2022-03-10T01:48:00.050+0000"
  } ],
  "uri" : "https://soleng.jfrog.io/artifactory/api/build?buildRepo=aa1-build-info"
}
```
---

To view the builds in the Artifacts tree view for the projectKey aa1 ( in repo aa1-build-info ) use:
https://proservicesone.jfrog.io/ui/repos/tree/General/aa1-build-info?projectKey=aa1

To view  the Artifactory >Builds published since epoch 1601424000000 i.e `GMT: Wednesday, September 30, 2020 
12:00:00 AM` ( as per https://www.epochconverter.com/)  use:

https://proservicesone.jfrog.io/ui/builds?after=1601424000000&type=builds&projectKey=aa1

Note: If you're unable to locate the builds, adjust the "after" filter in the Builds "Search" UI field to a date 
prior to the above epoch timestamp. 

---

The "build-info" repo for a project should be automatically created when a project is created and will have the name 
projectKey-build-info . Otherwise  it is created when a build is published to a project.

The "jf rt transfer-config" may not create the "build-info" repos  and so the buildinfos for projects may not be migrated automatically by the "jf rt transfer-files" command as the target repo will not exist.

So you can  publish a dummy build named `test` with buildnumber `1` which will create the projectKey-build-info repo  ( but takes some time to be visible in the UI) :

```text
jf rt bp  --project aa1 --server-id=target-server test 1
```

Note: The following command with `--ignore-state` does not transfer the build infos:
```
jf rt transfer-files source-rt target-rt --include-repos aa1-build-info --ignore-state 
```
Need to check why the "-–ignore-state" does not work for doing "jf rt transfer-files" for a build-info repo


Verify that the 'data-transfer' user plugin is installed on the source instance for the "transfer-files" command to work 

Then use the following command  without the `--ignore-state`  to then transfer the build infos ( it works):
```
jf rt transfer-files source-rt target-rt --include-repos aa1-build-info 
```
Note: Instead of using "jf rt transfer-files" you can also use the  script :
```text
#!/bin/bash
    source_server_name=source-rt
    target_server_name=target-rt
    reponame=aa1-build-info
    echo -e "\n\n##### Performing for $reponame #####"
    mkdir $reponame
    cd $reponame/
    echo "Downloading $reponame from $source_server_name server..."
    jf rt dl "$reponame" --server-id=$source_server_name
    echo "Uploading $reponame to $target_server_name server..."
    jf rt u "*" "$reponame" --server-id=$target_server_name
    cd ..
    rm -rf $reponame
    echo -e "Completed uploading the build-infos in $reponame ..."
```

Note: Though the  file count and the folder count were the same , the storage of this aa1-build-info repo in the 
target  was smaller than the aa1-build-info in the source artifactory instance.



---

You can get the details of all the builds in a project's build-info repo using:
```text
jf rt curl /api/storageinfo --server-id=soleng | jq | grep "aa1-build-info" -A 10
```
Note: Though all the buildinfo were uploaded sometimes  the above /api/storageinfo API may show higher  "usedSpace" for 
the source repo compared as seen below:

```text
{
      "repoKey": "aa1-build-info",
      "repoType": "LOCAL",
      "foldersCount": 1,
      "filesCount": 2,
      "usedSpace": "103.39 KB",
      "usedSpaceInBytes": 105872,
      "itemsCount": 3,
      "packageType": "BuildInfo",
      "projectKey": "aa1",
      "percentage": "0%"
    }
```
compared to the target repo which shows a lower "usedSpace":

```text
{
      "repoKey": "aa1-build-info",
      "repoType": "LOCAL",
      "foldersCount": 2,
      "filesCount": 2,
      "usedSpace": "47.10 KB",
      "usedSpaceInBytes": 48231,
      "itemsCount": 4,
      "packageType": "BuildInfo",
      "projectKey": "default",
      "percentage": "0%"
    }
```

This must be because some files in the  "aa1-build-info" repo in the source were not garbage collected. 


After some time if you :
1. Calculate the storage for the Artifactory Instance
```
jf rt curl -X POST "/api/storageinfo/calculate" --server-id=soleng
 
``` 
Output:
```text
{"info":"Calculating storage summary scheduled to run successfully"}
```


2. wait for 2 min for calculation to complete.

3. Generate the storage details for the "aa1-build-info" repo , it should show now show the same "filesCount" and 
   "usedSpace" for the source and target repos:
```text
   jf rt curl /api/storageinfo --server-id=soleng | jq | grep "aa1-build-info" -A 10
```
