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