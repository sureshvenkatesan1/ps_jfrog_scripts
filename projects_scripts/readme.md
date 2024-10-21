
Can you please give a high level picture of the sequence in which you used the scripts when using JFrog Projects ?
## High level overview of  the [projects_scripts](.) scripts  :

1. At the start of  SAAS migration   none of the repos  , projects will exist in the SAAS instance.
2. Next  we can create the repos  in SAAS after fixing the on-prem repos to be in only one JFROG Environment (  like  DEV or PROD).

Note:

   a)Mapping a repo to single ENV is a required step before SAAS migration.

   b)if they map repo to DEV will there permissions they use in the on-prem PROD JPD ( i.e repo in onprem was mapped  to DEV and PROD Env) be intact ?
   
   This change was introduced via [RTDEV-28886](https://jfrog-int.atlassian.net/browse/RTDEV-28886) and discussed in
   [#breaking-change-multiple-environments-per-repository](https://jfrog.slack.com/archives/C053UFFU8EQ/p1681825622449059) slack :
   
   **The solution from Product was:**
   If you one repo that you want to share with Developers Role (DEV) and Production team Role (PROD) the workaround is:

   i)- you can do it by assigning more than one environment to a role

   ii)How can I use the same repo with 2 different roles? - same answer as above

   In short you want the 2 roles to share the same repository, not the same environments.

**Note:** You can use [repos_mapped_to_multiple_env.sh ](repos_mapped_to_multiple_env.sh ) or 
[repos_mapped_to_multiple_env.py](repos_mapped_to_multiple_env.py) to determine the repos in the on-prem that are 
mapped to more than one Environment.

3. Next use the [getProjectDiffList.sh](getProjectDiffList.sh) to create the projects in the SAAS instance.
4. Note: the [getProjectComponentDiffList.sh](getProjectComponentDiffList.sh) only checks for users, groups and roles in
```   
   updateDataComponents "users"
   updateDataComponents "groups"
   updateDataComponents "roles"
```
   
   Is there a reason why the   Environment difference  is not checked ? Is it because the customer did not have any project level environments ?
>> These scripts were developed when we were working for infosys  that time environment option was not available.
Instead of these scripts please use the "jf rt transfer-config-merge" for transferring projects  using the options:
```text
Options:
  --exclude-projects    [Optional] A list of semicolon-separated JFrog Projects to exclude from the transfer. You can use wildcards to specify patterns for the project keys.

  --include-projects    [Optional] A list of semicolon-separated JFrog Project keys to include in the transfer. You can use wildcards to specify patterns for the JFrog Project keys.

```

