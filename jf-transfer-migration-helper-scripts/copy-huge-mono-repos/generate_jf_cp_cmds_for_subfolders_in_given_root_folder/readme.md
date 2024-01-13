The output of 

`jf rt curl "/api/storage/sureshv-liquid-test?list&deep=1&depth=1&listFolders=1" --server-id bosesaas`
is
```
{
  "uri" : "https://bose.jfrog.io/artifactory/api/storage/sureshv-liquid-test",
  "created" : "2023-09-08T22:04:31.199Z",
  "files" : [ {
    "uri" : "/.conan",
    "size" : -1,
    "lastModified" : "2023-09-08T21:37:44.915Z",
    "folder" : true
  }, {
    "uri" : "/_",
    "size" : -1,
    "lastModified" : "2023-09-08T21:37:43.915Z",
    "folder" : true
  } ]
}
```



I want to use this output and generate the command like the following for each "uri":
```
jf rt cp sureshv-liquid-test/.conan/  sureshv-merlin-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
jf rt cp sureshv-liquid-test/_/  sureshv-merlin-generic/ --flat=false --threads=8 --dry-run=false --server-id bosesh
```

You can use this script:
```
bash ./generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh bosesh liquid  bosesh sureshv-liquid-generic conan-center-index 
or
bash ./generate_jf_cp_cmds_for_subfolders_in_given_root_folder.sh bosesh liquid  bosesh sureshv-liquid-generic conan-center-index | wc -l  
```