# Version 0.9 - Nov 5 2024
from asyncore import poll3

import requests
import urllib3
import time
import sys

from docutils.nodes import target

urllib3.disable_warnings()

SYSTEM_REPOS = ["TOTAL", "auto-trashcan", "jfrog-support-bundle", "jfrog-usage-logs"]
repos_to_do = []

# This class defines an Artifactory object that carries its own information
# This helps with readability, re-usability, and to reduce the need to hard code information
class Artifactory:
    def __init__(self, url, auth, name):
        self.url = url
        self.auth = auth
        self.name = name
        self.storage = self.storage()
        self.repos = self.get_repo_list()
        self.repository_configurations = self.get_repository_configurations()
        self.repo_details = self.storage["repositoriesSummaryList"]
        self.local_storage, self.remote_storage, self.federated_storage = self.get_filtered_repos_storage()
        self.local_configs, self.federated_configs, self.remote_configs, self.virtual_configs = self.get_filtered_repo_configs()
        self.xray_policies = []
        self.xray_watches = []
        self.xray_ignore_rules = []

    def storage(self):
        storage = requests.get(self.url+"/artifactory/api/storageinfo", auth=self.auth, verify=False)
        return storage.json()

    def get_repo_list(self):
        return [summary["repoKey"] for summary in self.storage["repositoriesSummaryList"]]

    def print_remotes_with_password(self):
        out_file = open("./remotes_with_password_{}.log".format(self.name), 'w')
        for repo in self.repository_configurations["REMOTE"]:
            if repo["password"] != "":
                print(repo["key"])
                out_file.write(repo["key"])
                out_file.write('\n')

    def get_repository_configurations(self):
        repos = requests.get(self.url + "/artifactory/api/repositories/configurations", auth=self.auth, verify=False)
        return repos.json()

    def get_filtered_repos_storage(self):
        l, r, v, f = {}, {}, {}, {}
        for summary in self.storage["repositoriesSummaryList"]:
            if summary["repoType"] == "LOCAL":
                l[summary["repoKey"]] = summary
            if summary["repoType"] == "FEDERATED":
                f[summary["repoKey"]] = summary
            if summary["repoType"] == "CACHE":
                r[summary["repoKey"]] = summary
        return l, r, f

    def get_repo_content(self, repo_name):
        headers = {'content-type': 'text/plain', }
        query = 'items.find({"name":{"$match":"*"}, "repo":"'+repo_name+'"}).include("name", "path")'
        resp = requests.post(self.url+"/artifactory/api/search/aql", auth=self.auth, headers=headers, data=query, verify=False)
        return resp.json()["results"]

    def transform_local_to_federated(self):
        for repo in self.local_storage:
            print("Transforming local repository:", repo)
            headers = {'content-type': 'application/json', }
            resp = requests.post(self.url + "/artifactory/api/federation/migrate/{}".format(repo), auth=self.auth, headers=headers, verify=False)
            if resp.status_code != 200:
                print("Non-200 response:", resp.status_code)
                print(resp.text)
        self.local_storage, self.remote_storage,  self.federated_storage = self.get_filtered_repos_storage()

    def refresh_storage_summary(self):
        headers = {'content-type': 'application/json', }
        resp = requests.post(self.url + "/artifactory/api/storageinfo/calculate", auth=self.auth, headers=headers, verify=False)
        if resp.status_code != 202:
            print("Non-202 response:", resp.status_code)
            print(resp.text)

        self.local_storage, self.remote_storage,  self.federated_storage = self.get_filtered_repos_storage()

    def get_filtered_repo_configs(self):
        l, f, r, v = {}, {}, {}, {}

        try:
            for repo in self.repository_configurations["LOCAL"]:
                repo_name = repo["key"]
                l[repo_name] = repo
        except KeyError:
            l = {}

        try:
            for repo in self.repository_configurations["FEDERATED"]:
                repo_name = repo["key"]
                f[repo_name] = repo
        except KeyError:
            f = {}

        try:
            for repo in self.repository_configurations["REMOTE"]:
                repo_name = repo["key"]
                r[repo_name] = repo
        except KeyError:
            r = {}

        try:
            for repo in self.repository_configurations["VIRTUAL"]:
                repo_name = repo["key"]
                v[repo_name] = repo
        except KeyError:
            v = {}

        return l, f, r, v

    def load_xray_data(self):

        # Get Policies
        resp = requests.get(self.url + "/xray/api/v2/policies", auth=self.auth, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of policies:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting policies")
        self.xray_policies = resp.json()

        # Get Watches
        resp = requests.get(self.url + "/xray/api/v2/watches", auth=self.auth, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of watches:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting watches")
        self.xray_watches = resp.json()

        # Get Ignore Rules
        resp = requests.get(self.url + "/xray/api/v1/ignore_rules", auth=self.auth, verify=False)
        if resp.status_code != 200:
            print("Non-200 response for getting ist of watches:", resp.status_code)
            print(resp.text)
        else:
            print("Success collecting watches")
        self.xray_ignore_rules = resp.json()


class FederationHelper:
    def __init__(self, rt1, rt2):
        self.rt1 = rt1
        self.rt2 = rt2
        self.missing_r1, self.missing_r2 = self.missing_repos()

    def missing_repos(self):
        missing_r1 = [str(repo) for repo in self.rt2.repos if repo not in self.rt1.repos]
        missing_r2 = [str(repo) for repo in self.rt1.repos if repo not in self.rt2.repos]
        return missing_r1, missing_r2

    def missing_locals(self):
        missing_r1 = [str(repo) for repo in self.rt2.local_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.local_storage if repo in self.missing_r2]
        return missing_r1, missing_r2

    def missing_federated(self):
        missing_r1 = [str(repo) for repo in self.rt2.federated_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.federated_storage if repo in self.missing_r2]
        return missing_r1, missing_r2

    def missing_remote(self):
        missing_r1 = [str(repo) for repo in self.rt2.remote_storage if repo in self.missing_r1]
        missing_r2 = [str(repo) for repo in self.rt1.remote_storage if repo in self.missing_r2]
        return  missing_r1, missing_r2

    def missing_virtual(self):
        missing_r1 = [repo for repo in self.rt2.virtual_configs.keys() if repo not in self.rt1.virtual_configs.keys()]
        missing_r2 = [repo for repo in self.rt1.virtual_configs.keys() if repo not in self.rt2.virtual_configs.keys()]
        return missing_r1, missing_r2

    def common_repos(self):
        return [str(repo) for repo in self.rt2.repos if repo in self.rt1.repos and repo not in SYSTEM_REPOS]

    def repo_report(self):

        mlr1, mlr2 = self.missing_locals()
        mfr1, mfr2 = self.missing_federated()
        mrr1, mrr2 = self.missing_remote()
        mvr1, mvr2 = self.missing_virtual()

        out_missing_local_source = open("./missing_local_source.log", 'w')
        out_missing_local_target = open("./missing_local_target.log", 'w')

        out_missing_federated_source = open("./missing_federated_source.log", 'w')
        out_missing_federated_target = open("./missing_federated_target.log", 'w')

        out_missing_remote_source = open("./missing_remote_source.log", 'w')
        out_missing_remote_target = open("./missing_remote_target.log", 'w')

        out_missing_virtual_source = open("./missing_virtual_source.log", 'w')
        out_missing_virtual_target = open("./missing_virtual_target.log", 'w')


        print("************")
        print("# of Local Repos Missing for {}: {}".format(self.rt1.name, len(mlr1)))
        for repo in mlr1:
            out_missing_local_source.write(repo)
            out_missing_local_source.write('\n')
        print("# of Local Repos Missing for {}: {}".format(self.rt2.name, len(mlr2)))
        for repo in mlr2:
            out_missing_local_target.write(repo)
            out_missing_local_target.write('\n')
        print("************")
        print("# of Federated repos missing in {} (present in {}): {}".format(self.rt1.name, self.rt2.name, len(mfr1)))
        for repo in mfr1:
            out_missing_federated_source.write(repo)
            out_missing_federated_source.write('\n')
        print("# of Federated repos missing in {} (present in {}): {}".format(self.rt2.name, self.rt1.name, len(mfr2)))
        for repo in mfr2:
            out_missing_federated_target.write(repo)
            out_missing_federated_target.write('\n')
        print("************")
        print("# of remote Repos Missing for {}: {}".format(self.rt1.name, len(mrr1)))
        for repo in mrr1:
            out_missing_remote_source.write(repo)
            out_missing_remote_source.write('\n')
        print("# of Remote Repos Missing for {}: {}".format(self.rt2.name, len(mrr2)))
        for repo in mrr2:
            out_missing_remote_target.write(repo)
            out_missing_remote_target.write('\n')
        print("************")
        print("# of Virtual  Repos Missing in {}: {}".format(self.rt1.name, len(mvr1)))
        for repo in mvr1:
            out_missing_virtual_source.write(repo)
            out_missing_virtual_source.write('\n')
        print("# of Virtual  Repos Missing in {}: {}".format(self.rt2.name, len(mvr2)))
        for repo in mvr2:
            out_missing_virtual_target.write(repo)
            out_missing_virtual_target.write('\n')
        print("************")

    def local_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.local.keys():
                if self.rt1.local[repo_name]["filesCount"] != self.rt2.local[repo_name]["filesCount"] or self.rt1.local[repo_name]["usedSpace"] != self.rt2.local[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.local[repo_name]["filesCount"], self.rt1.local[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.local[repo_name]["filesCount"], self.rt2.local[repo_name]["usedSpace"]))

    def federated_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.federated.keys():

                if self.rt1.federated[repo_name]["filesCount"] != self.rt2.federated[repo_name]["filesCount"] or self.rt1.federated[repo_name]["usedSpace"] != self.rt2.federated[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.federated[repo_name]["filesCount"], self.rt1.federated[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.federated[repo_name]["filesCount"], self.rt2.federated[repo_name]["usedSpace"]))

    def remote_repos_diff(self):
        print("************")
        print("Checking local repositories in common")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.remote.keys():
                if self.rt1.federated[repo_name]["filesCount"] != self.rt2.federated[repo_name]["filesCount"] or self.rt1.federated[repo_name]["usedSpace"] != self.rt2.federated[repo_name]["usedSpace"]:
                    print("************")
                    print("Repository Name: {}".format(repo_name))
                    print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.federated[repo_name]["filesCount"], self.rt1.federated[repo_name]["usedSpace"]))
                    print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.federated[repo_name]["filesCount"], self.rt2.federated[repo_name]["usedSpace"]))

    def repo_content_diff(self, repo_name):
        r1_content = self.rt1.get_repo_content(repo_name)
        r2_content = self.rt2.get_repo_content(repo_name)
        paths_one = []
        paths_two = []

        for result in r1_content:
            path = result['path'] + "/" + result['name']  # put the repo and path of each image in a tuple
            paths_one.append(path)  # put them all on a list

        for result in r2_content:
            path = result['path'] + "/" + result['name']  # put the repo and path of each image in a tuple
            paths_two.append(path)  # put them all on a list

        one_missing = list(set(paths_one) - set(paths_two))
        two_missing = list(set(paths_two) - set(paths_one))

        return one_missing, two_missing

    def do_full_file_diff(self):
        print("************")
        print("Checking local repositories in common for full file diff")
        for repo_name in self.common_repos():
            if repo_name in self.rt1.local.keys():
                print("************")
                print("Repository Name: {}".format(repo_name))
                print("Instance {}: {} files, {} used".format(self.rt1.name, self.rt1.local[repo_name]["filesCount"], self.rt1.local[repo_name]["usedSpace"]))
                print("Instance {}: {} files, {} used".format(self.rt2.name, self.rt2.local[repo_name]["filesCount"], self.rt2.local[repo_name]["usedSpace"]))
                one_missing, two_missing = self.repo_content_diff(repo_name)
                print("Instance {} is missing artifacts {}".format(self.rt1.name, one_missing))
                print("Instance {} is missing artifacts {}".format(self.rt2.name, two_missing))

    def create_missing_federated(self, include_target=True, repo_filter=False):

        print("Creating missing repositories for", self.rt2.name)
        for repo_name in self.rt1.federated.keys():
            if repo_filter:
                if repo_name not in repos_to_do:
                    continue
            if repo_name not in SYSTEM_REPOS and repo_name not in self.rt2.federated.keys():

                repo = self.rt1.federated[repo_name]
                if include_target:
                    repo["members"] = [{"url": self.rt1.url + "/artifactory/" + repo_name, "enabled": "true"}]
                else:
                    repo["members"] = []
                headers = {'content-type': 'application/json',}
                repo["rclass"] = "federated"
                resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

        print("Creating missing repositories for", self.rt1.name)
        for repo_name in self.rt2.federated.keys():
            if repo_name not in SYSTEM_REPOS and repo_name not in self.rt1.federated.keys():

                repo = self.rt2.federated[repo_name]
                if include_target:
                    repo["members"] = [{"url": self.rt2.url + "/artifactory/" + repo_name, "enabled": "true"}]
                else:
                    repo["members"] = []
                repo["rclass"] = "federated"
                headers = {'content-type': 'application/json',}

                resp = requests.put(self.rt1.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt1.auth, headers=headers)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

    def create_missing_federated_on_target(self, include_target=True):
        error_file = open('./create_federated_errors.log', 'w')
        success_file = open('./create_federated_success.log', 'w')
        print("Creating missing repositories for", self.rt2.name)
        for repo_name in self.rt1.federated_configs.keys():
            if repo_name not in SYSTEM_REPOS and repo_name not in self.rt2.federated_configs.keys():
                repo = self.rt1.federated_configs[repo_name]
                if include_target:
                    repo["members"] = [{"url": self.rt1.url + "/" + repo_name, "enabled": "true"}]
                else:
                    repo["members"] = []
                headers = {'content-type': 'application/json',}
                repo["rclass"] = "federated"
                resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code != 200:
                    print("Non-200 response:", resp.status_code)
                    print(resp.text)
                    error_file.write(repo_name)
                    error_file.write(" | ")
                    error_file.write(resp.text)
                    error_file.write('\n')
                else:
                    print("Success for", repo_name)
                    success_file.write(resp.text)
                    success_file.write('\n')

    def create_missing_remotes_on_target(self):
        print("Creating missing remote repositories for", self.rt2.name)
        error_file = open('./create_remote_errors.log', 'w')
        success_file = open('./create_remote_success.log', 'w')
        for repo_name in self.rt1.remote_configs.keys():
            if repo_name not in SYSTEM_REPOS and repo_name not in self.rt2.remote_configs.keys():
                repo = self.rt1.remote_configs[repo_name]
                print(repo_name)

                headers = {'content-type': 'application/json', }
                repo["rclass"] = "remote"
                repo["password"] = ""
                repo["dockerApiVersion"] = "V2"
                resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code != 200:
                    print("Non-200 response:", resp.status_code)
                    print(resp.text)
                    error_file.write(repo_name)
                    error_file.write(" | ")
                    error_file.write(resp.text)
                    error_file.write('\n')
                else:
                    print("Success for", repo_name)
                    success_file.write(resp.text)
                    success_file.write('\n')

    def create_missing_virtual_on_target(self):

        print("Creating missing virtual repositories for", self.rt2.name)

        mvr1, mvr2 = self.missing_virtual()
        retry = []
        error_file = open('./create_virtual_errors.log', 'w')
        success_file = open('./create_virtual_success.log', 'w')

        for repo in self.rt1.repository_configurations['VIRTUAL']:
            repo_name = repo["key"]
            if repo_name not in SYSTEM_REPOS and repo_name in mvr1:
                #print(self.rt1.url + "/artifactory/api/repositories/" + repo_name)

                repo = requests.get(self.rt1.url + "/artifactory/api/repositories/" + repo_name, auth=self.rt1.auth)
                repo = repo.json()
                headers = {'content-type': 'application/json', }
                repo["rclass"] = "virtual"
                resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code != 200:
                    print("Adding {} to retry queue. Non-200 response: {}".format(repo_name, resp.status_code))
                    print(resp.text)
                    retry.append(repo)
                else:
                    print("Success for", repo_name)
                    success_file.write(resp.text)
                    success_file.write('\n')

        for repo in retry:
            repo_name = repo["key"]
            print("Retrying repo", repo_name)
            headers = {'content-type': 'application/json', }
            resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                auth=self.rt2.auth, headers=headers)
            if resp.status_code != 200:
                print("Failure on retry for {}. Non-200 response: {}".format(repo_name, resp.status_code))
                error_file.write(repo_name)
                error_file.write(" | ")
                error_file.write(resp.text)
                error_file.write('\n')
            else:
                print("Success on retry for", repo_name)
                success_file.write(resp.text)
                success_file.write('\n')

    def update_federated_members(self, repo_filter=False):
        print("Updating member repositories for", self.rt1.name)
        for repo_name in self.rt1.federated.keys():
            if repo_filter:
                if repo_name not in repos_to_do:
                    continue


            if repo_name not in SYSTEM_REPOS:

                repo = self.rt1.federated[repo_name]
                repo["members"] = [{"url": self.rt2.url + "/" + repo_name, "enabled": "true"}]
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt1.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt1.auth, headers=headers)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

        print("Updating member repositories for", self.rt2.name)
        for repo_name in self.rt2.federated.keys():
            if repo_name not in SYSTEM_REPOS:

                repo = self.rt2.federated[repo_name]
                repo["members"] = [{"url": self.rt1.url + "/" + repo_name, "enabled": "true"}]
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code != 201:
                    print("Non-201 response:", resp.status_code)
                    print(resp.text)
                else:
                    print("success")

    def refresh_storage_summary(self):
        print("Refreshing storage summary for", self.rt1.name)
        self.rt1.refresh_storage_summary()
        print("Refreshing storage summary for", self.rt2.name)
        self.rt2.refresh_storage_summary()

    def federate_one(self, repo_name):
        repo = self.rt1.federated[repo_name]
        repo["members"] = [{"url": self.rt1.url + "/" + repo_name, "enabled": "true"}]
        headers = {'content-type': 'application/json', }
        repo["rclass"] = "federated"
        print("Creating repo in target")
        resp = requests.put(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                            auth=self.rt2.auth, headers=headers)
        if resp.status_code != 201:
            print("Non-201 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Updating repo in source")
        repo = self.rt1.federated[repo_name]
        repo["members"] = [{"url": self.rt2.url + "/" + repo_name, "enabled": "true"}]
        headers = {'content-type': 'application/json', }
        resp = requests.post(self.rt1.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                            auth=self.rt1.auth, headers=headers)
        if resp.status_code != 201:
            print("Non-201 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Triggering Configuration Sync on source")
        r = requests.post(self.rt1.url + "/artifactory/api/federation/configSync/{}".format( repo["repoKey"]), auth=self.rt1.auth, verify=False)
        if resp.status_code != 200:
            print("Non-200 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

        print("Triggering Full Sync on source")
        r = requests.post(self.rt1.url + "/artifactory/api/federation/fullSync/{}".format( repo["repoKey"]), auth=self.rt1.auth, verify=False)
        if resp.status_code != 200:
            print("Non-200 response:", resp.status_code)
            print(resp.text)
        else:
            print("success")

    def federate_all(self, repo_filter=False):
        for repo_name in self.rt1.federated.keys():
            if repo_filter:
                if repo_name not in repos_to_do:
                    continue

            if repo_name not in SYSTEM_REPOS:
                self.federate_one(repo_name)

    def update_virtual_members(self, dry=False):
        for repo in self.rt1.repository_configurations['VIRTUAL']:
            repo_name = repo["key"]
            repo_refs = repo["repositories"]

            resp = requests.get(self.rt2.url + "/artifactory/api/repositories/" + repo_name, auth=self.rt2.auth)

            if resp.status_code >= 400:
                print("Repo {} does not exist in target.".format(repo_name))
                continue

            target_repo = resp.json()
            try:
                target_repo_refs = target_repo["repositories"]
            except Exception as e:
                print(e)
                print(target_repo)
                sys.exit()

            repo_refs = sorted(repo_refs)
            target_repo_refs = sorted(target_repo_refs)

            if repo_refs != target_repo_refs:
                print("Found non equal members for repo {}".format(repo_name))
                print(repo_refs)
                print(target_repo_refs)

                if not dry:
                    headers = {'content-type': 'application/json', }
                    repo["rclass"] = "virtual"
                    resp = requests.post(self.rt2.url + "/artifactory/api/repositories/" + repo_name, json=repo,
                                        auth=self.rt2.auth, headers=headers)
                    if resp.status_code != 200:
                        print("Failed to update virtual repository {}. Non-200 response: {}".format(repo_name,
                                                                                                    resp.status_code))
                        print(resp.text)
                    else:
                        print("Success updating members for", repo_name)
            else:
                print("Members the same for repo {}".format(repo_name))

    # Xray stuff
    def update_all_xray_data(self):
        self.rt1.load_xray_data()
        self.rt2.load_xray_data()

    def report_watches_policies(self):

        self.update_all_xray_data()

        print("Doing", len(self.rt1.xray_policies), "policies.")
        for policy in self.rt1.xray_policies:
            policy_name = policy["name"]
            rt2_policy = requests.get(self.rt2.url + "/xray/api/v2/policies/" + policy_name, auth=self.rt2.auth,
                                      verify=False)
            if rt2_policy.status_code == 404:
                print("Policy", policy_name, "doesn't exist in target Artifactory")
            elif rt2_policy.status_code == 200:
                # The policy may still be different (author, creation date, and modification date will
                target_policy = rt2_policy.json()
                if target_policy["rules"] == policy["rules"]:
                    # Rules are the same
                    try:
                        if target_policy["description"] == policy["description"]:
                            print("Policy", policy_name, "already exists. They are the same")
                        else:
                            print("Policy", policy_name, "already exists. Descriptions are not the same, needs updating.")
                    except KeyError:
                        # Sometimes there is no description. that's fine.
                        print("Policy", policy_name, "already exists. They are the same")
                else:
                    print("Policy", policy_name, "already exists. Rules are the not same, needs updating.")

            else:
                print("Error for policy", policy_name, "unexpected status code", rt2_policy.status_code)

        print("Doing", len(self.rt1.xray_watches), "watches.")
        for watch in self.rt1.xray_watches:
            watch_name = watch["general_data"]["name"]
            rt2_watch = requests.get(self.rt2.url + "/xray/api/v2/watches/" + watch_name, auth=self.rt2.auth, verify=False)
            if rt2_watch.status_code == 404:
                print("Watch", watch_name,  "doesn't exist in target Artifactory")

            elif rt2_watch.status_code == 200:
                target_watch = rt2_watch.json()
                is_diff = False
                try:
                    target_res = []
                    for i in target_watch["project_resources"]["resources"]:
                        target_res.append(i["name"])

                    source_res = []
                    for i in watch["project_resources"]["resources"]:
                        source_res.append(i["name"])

                    target_res = set(target_res)
                    source_res = set(source_res)
                    diff = source_res-target_res

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_watch["assigned_policies"] != watch["assigned_policies"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_watch["watch_recipients"] != watch["watch_recipients"]:
                        is_diff = True
                except KeyError:
                    pass

                if is_diff:
                    print("Watch", watch_name, "already exists, but it's not the same. Needs update.")
                else:
                    print("Watch", watch_name, "already exists.")

            else:
                print("Error for watch", watch_name, "unexpected status code", rt2_watch.status_code)

        print("Doing", len(self.rt1.xray_ignore_rules["data"]), "ignore rules.")

        for rule in self.rt1.xray_ignore_rules["data"]:
            rule_id = rule["id"]
            rt2_rule = requests.get(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, auth=self.rt2.auth,
                                     verify=False)
            if rt2_rule.status_code == 404:
                print("Rule", rule_id, "doesn't exist in target Artifactory")

            elif rt2_rule.status_code == 200:
                target_rule = rt2_rule.json()
                is_diff = False
                try:
                    target_comps = []
                    for i in target_rule["components"]:
                        target_comps.append(i["name"])

                    source_comps = []
                    for i in rule["components"]:
                        source_comps.append(i["name"])

                    target_comps = set(target_comps)
                    source_comps = set(source_comps)
                    diff = source_comps - target_comps

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["licenses"] != rule["licenses"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["watches"] != rule["watches"]:
                        is_diff = True
                except KeyError:
                    pass

                if is_diff:
                    print("Rule", rule_id, "already exists, but it's not the same. Needs update.")
                else:
                    print("Rule", rule_id, "already exists.")

            else:
                print("Error for rule", rule_id, "unexpected status code", rt2_rule.status_code)

    def create_missing_and_update_policies(self):
        self.update_all_xray_data()
        for policy in self.rt1.xray_policies:
            policy_name = policy["name"]
            rt2_policy = requests.get(self.rt2.url + "/xray/api/v2/policies/" + policy_name, auth=self.rt2.auth, verify=False)
            if rt2_policy.status_code == 404:
                print("Policy", policy_name, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v2/policies", json=policy,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code == 200:
                    print(resp.text)
                else:
                    print("Non 200 status code", resp.status_code)
                    print(resp.text)
            elif rt2_policy.status_code == 200:
                # The policy may still be different (author, creation date, and modification date will
                target_policy = rt2_policy.json()
                if target_policy["rules"] == policy["rules"]:
                    # Rules are the same
                    try:
                        if target_policy["description"] == policy["description"]:
                            print("Policy", policy_name, "already exists. They are the same")
                        else:
                            print("Policy", policy_name,
                                  "already exists. Descriptions are not the same, needs updating.")
                            headers = {'content-type': 'application/json', }
                            resp = requests.put(self.rt2.url + "/xray/api/v2/policies/" + policy_name, json=policy,
                                                auth=self.rt2.auth, headers=headers)

                            if resp.status_code == 200:
                                print("Success updating", policy_name)
                            else:
                                print("Non 200 status code while updating", policy_name)
                    except KeyError:
                        # Sometimes there is no description. that's fine.
                        print("Policy", policy_name, "already exists. They are the same")
                else:
                    print("Policy", policy_name, "already exists. Rules are the not same, needs updating.")
                    headers = {'content-type': 'application/json', }
                    resp = requests.put(self.rt2.url + "/xray/api/v2/policies/" + policy_name, json=policy,
                                         auth=self.rt2.auth, headers=headers)

                    if resp.status_code == 200:
                        print("Success updating", policy_name)
                    else:
                        print("Non 200 status code", resp.status_code ,"while updating", policy_name)

            else:
                print("Error for policy", policy_name, "unexpected status code", rt2_policy.status_code)

    def create_missing_and_update_watches(self):
        self.update_all_xray_data()
        for watch in self.rt1.xray_watches:
            watch_name = watch["general_data"]["name"]
            rt2_watch = requests.get(self.rt2.url + "/xray/api/v2/watches/" + watch_name, auth=self.rt2.auth, verify=False)
            if rt2_watch.status_code == 404:
                print("Watch", watch_name, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v2/watches", json=watch,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code == 201:
                    print(resp.text)
                else:
                    print("Non 201 status code", resp.status_code)
                    print(resp.text)
            elif rt2_watch.status_code == 200:
                target_watch = rt2_watch.json()
                is_different = False

                try:
                    target_res = []
                    for i in target_watch["project_resources"]["resources"]:
                        target_res.append(i["name"])

                    source_res = []
                    for i in watch["project_resources"]["resources"]:
                        source_res.append(i["name"])

                    target_res = set(target_res)
                    source_res = set(source_res)
                    diff = source_res-target_res

                    if len(diff) != 0:
                        is_different = True

                except KeyError:
                    pass

                try:
                    if target_watch["watch_recipients"] != watch["watch_recipients"]:
                        is_different = True
                except KeyError:
                    # print("No watch recipients")
                    pass
                try:
                    if target_watch["assigned_policies"] != watch["assigned_policies"]:
                        is_different = True
                except KeyError:
                    pass
                    # print("No assigned policies")

                if is_different:
                    print("Watch", watch_name, "already exists, but it's not the same. Needs update.")
                    headers = {'content-type': 'application/json', }
                    resp = requests.put(self.rt2.url + "/xray/api/v2/watches/" + watch_name, json=watch,
                                        auth=self.rt2.auth, headers=headers)
                    if resp.status_code == 200:
                        print("Success updating", watch_name)
                    else:
                        print("Non 200 status code", resp.status_code, "while updating", watch_name)
                else:
                    print("Watch", watch_name, "already exists.")

            else:
                print("Error for watch", watch_name, "unexpected status code", rt2_watch.status_code)

    def create_missing_and_update_ignore_rules(self):
        self.update_all_xray_data()
        for rule in self.rt1.xray_ignore_rules["data"]:
            rule_id = rule["id"]
            rt2_rule = requests.get(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, auth=self.rt2.auth,
                                    verify=False)
            if rt2_rule.status_code == 404:
                print("Ignore Rule", rule_id, "doesn't exist in target Artifactory, need to create.")
                headers = {'content-type': 'application/json', }
                resp = requests.post(self.rt2.url + "/xray/api/v1/ignore_rules", json=rule,
                                    auth=self.rt2.auth, headers=headers)
                if resp.status_code == 201:
                    print("Success creating", rule_id)
                else:
                    print("Non 201 status code", resp.status_code,  "for Ignore Rule", rule_id)
                    print(resp.text)
            elif rt2_rule.status_code == 200:
                target_rule = rt2_rule.json()
                is_diff = False
                try:
                    target_comps = []
                    for i in target_rule["components"]:
                        target_comps.append(i["name"])

                    source_comps = []
                    for i in rule["components"]:
                        source_comps.append(i["name"])

                    target_comps = set(target_comps)
                    source_comps = set(source_comps)
                    diff = source_comps - target_comps

                    if len(diff) != 0:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["licenses"] != rule["licenses"]:
                        is_diff = True
                except KeyError:
                    pass
                try:
                    if target_rule["watches"] != rule["watches"]:
                        is_diff = True
                except KeyError:
                    pass
                    # print("No assigned policies")

                if is_diff:
                    print("Ignore Rule", rule_id, "already exists, but it's not the same. Needs update.")
                    headers = {'content-type': 'application/json', }
                    print("Deleting Ignore Rule in Target:", rule_id)
                    resp = requests.delete(self.rt2.url + "/xray/api/v1/ignore_rules/" + rule_id, json=rule,
                                        auth=self.rt2.auth, headers=headers)
                    if resp.status_code == 204:
                        print("Success udeleting", rule_id)
                    else:
                        print("Non 200 status code", resp.status_code, "while deleting", rule_id)
                    print("Creating Ignore Rule in Target:", rule_id)
                    headers = {'content-type': 'application/json', }
                    resp = requests.post(self.rt2.url + "/xray/api/v1/ignore_rules", json=rule,
                                         auth=self.rt2.auth, headers=headers)
                    if resp.status_code == 201:
                        print("Success creating", rule_id)
                    else:
                        print("Non 201 status code", resp.status_code, "for Ignore Rule", rule_id)
                        print(resp.text)

                else:
                    print("Ignore Rule", rule_id, "already exists.")

            else:
                print("Error for Ignore Rule", rule_id, "unexpected status code", rt2_rule.status_code)


def main():
    if len(sys.argv) < 6:
       print("Usage: python repo_sync.py https://url_source https://url_target user token <command>")
       sys.exit()
    url_source = sys.argv[1]
    url_target = sys.argv[2]

    _auth = (sys.argv[3], sys.argv[4])
    # Initialize the objects that help us interact
    source = Artifactory(url_source, _auth, "source")
    target = Artifactory(url_target, _auth, "target")
    helper = FederationHelper(source, target)

    command = sys.argv[5]

    # Print out the repo diff
    if command == "report":
        helper.repo_report()

    # This prints the remote repos that have password
    if command == "remotes_with_password_source":
        source.print_remotes_with_password()

    if command == "remotes_with_password_target":
        target.print_remotes_with_password()

    # Refresh storage summary page
    if command == "refresh_storage_summary":
        helper.refresh_storage_summary()

    # Transform all local repos to federated
    # art1.transform_local_to_federated()
    # art2.transform_local_to_federated()

    # Push federated repo configs
    # helper.federate_all() # If you don't pass the flag it will do all repos


    # Create Missing federated repos
    if command == "create_missing_federated_on_target":
        helper.create_missing_federated_on_target()

    # Create missing remote repositories
    if command == "create_missing_remotes_on_target":
        helper.create_missing_remotes_on_target()

    # Create Missing virtual repositories
    if command == "create_missing_virtual_on_target":
        helper.create_missing_virtual_on_target()

    # Update virtual repo members
    if command == "update_virtual_members":
        helper.update_virtual_members()
    if command == "update_virtual_members_dry":
        helper.update_virtual_members(dry=True)

    # Xray commands
    if command == "xray_report":
        helper.report_watches_policies()
    if command == "sync_xray_policies":
        helper.create_missing_and_update_policies()
    if command == "sync_xray_watches":
        helper.create_missing_and_update_watches()
    if command == "sync_xray_ignore_rules":
        helper.create_missing_and_update_ignore_rules()

if __name__ == '__main__':
    main()