You can add environments to project as mentioned in
[readme_to_workaround_terraform_projects_provider.md](https://github.com/sureshvenkatesan/config_RT_Xray_with_Terraform/blob/master/projects/readme_to_workaround_terraform_projects_provider.md)
or
https://github.com/shivaraman83/projects-kickstart/blob/main/README.md

```text
##create a new environment with name as $project-key-UAT
curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -X POST -H "Content-Type: application/json" $SOURCE_JPD_URL/access/api/v1/projects/$PROJECT_KEY/environments -d '{ "name": "'$PROJECT_KEY'-UAT"}'

```
To delete the project environment (stp-UAT) use:
```text
curl -H"Authorization: Bearer $JPD_AUTH_TOKEN" -X DELETE -H "Content-Type: application/json" $SOURCE_JPD_URL/access/api/v1/projects/$PROJECT_KEY/environments/stp-UAT
```
---


How is it possible to set the **read-only** permission via REST API when sharing a repository with another project 
using the API [Share Repository with Target Project](https://jfrog.com/help/r/jfrog-rest-apis/share-repository-with-target-project)?

>> Use the same REST API and pass the query params "?readOnly=true" along with it.

Please find the example below:
```text
curl -X PUT "${baseUrl}/access/api/v1/projects/_/share/repositories/${repo_name}/{target_project_key}?readOnly=true" -H "accept: application/json -H 'Authorization: Bearer <a valid access-token>"
```


---

## Is it possible to create custom roles in projects using CLI or REST API and Its steps?

We cannot create a custom project role using JFrog CLI but we can achieve this use case using the [Add New Role](https://jfrog.com/help/r/jfrog-rest-apis/add-a-new-role) REST 
API. Using this API, we can add roles to the projects . Also Please note that it requires a user assigned with the 'Administer the Platform' role or Project Admin permissions to run this REST API and with the Authorization: Bearer header parameter. Attached below example for your reference.

REST API:
POST ${baseUrl}/access/api/v1/projects/{project_key}/roles

Example:

```
curl -H "Authorization: Bearer <ADMIN_TOKEN>" -X POST “http://<JFROG_BASEURL>/access/api/v1/projects/<project_key>/roles” -H "Content-Type: application/json" -T AddRole.json
```

Below is the sample JSON input to define name of the role, type, actions(permissions) & environment.

$ cat AddRole.json

```
{
"name": "custom_viewer",
"actions": [
"READ_REPOSITORY",
"READ_RELEASE_BUNDLE",
"READ_BUILD",
"READ_SOURCES_PIPELINE",
"READ_INTEGRATIONS_PIPELINE",
"READ_POOLS_PIPELINE"
],
"type": "CUSTOM",
"environments": [
"PROD"
]
}
```

In the above example, we have added a role called custom_viewer with a read permission and environment as Prod to the project.

---

How to add  a  user to the project as “Project Admin” ?

Assign a User to a Project: (user should be already in the Artifactory)
use  the [Add or Update User in Project](https://jfrog.com/help/r/jfrog-rest-apis/update-user-in-project) API:

```
curl -H "Authorization: Bearer <TOKEN>"  -X PUT "http://localhost:8082/access/api/v1/projects/{project_key}/users/{userName}" -H "Content-Type: application/json" -T user.json
User Json file:
{
"name": "userName",
"roles": [
"Project Admin"
]
}
```

Delete a User from a Project:
```
curl -H "Authorization: Bearer <TOKEN>"  -X DELETE  http://localhost:8082/access/api/v1/projects/{project_key}/users/{user}
```
---

Unassign the repository first from the project. Then you may perform the changes needed (i.e. add a repository or update another configuration in that repository). Afterward, you can assign the repository back to the project.

[Unassign a Project from a Repository](https://jfrog.com/help/r/jfrog-rest-apis/unassign-a-project-from-a-repository).

```
curl -H "Authorization: Bearer <TOKEN>" -XDELETE "<ART_URL>/access/api/v1/projects/_/attach/repositories/<REPO_NAME>"
```


Rest api endpoint to assign/move the repository back to a project.
[Move Repository in a Project](https://jfrog.com/help/r/jfrog-rest-apis/move-repository-in-a-project)
```
curl -H "Authorization: Bearer <TOKEN>" -XPUT "<ART_URL>/access/api/v1/projects/_/attach/repositories/<REPO_NAME>/<PROJECT>?force=true"
```

---
Get the project name from a project key :

```text
curl -s -XGET -H "Authorization: Bearer ${MYTOKEN}" https://soleng.jfrog.io/ui/api/v1/ui/storagesummary/projects | jq '.[] | select(.projectKey == "aa1") | .projectName'
```

or
Get the project details from UI using the url below for projectKey=aa1: 
https://proservicesone.jfrog.io/ui/admin/projects/overview?projectKey=aa1

---
Get the project key from a project name :

```text
curl -s -XGET -H "Authorization: Bearer ${MYTOKEN}" https://soleng.jfrog.io/ui/api/v1/ui/storagesummary/projects | jq '.[] | select(.projectName == "Asafc-proj1") | .projectKey'
```
---
Get the projectName and projectKey in tabular format :

```text
echo "projectKey=projectName"
curl -s -XGET -H "Authorization: Bearer ${MYTOKEN}" https://soleng.jfrog.io/ui/api/v1/ui/storagesummary/projects  | jq -r '.[] | "\(.projectKey)=\(.projectName)"'
```
---



