For huge mono repos - the transfer migration tool when transferring files for Conan repositories, jfrog-cli makes sure to upload files with the following name suffix last (after all the other files in the repository have been transferred -
```
conanfile.py
conaninfo.txt
.timestamp
```

That’s the reason why you see this message -
```
2023/08/28 21:43:35 [Debug] Delaying the upload of file 'merlin/Temporary/SpitfireUpdate/13.1.43+gb24076e/master/b24076e0c02ee674ac5eb5ee0f8a92fd5d1f1c29/package/91c1d01c85e0c084bbd511c544cf3000f28582ba/b1644ce5d1b757e7e5356500962247d6/.timestamp'. Writing it to be uploaded later...
```
But the problem is there are `294` subfolders folders under liquid/BoseCorp/ (  liquid is the conan repo name ).

Got using [generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh](generate_jf_cp_cmds_for_subfolders_in_given_root_folder/generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh):

```
bash ./generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh bosesh liquid  bosesh sureshv-liquid-generic BoseCorp | wc -l
```

So even the following fails:
```
jf rt cp liquid/BoseCorp/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
```

It fails with:
```
15:23:08 [Debug] JFrog CLI version: 2.46.2
15:23:08 [Debug] OS/Arch: darwin/amd64
15:23:08 [🔵Info] Searching artifacts...
15:23:08 [Debug] Usage Report: Sending info...
15:23:08 [Debug] Searching Artifactory using AQL query:
 items.find({"type":"any","path":{"$ne":"."},"$or":[{"$and":[{"repo":"liquid","path":"BoseCorp","name":{"$match":"*"}}]},{"$and":[{"repo":"liquid","path":{"$match":"BoseCorp/*"},"name":{"$match":"*"}}]}]}).include("name","repo","path","actual_md5","actual_sha1","sha256","size","type","modified","created")
15:23:08 [Debug] Sending HTTP POST request to: https://rtf.bose.com/artifactory/api/search/aql
15:23:08 [Debug] Sending HTTP GET request to: https://rtf.bose.com/artifactory/api/system/version
15:23:08 [Debug] Artifactory response: 200 OK
15:23:08 [Debug] JFrog Artifactory version is: 7.41.14
15:23:08 [Debug] Sending HTTP POST request to: https://rtf.bose.com/artifactory/api/system/usage
15:23:09 [Debug] Usage Report: Usage info sent successfully. Artifactory response: 200 OK

15:24:09 [Debug] Artifactory response: 200 OK
15:24:09 [Debug] Streaming data to file...
15:35:23 [Debug] Finished streaming data successfully.
15:35:44 [🚨Error] unexpected EOF
15:35:44 [🚨Error] unexpected EOF
15:35:44 [🚨Error] unexpected EOF
15:35:44 [🚨Error] copy finished with errors, please review the logs
15:35:44 [🚨Error] copy finished with errors, please review the logs
```


Similarly there is another path liquid/conan-center-index/ which also has `112` sub-folders and that also will fail.
Got using:
```
bash ./generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh bosesh liquid  bosesh sureshv-liquid-generic conan-center-index | wc -l
```
 
 I tried push replication for the `liquid` repo and that also does not seem to work.

 The `jf rt transfer-files` attemps to transfer the whole repo . Instead we need an option to specify `"include Patterns"` similar to to how we can do in replication.

---

I did the followig simple test:

1. create a `sureshv-liquid-test` conan repo in source  and target artifactory (  No need to change the repo layout to `simple-default` , keep it as `conan-default`). 
Have copied a  test package from the liquid repo to this repo.
2. Create `sureshv-liquid-generic` in source and target artifactory.
3. Copy `liquid/test` folder  to `sureshv-liquid-generic` 
4. Transfer  `sureshv-liquid-generic` from source to target using the transfer migration tool.

```
jf rt transfer-files  --include-repos "sureshv-liquid-generic" --ignore-state bosesh bosesaas
```

5. copy `test` folder from `sureshv-liquid-generic` in target to `sureshv-liquid-test` in target.
Note: Since it is only one folder , you can copy the entire repo. 
```
jf rt cp sureshv-liquid-generic sureshv-liquid-test --flat=false --threads=8 --dry-run=false --server-id bosesaas
```

6. export the `sureshv-liquid-test` repos in source and target and compare in `meld`  to see if they are same.
```
cd /Users/sureshv/Documents/From_Customer/Bose/tests
jf rt dl "sureshv-liquid-test/*" source/ --server-id bosesh
jf rt dl "sureshv-liquid-test/*" target/ --server-id bosesaas

meld source target
```
The source and target folders were identical.

---

## Here is the plan I have for migrating the 1.5TB liquid repo:

Now I do not need the `sureshv-liquid-test` conan repo as I can start copying from the  liquid repo to the `sureshv-liquid-generic` in source and follow the above steps.


Do the copy,   folder by folder like  `step 3` above , so that you can do the steps 4,5,6 after that:

Note: For the `conan` repo you don't have to copy the liquid/.conan folder as it will  automatically be created in `step 5` above and the 
`liquid/.conan/packages.ref.json` containing the conan package manifest will also be generated  as packages get copied to the conan repo ( that is the default conan repo behavior).

```
jf rt cp liquid/_/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/bose-corp/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/BoseCorp/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh

jf rt cp liquid/Build_RivieraLpmService/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/conan-center-index/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh

jf rt cp liquid/dr1032972/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/mh70023/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh

jf rt cp liquid/nh20219/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/PR_Tests/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp liquid/test/  sureshv-liquid-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
```

Do the transfer
```
jf rt transfer-files  --include-repos "sureshv-liquid-generic" --ignore-state bosesh bosesaas
```

copy   folders from `sureshv-liquid-generic` in target to `liquid` repo in target.
```
jf rt cp sureshv-liquid-generic/_/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/bose-corp/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/BoseCorp/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/Build_RivieraLpmService/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/conan-center-index/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/dr1032972/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/mh70023/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/nh20219/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/PR_Tests/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
jf rt cp sureshv-liquid-generic/test/  liquid/ --flat=false --threads=8 --dry-run=false --server-id bosesaas
```

But we know that for the big folders  like `sureshv-liquid-generic/BoseCorp/` and `sureshv-liquid-generic/conan-center-index/`  it will fail.

For this or any root-folder to copy the subfolders recursively I have the 
[copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh](copy_sub_folders_in_parallel/copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh) script as mentioned in 
[copy_sub_folders_in_parallel/readme.md](copy_sub_folders_in_parallel/readme.md)

---




