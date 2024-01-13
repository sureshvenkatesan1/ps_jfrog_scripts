```
grep -i error /root/nohup.out
```

Output:
```
nohup.out:15:04:01 [Debug] Handling errors file: ' /root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/errors/retryable/authentic-maven-snapshots-restored-2-1693435664681-0.json '
nohup.out:15:04:01 [Debug] Done handling errors file: ' /root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/errors/retryable/authentic-maven-snapshots-restored-2-1693435664681-0.json '. Deleting it...
nohup.out:15:04:21 [Debug] Saving split content JSON file to: /root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/delays/authentic-maven-snapshots-restored-1693494241513-0.json.
nohup.out:15:04:21 [Debug] Handling delayed artifacts file: '/root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/delays/authentic-maven-snapshots-restored-1693494241513-0.json'
nohup.out:15:04:21 [Debug] Done handling delayed artifacts file: '/root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/delays/authentic-maven-snapshots-restored-1693494241513-0.json'. Deleting it...
nohup.out:22:08:17 [Debug] write ConnectException: Connection refused to file /root/.jfrog/transfer/repositories/b6accca51b29c632aceee8a64600a3c248ad2ea0/errors/retryable/authentic-maven-snapshots-restored-0-1693432753461-0.json
```


```
grep "Handling folder\|transferring folder"  nohup.out
```
Output:
```
04:32:44 [Debug] [Thread 19] Handling folder: ndce-snapshots/com/ncr/ndce/terminal/ndce-sst-runtime-for-andc50x/2.2.1-M02-SNAPSHOT
04:32:44 [Debug] [Thread 13] Done transferring folder: ndce-snapshots/com/ncr/ndce/terminal/ndce-agent-installer/1.1.1-SNAPSHOT
```


cd ~/.jfrog/transfer/repositories 

find . -type d -name fsg-vsn-maven-releases

find /root/.jfrog/transfer/repositories -type f -iname "fsg-vsn-maven-releases*"

find . -type d -name errors

Example:
```
./79ffba08a1b8b0253658986285063fa9a5b5c601/errors
./b03b6059ffd093b965b2f1ff41ca673ac6d62721/errors
./77e19234b6a7bf1493e344e41cf7c3abadf3ff8a/errors
```

How to find all the file names in any of the subfolders under these folders?
```
find . -type d -name errors | while read -r folder; do
    find "$folder" -type f
done
```


This returns a list of files :
./12ea94e202cdb14332719ca803f315f2e8575e2f/errors/retryable/authentic-docker-public-2-1692585833546-0.json
./2476a1eb47fb95bcd83b51eaa1d52c5f2fca5057/errors/retryable/fin-authentic-eng-distribution-docker-public-2-1693495452160-0.json
./463728b1192a8aaa547eb03732c0c935a28edda0/errors/retryable/fin-authentic-eng-docker-releases-2-1693495706373-0.json
./50b326b5b53826c6ef2bf5bdb3ba8103aca3253a/errors/retryable/fin-authentic-eng-docker-snapshots-2-1693495876432-0.json


These files conatin a "status_code" like:
{
  "errors": [
    {
      "repo": "authentic-docker-public",
      "path": ".jfrog",
      "status": "FAIL",
      "status_code": 404,
      "time": "2023-08-21T02:43:59Z"
    }
  ]
}

I want to find all the distinct "status_code" values in these files.
find . -type d -name errors | while read -r folder; do
    find "$folder" -type f -name "*.json" -exec jq -r '.errors[].status_code' {} + 
done | sort -u
That returns:
404
409
500

I want to find all the "repo" and "path":  entries in the json files which have "status_code" 404

find . -type d -name errors | while read -r folder; do
    find "$folder" -type f -name "*.json" -exec jq -r '.errors | map(select(.status_code == 404)) | .[] | { repo: .repo, path: .path }' {} +
done


In these json files I want to pass a "repo" name and get all the "path" that have errors


repo_name="fsg-th-docker-snapshots"  # Replace this with the desired repo name
find . -type d -name errors | while read -r folder; do
    find "$folder" -type f -name "*.json" -exec jq -r --arg repo "$repo_name" '.errors | map(select(.repo == $repo and .status_code == 404)) | .[].path' {} +
done

Instaed of ".status_code == 404" I want to pass a list of stats codes

repo_name="alaricauthentic-maven-snapshots"  # Replace this with the desired repo name
find /root/.jfrog/transfer/repositories -type d -name errors | while read -r folder; do
    find "$folder" -type f -name "*.json" -exec jq -r --arg repo "$repo_name" '.errors | map(select(.repo == $repo and (.status_code == 404 or .status_code == 409 or .status_code == 500))) | .[].path' {} +
done
