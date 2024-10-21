How to handle the error "Virtual repository must include only repositories from the same project it was created with"  when migrating  virtual repos in a JFrog project to the SAAS instance as mentioned in the KB , "[
Virtual repository must include only repositories from the same project it was created with
](https://jfrog.com/help/r/artifactory-why-do-i-get-the-error-virtual-repository-must-include-only-repositories-from-the-same-project-it-was-created-with)"? 

**Steps  to reproduce**  the above error  from an earlier ticket  [264725](https://groups.google.com/a/jfrog.com/g/support-followup/c/y39sr-2w_3E/m/lQHrrSMhAwAJ) :

1. Created project1(p1)
2. Create a local repository1(p1-lr1) and virtual repository(p1-vr1) and include the local repository in it.
3. Created project2(p2)
4. Create a local repository1(p2-lr2) and virtual repository(p2-vr2) and include the local repository in it.
5. In Project1(p1), we have shared the local repository(p1-lr1) with Project2(p2)
6. Project2(p2), we have included project1’s local repository(p1-lr1) as part of the virtual repository(p2-vr2). 
   Since the local repository is part of both the projects, there is no issue.
7. Later, to reproduce the issue, we opened Project1 and unshared the local repository(p1-lr1) from Project2.
8. The above activity will not remove the local repository(p1-lr1) of Project1 in Project2’s virtual repository(p2-vr2)
   . However, if we try to modify any of the configurations of Project2’s virtual repository, we will get the error “Virtual repository must include only repositories from the same project it was created with” because that specific repository was not part of it anymore.

**We need  a script to :**

- a) go through the list of aggregated repositories (local, remote, and virtual) and confirm which 
are not shared with the project so you can do the steps in the above KB.

- b) if I open Project1 and unshared the local repository "p1-lr1" from Project2 i.e "p2" , then how can I find from project p2 that the repo "p1-lr1" is not shared with p2?

## A Solution:
The script  [find_unshared_repositories_in_project.py](find_unshared_repositories_in_project.py) helps  to to go through the list of aggregated repositories (local, remote,
and virtual) i.e all the "repoKey"  in the output of
```
curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p2"
```
( including the virtual repos recursively) as recommended by the above KB and find if any repo is not shared with project p2 i.e check the "sharedWithProjects" for the repo does not contain project p2.

Details in [find_unshared_repositories_in_project.md](find_unshared_repositories_in_project.md)

---

I did run into following errors while performing the "Steps  to reproduce" above:

- "Failed to create repository p1-vr1: Virtual repository must include only repositories from the same project it   was created with"

- Resources [p1-lr1] already exists in another project, consider removing them first from source project or use force=true query param to force override resources

---

As per [RTDEV-33942](https://jfrog-int.atlassian.net/browse/RTDEV-33942) :

i) By design, “Virtual repository must include only repositories from the same project it was created with” - This 
statement should be valid for any repo under virtual, even if it’s nested under virtual repo.

Following validation   missing in UI:
- Virtual repository can be assigned to a Project if all its members directly or indirectly already assigned to the Project.

- Virtual repository can be shared with a Project if all its members directly or indirectly already shared with the Project.

ii) The design doc for “managing  virtual repositories within a project” is not fully baked-in . For example  all project entities ( including sharing / assigning repos to project ) are managed by Access vs the virtual repo config is managed by Artifactory.

iii) So RTDEV-33942 is  an enhancement and currently is documented  with a workaround for  “managing  virtual repositories within a project” wrt RTDEV-33942 under  [Known issues for in Artifactory 7.63](https://jfrog.com/help/r/jfrog-release-information/artifactory-7.63?tocId=GME3dNu8XN6wP8NYkRTWAw) .
This workaround is still required  in Artifactory 7.73  .

---

### Here is the workaround description:
When assigning a virtual repository to a project, no validation is performed. Validation is performed only when the assigned virtual repository is changed. This means that an invalid repository can be assigned to a project, and no configuration changes can be made to the virtual repository.

Two possible workarounds:

- If you want to make configuration changes to the virtual repository, you should unassign the virtual repository 
from the project, remove all repositories underneath the virtual repository, and then reassign the virtual repository back to the project. You can then add back any valid repositories to the virtual repository.

- You can share the virtual repository instead of assigning it to a project.

---

### Some JFrog Project i.e Access REST APIs I used in my test:

How to find out which projects a local repository assigned to a project "p1" is shared with?
Here is an undocumented API got from using developers tools from the UI page:
https://proservices.jfrog.io/ui/admin/repositories/local?projectKey=p2

```text
curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p1" | jq '.'
```
Output:
```text
[
  {
    "repoKey": "p1-lr1",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p1",
    "projectName": "project1",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [
      "p2"
    ],
    "shareWithAllProjects": false,
    "replications": false,
    "target": false,
    "sharedReadOnly": false
  }
]
```
**Note:** You cna find this information from any project that this "repoKey": "p1-lr1" is shared with.
For example from the project p2 as:
```text
curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p2" | jq '.'
```
Output:
```text
[
  {
    "repoKey": "p2-lr2",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p2",
    "projectName": "project2",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [],
    "shareWithAllProjects": false,
    "replications": false,
    "target": false,
    "sharedReadOnly": false
  },
  {
    "repoKey": "p1-lr1",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p1",
    "projectName": "project1",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [
      "p2"
    ],
    "shareWithAllProjects": false,
    "replications": false,
    "target": true,
    "sharedReadOnly": false
  }
]
```

After doing the step 7, to unshare the local repository(p1-lr1) from Project2 "p2" if you check the 
virtual repos in "p2" it will still show the "p1-lr1" in "selectedRepos" in the "repoKey": "p2-vr2":
```text
curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/virtual/info?projectKey=p2" | jq '.'
```

output is as follows

```
[
  {
    "repoKey": "p2-vr2",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p2",
    "projectName": "project2",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [],
    "shareWithAllProjects": false,
    "selectedRepos": [
      "p1-lr1",
      "p2-lr2"
    ],
    "numberOfIncludesRepositories": 2,
    "target": false,
    "sharedReadOnly": false
  }
]
```
Then you will have to confirm that the local repo "p1-lr1" is not shared with project p2 by checking the project p1 using:

```curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p1" | jq '.'```

Output:
```text
[
  {
    "repoKey": "p1-lr1",
    "repoType": "Generic",
    "hasReindexAction": false,
    "projectKey": "p1",
    "projectName": "project1",
    "environments": [
      "DEV"
    ],
    "sharedWithProjects": [],
    "shareWithAllProjects": false,
    "replications": false,
    "target": false,
    "sharedReadOnly": false
  }
]
```
---

Using jq how can I parse the output to get the "sharedWithProjects" for "repoKey": "p1-lr1" ?

```text
curl -X GET -H "Authorization: Bearer ${MYTOKEN}" "https://proservices.jfrog.io/ui/api/v1/ui/admin/repositories/local/info?projectKey=p2" | jq '.[] | select(.repoKey == "p1-lr1") | .sharedWithProjects'
```
Output:
```text
[
  "p2"
]
```
---
