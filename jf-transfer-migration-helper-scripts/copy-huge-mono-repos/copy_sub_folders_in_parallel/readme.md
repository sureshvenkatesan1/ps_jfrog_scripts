Script to copy ( recursively) the contents of folder "liquid/BoseCorp/" and "liquid/conan-center-index/" in a loop :
a) 5 subfolders  at a  time from liquid repo to  sureshv-liquid-generic repo in bosesh

```
Usage:
example:

bash ./copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh <source artifactory> <source repo>  <target artifactory> <target repo> [<root-folder to copy from source repo to target>]

Example:
In /Users/sureshv/Documents/From_Customer/Bose/tests
bash ./copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh bosesh liquid  bosesh sureshv-liquid-generic BoseCorp

In /Users/sureshv/Documents/From_Customer/Bose/tests/conan-center-index
bash ../copy_subfolders_in_given_root_folder_from_source_repo_to_generic_target_repo_in_parallel.sh bosesh liquid  bosesh sureshv-liquid-generic conan-center-index
```