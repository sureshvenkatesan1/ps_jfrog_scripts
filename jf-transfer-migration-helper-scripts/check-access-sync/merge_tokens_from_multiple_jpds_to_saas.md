
## Steps to merge the tokens from different JPDS to a single target SAAS JPD:
The following steps show how to migrate the tokens from multiple JPDs (without using access federation) i.e using the 
internal /access/api/v1/import/entities/cloud API as mentioned in https://git.jfrog.info/projects/PROFS/repos/usingjfrogcli/browse/Access/test_Access_federation.md

1. cd to the folder containing the tokens from UA and DOQ JPDs that you want to merge to the https://example.jfrog.io 
target SAAS JPD.

2. Extract only the "version" and "tokens" from the 3 JPDs ( UA, DOQ, and SAAS) :
```
python extract_version_and_tokens.py UA-access.backup.20240221125844.json
python extract_version_and_tokens.py DOQ_access.backup.20240221141536.json
python extract_version_and_tokens.py access.backup.20240221223922.json
```

3. As per [How to import access data?](https://jfrog.com/help/r/how-to-import-access-data/subject)  and 
[#173103](https://groups.google.com/a/jfrog.com/g/support-followup/c/f5kePgMUFKY/m/4x2psDOEAAAJ) and
[#244681](https://groups.google.com/a/jfrog.com/g/support-followup/c/J7Z6iPGBoig/m/bJU0-rS-DgAJ) get the 
   Artifactory i.e jfrt    service_id of  the target SAAS JPD.
``` 
curl -uadmin:password -XGET "http://localhost:8081/artifactory/api/system/service_id" 
```
Output:
jfrt@01hbgzkk2aa7h50j9eqctj1fvb

Since this API needs  admin credentials we found that the Artifactory i.e jfrt   service_id can also be got 
using the following API which does not need any credentials:
```text
curl -s -XGET https://bellca.jfrog.io/router/api/v1/system/health | jq -r '.services[] | select(.service_id | startswith("jfrt@")) | .service_id'
```
4. Get the unique jfrt or jf-artifactory token IDs:
```
python get_unique_jfrt_ids.py UA-access.backup.20240221125844_modified.json
```
Output:
Unique IDs for 'jf-artifactory@': set()
Unique IDs for 'jfrt@': {'01fm5ctjzk74130d2m6cc017bq'}

5. Change all the token IDs to the jfrt service_id of the target SAAS JPD:
Run:
```
sed -i '' 's/jfrt@01fm5ctjzk74130d2m6cc017bq/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/g' UA-access.backup.20240221125844_modified.json
```

6. Similarly do the cleanup for other JDP tokens:
```
python get_unique_jfrt_ids.py DOQ_access.backup.20240221141536_modified.json

Output:
Unique IDs for 'jf-artifactory@': {'3f51f108-4fb5-4bfe-90f8-0016af988168'}
Unique IDs for 'jfrt@': set()

Run:
sed -i '' 's/jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/g' DOQ_access.backup.20240221141536_modified.json
python get_unique_jfrt_ids.py DOQ_access.backup.20240221141536_modified.json

Output:
Unique IDs for 'jf-artifactory@': set()
Unique IDs for 'jfrt@': {'01hbgzkk2aa7h50j9eqctj1fvb'}

python get_unique_jfrt_ids.py access.backup.20240221223922_modified.json
Output:
Unique IDs for 'jf-artifactory@': {'3f51f108-4fb5-4bfe-90f8-0016af988168'}
Unique IDs for 'jfrt@': {'01hbgzkk2aa7h50j9eqctj1fvb', '01fm5ctjzk74130d2m6cc017bq'}

Run:
sed -i '' 's/jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/g' access.backup.20240221223922_modified.json
sed -i '' 's/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/g' access.backup.20240221223922_modified.json
sed -i '' 's/jfrt@01fm5ctjzk74130d2m6cc017bq/jfrt@01hbgzkk2aa7h50j9eqctj1fvb/g' access.backup.20240221223922_modified.json
python get_unique_jfrt_ids.py access.backup.20240221223922_modified.json

Output:
Unique IDs for 'jf-artifactory@': set()
Unique IDs for 'jfrt@': {'01hbgzkk2aa7h50j9eqctj1fvb'}
```

7. Get the number of unique token IDs in each JSON file using jq, you can use the following command:
```
jq '.tokens | map(.id) | unique | length' UA-access.backup.20240221125844_modified.json
Output: 2523

jq '.tokens | map(.id) | unique | length' DOQ_access.backup.20240221141536_modified.json
Output: 1138
```

8. Merge the UA and DOQ tokens:
```
python merge_tokens.py UA-access.backup.20240221125844_modified.json DOQ_access.backup.20240221141536_modified.json UA-DOQ-combined.json

jq '.tokens | map(.id) | unique | length' UA-DOQ-combined.json
```
UA-DOQ-combined.json has exactly 2523 + 1138 = 3661 tokens

```
python get_unique_jfrt_ids.py UA-DOQ-combined.json
Output:
Unique IDs for 'jf-artifactory@': set()
Unique IDs for 'jfrt@': {'01hbgzkk2aa7h50j9eqctj1fvb'}

jq '.tokens | map(.id) | unique | length' access.backup.20240221223922_modified.json
Output: 2733
```

9. Now merge the access.backup.20240221223922_modified.json and UA-DOQ-combined.json :
```
python merge_tokens.py access.backup.20240221223922_modified.json UA-DOQ-combined.json final_tokens_to_import.json


jq '.tokens | map(.id) | unique | length' final_tokens_to_import.json
Output: 4119

python get_unique_jfrt_ids.py final_tokens_to_import.json
Output:
Unique IDs for 'jf-artifactory@': set()
Unique IDs for 'jfrt@': {'01hbgzkk2aa7h50j9eqctj1fvb'}
```

10. Now log a support ticket to ask the PE team  to use the `service admin token` to import the final_tokens_to_import.
json into the target SAAS JPD to replace all the existing tokens in  SAAS  

**Note:** The  `service admin token` is an internal token used for JFrog internal services communication. Even and admin user cannot create that.
SAAS Production team knows how to create this for saas instance
```
curl --verbose "http://localhost:8082/access/api/v1/import/entities/cloud" -XPOST -H "Authorization: Bearer  $MYTOKEN" -H "Content-Type: application/json" -d @final_tokens_to_import.json
```
Note: This API is available even in Self Hosted Artifactory.

---

### How many unique  tokens id are in each access json export   file ?
To count the number of unique token IDs in each JSON file using jq, you can use the following command:
```
jq '.tokens | map(.id) | unique | length' access.backup.20240221223922.json
```
Output:
2733

---

I have 2 json files access.backup.20240221223922.json ( from SAAS) and  UA-DOQ-combined-tokens-022124.json ( from 
the 2 SH JPDs) with following format.
```text
{
    "version": "15",
    "tokens": [
        {
            "id": "695732f2-ed68-4efa-8450-230e2de6ad76",
            "subject": "jfac@01fm5ct2g44mdv14jcrp931ra5/users/fidappwnodiua"
        },
        {
            "id": "695732f2-ed68-4efa-8450-230e2de6ad98",
            "subject": "jfac@01fm5ct2g44mdv14jcrp931ra5/users/fidappwnodiua"
        }
    ]
}
```
### How to take the tokens in UA-DOQ-combined-tokens-022124.json and merge them into access.backup.20240221223922.json ?

You can use :
```text
python merge_tokens.py access.backup.20240221223922.json UA-DOQ-combined-tokens-022124.json final_tokens.json
```
---

### How to compare 2 json files to validate that they have  the same token ids ?
```text
python compare_token_ids_in_json_files.py  final_tokens.json merge.json
```
If both files have the same token "ids" you wil get the following output:
```text
Both JSON files have the same token IDs.
```

---
### How to deep compare the  matching tokens ( those with same token  "id") in 2 json files to verify if any other attributes are different  ?
```text
python compare_full_token_in_json_files.py  final_tokens.json merge.json
```

I found 1438 tokens with matching "ids" but in 7.49.8 the token has the subject , owner, issuer with prefix as `jfrt`
but in SAAS the same token has the prefix as `jf-artifactory` as shown below:
```text
Token ID: a3ae78f9-f9cf-48cb-ac90-2eb950fdd456
Difference in file 1:
{
    "id": "a3ae78f9-f9cf-48cb-ac90-2eb950fdd456",
    "subject": "jfrt@01hbgzkk2aa7h50j9eqctj1fvbifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
    "owner": "jfrt@01hbgzkk2aa7h50j9eqctj1fvbifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
    "created": 1708537121564,
    "scope": "HASHED:2efa80ebed31aa0b7c67ed...",
    "type": "generic",
    "username": "fidsainventory_cicd",
    "description": "",
    "payload": {
        "kid": "7ygXgF-8YliIL73NjiyEhKqUdURjqUx5vht89-Hq-Iw",
        "tokenId": "a3ae78f9-f9cf-48cb-ac90-2eb950fdd456",
        "subject": "jfrt@01hbgzkk2aa7h50j9eqctj1fvbifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
        "scope": "member-of-groups:*",
        "audience": "jfrt@01hbgzkk2aa7h50j9eqctj1fvbifactory@3f51f108-4fb5-4bfe-90f8-0016af988168",
        "extension": null,
        "version": "2",
        "expiry": 3600,
        "issuer": "jfrt@01hbgzkk2aa7h50j9eqctj1fvbifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
        "issuedAt": 1708537121564
    },
    "hashedReference": null,
    "expiry": 1708540721564,
    "refreshToken": "c2a25d55e4f31dc5e337761...",
    "persistent": true
}
Difference in file 2:
{
    "id": "a3ae78f9-f9cf-48cb-ac90-2eb950fdd456",
    "subject": "jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
    "owner": "jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
    "created": 1708537121564,
    "scope": "HASHED:2efa80ebed31aa0b7c67ed46...",
    "type": "generic",
    "username": "fidsainventory_cicd",
    "description": "",
    "payload": {
        "kid": "7ygXgF-8YliIL73NjiyEhKqUdURjqUx5vht89-Hq-Iw",
        "tokenId": "a3ae78f9-f9cf-48cb-ac90-2eb950fdd456",
        "subject": "jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
        "scope": "member-of-groups:*",
        "audience": "jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168",
        "extension": null,
        "version": "2",
        "expiry": 3600,
        "issuer": "jf-artifactory@3f51f108-4fb5-4bfe-90f8-0016af988168/users/fidsainventory_cicd",
        "issuedAt": 1708537121564
    },
    "hashedReference": null,
    "expiry": 1708540721564,
    "refreshToken": "c2a25d55e4f31dc5e337761bee190d88...",
    "persistent": true
}

```

