import requests
import subprocess
import json
from requests.auth import HTTPBasicAuth

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SOURCE_JPD_URL="https://psemea.jfrog.io"
JPD_USERNAME="ramkannans"
JPD_TOKEN="****"

# Get all remote repositories
response = requests.get(SOURCE_JPD_URL+ "/artifactory/api/repositories?type=remote", auth=HTTPBasicAuth(JPD_USERNAME, JPD_TOKEN))
data=response.json()
print(json.dumps(data, indent=4))

for i in data:
    remoterepo= i["key"]
    packagetype = i["packageType"]
    # add cache to remote repository to get cache repository
    remotecache=remoterepo+"-cache"
    # add local to remote repository to get local repository
    localrepo=remoterepo+"-local"
    print("remote repository : " + remoterepo)
    print("remote cache repository : " + remotecache)
    print("local repository : " + localrepo)

    # check if local repo is available
    response = requests.get(SOURCE_JPD_URL+ "/artifactory/api/repositories/"+ localrepo, auth=HTTPBasicAuth(JPD_USERNAME, JPD_TOKEN))
    if (response.status_code==200):
        print("local repository exists")
        p = subprocess.Popen('jf rt cp '+ remotecache +"/ " + localrepo+"/" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print(line)
        
    else:
        # create local repository
        print(response.status_code)
        data = { 
                "key": localrepo, 
                "rclass": "local", 
                "packageType": packagetype, 
                "description": "", 
                "checksumPolicyType": "client-checksums"
                }

        response = requests.put(SOURCE_JPD_URL+ "/artifactory/api/repositories/"+ localrepo, json=data,  auth=HTTPBasicAuth(JPD_USERNAME, JPD_TOKEN))
        if(response.status_code== 200):
          print("repository created" + localrepo )
          p = subprocess.Popen('jf rt cp '+ remotecache +"/ " + localrepo+"/" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          for line in p.stdout.readlines():
            print(line)
        else:
          print("unable to create local repo, status code : " + response.status_code)