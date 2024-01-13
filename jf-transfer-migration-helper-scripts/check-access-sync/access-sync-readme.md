When using E+ license you can setup access federation and check if access star sync ( of users, groups, permissions) is complete from source to target Artifactory.

Note: If the customer's email domain will change then don't care about the Access tokens sync  ( as the JWT access tokens will have the old email domain )

Always make sure the jfrog default "admin" user (and any customer specifc admin users in the source RT) is present in the target RT as well and preferably has the same password.
Configure the jf with same  admin user ( not necessary to be the same as the default "admin" user) to connect to both the source and target RT.

1. Do the following checks on the Source and Target user  list 

The outout of /api/security/users will be a json containing a list of users:

```
, {
  "name" : "jp250606@ncr.com",
  "uri" : "https://ncr.jfrog.io/artifactory/api/security/users/jp250606@ncr.com",
  "realm" : "internal"
}, {
  "name" : "as185823@ncr.com",
  "uri" : "https://ncr.jfrog.io/artifactory/api/security/users/as185823@ncr.com",
  "realm" : "saml"
}
```

From this extract the user "name" ( which has the domain) 
```
jf rt curl /api/security/users | jq -r '.[] | .name' >> ncr/users.list
Sort the contents:
sort -o ncr/users.list ncr/users.list
```
---

Based on the user email address how to find out unique email domains in the ncr/users.list file ?
```
awk -F '@' '{print $2}' ncr/users.list | sort -u
```

Example output:
```
corp.ncr.com
jfrog.com
ncr.com
ncratmco.com
```
---

If you also want to count the occurrences of each domain, you can use uniq -c:
```
awk -F '@' '{print $2}' ncr/users.list | sort | uniq -c
```
Example output:
```
 119
 137 corp.ncr.com
   3 jfrog.com
5027 ncr.com
   1 ncratmco.com
```

---

2. If you have  to change the user domains from @ncr.com to @ncratleos.com the PE team will export and share the access.bootstrap.json as mentioned in the  
[Access import/export](https://docs.google.com/document/d/1n6F1nfCfwJPlR2FlGXeqWTwYFabAZMHiKjRnpPnQ6wk/edit#heading=h.35mueprt0t2o) document.
Make the domain chages for the users as requested by customer using the [modifyAccess.sh](https://github.com/shivaraman83/security-entities-migration/blob/main/access-modifications/modifyAccess.sh)  script.

Verify the changes usinng:
```
jf rt curl /api/security/users | jq -r '.[] | .name' >> ncratleostest/users_after_domain_fix.list
sort -o ncratleostest/users_after_domain_fix.list ncratleostest/users_after_domain_fix.list
awk -F '@' '{print $2}' ncratleostest/users_after_domain_fix.list | sort | uniq -c
```
Example output:
```
 119
 137 corp.ncr.com
   3 jfrog.com
5027 ncratleos.com
   1 ncratmco.com
```

---
3. Diff the groups:
Compare groups between ncr and ncratleostest

Source ncr:
```
jf c use ncr
jf rt curl /api/security/groups | jq -r '.[] | .name'>> ncr/groups.list
Sort the contents:
sort -o ncr/groups.list ncr/groups.list
```

Target ncratleostest:
```
jf c use ncratleostest
jf rt curl /api/security/groups | jq -r '.[] | .name' >> ncratleostest/groups.list
sort -o ncratleostest/groups.list ncratleostest/groups.list
```

---

3. Diff the permissions:
Source ncr:
```
jf c use ncr
jf rt curl /api/security/permissions | jq -r '.[] | .name'>> ncr/permissions.list
sort -o ncr/permissions.list ncr/permissions.list
```

Target ncratleostest:
```
jf c use ncratleostest
jf rt curl /api/security/permissions | jq -r '.[] | .name' >> ncratleostest/permissions.list
sort -o ncratleostest/permissions.list ncratleostest/permissions.list
```


Compare permissions between ncr and ncratleostest
```
comm -13 ncratleostest/permissions.list ncr/permissions.list  > ncratleostest/permissions_not_synced_yet.txt
```
Note: comm is preferable over diff in macos

---
4. No need to diff the tokens as the JWT access tokens will have the old email domain and will be invalid anyway.

If the user domain is same in source and target the you could diff the tokens  as well.

Source ncr:
```
jf c use ncr
curl -H "Authorization: Bearer  $MYTOKEN"  -XGET "https://ncr.jfrog.io/access/api/v1/tokens"  | jq -r '.tokens[] | .token_id'  >> ncr/token.list
sort -o ncr/token.list ncr/token.list
```

Target ncratleostest
```
jf c use ncratleostest
curl -H "Authorization: Bearer  $MYTOKEN"  -XGET "https://ncratleostest.jfrog.io/access/api/v1/tokens"  | jq -r '.tokens[] | .token_id'  >> ncratleostest/token.list
sort -o ncratleostest/token.list ncratleostest/token.list
```

---

5. Give  the modifed  access.bootstrap.json back to the PE team as mentioned in the document , so PE team can import it in the target instance.

Note: If these domain changes are not needed we could have done Access Federation in star mode to sync Access from source to target Artifactory.

```
sed -i.bak 's/@ncr.com/@ncratleos.com/g' access.bootstrap_b4_domain_change.json
mv access.bootstrap_b4_domain_change.json access.bootstrap_after_domain_change.json
```


There are some more steps to encrypt the `access.bootstrap_after_domain_change.json` and rename to `access.bootstrap.json` as  mentioned in the [Access import/export](https://docs.google.com/document/d/1n6F1nfCfwJPlR2FlGXeqWTwYFabAZMHiKjRnpPnQ6wk/edit#heading=h.35mueprt0t2o) document, so that the PE team can use it.

--- 

