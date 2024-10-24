Script to copy ( recursively) the contents of folder "liquid/exampleCorp/" and "liquid/conan-center-index/" in a loop :
a) 5 subfolders  at a  time from liquid repo to  sureshv-liquid-generic repo in examplesh

```
Usage:
example:

bash ./copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh <source artifactory> <source repo>  <target artifactory> <target repo> [<root-folder to copy from source repo to target>]

Example:
In /Users/sureshv/Documents/From_Customer/example/tests
bash ./copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh examplesh liquid  examplesh sureshv-liquid-generic exampleCorp

In /Users/sureshv/Documents/From_Customer/example/tests/conan-center-index
bash ../copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh examplesh liquid  examplesh sureshv-liquid-generic conan-center-index
```

References: 

[Copy Item](https://jfrog.com/help/r/jfrog-rest-apis/copy-item)
[ARTIFACTORY: How to Copy / Move large repositories](https://jfrog.com/help/r/artifactory-how-to-copy-move-large-repositories/artifactory-how-to-copy/move-large-repositories)
[How to Move Artifacts with AQL](https://jfrog.com/help/r/artifactory-an-advanced-approach-to-move-copy-artifacts/how-to-move-artifacts-with-aql)
[ARTIFACTORY: How to copy a large repository or folder from one location to the other](https://jfrog.com/help/r/artifactory-how-to-copy-a-large-repository-or-folder-from-one-location-to-the-other)