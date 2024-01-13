#!/bin/bash

# Note: REST API calls require JPD version >= 7.49.3

# NOTICE:
# This script only syncs up specified user's configs (ie: group membership & permission target membership) from source JPD (SRC_JPD) to destination JPD (DST_JPD). 

SRC_JPD_URL="${1:?please enter source JPD URL. ex - https://srcjpd.jfrog.io}"
SRC_JPD_AUTH_TOKEN="${2:?Please enter source admin user identity token}"

DST_JPD_URL="${3:?please enter destination JPD URL. ex - https://dstjpd.jfrog.io}"
DST_JPD_AUTH_TOKEN="${4:?Please enter destination admin user identity token}"

USER_LIST_STR="${5:?Please enter user list as comma sepeated string. ex - user1,user2,user3}"
USER_LIST=$(echo $USER_LIST_STR | tr ',' "\n")

DRY_RUN="${6:?Specify if dry run yes/no.}"
DRY_RUN=$(echo $DRY_RUN | tr '[:upper:]' '[:lower:]')

# Ensure DRY_RUN is set to "yes" if not provided or not "yes" or "no"
if [[ -z "$DRY_RUN" || ("$DRY_RUN" != "yes" && "$DRY_RUN" != "no") ]]; then
    DRY_RUN="yes"
fi

echo SRC_JPD_URL: $SRC_JPD_URL
echo DST_JPD_URL: $DST_JPD_URL
echo USER_LIST: $USER_LIST_STR
echo DRY_RUN: $DRY_RUN

DEFAULT_NEW_USER_PASSWORD="ChangeMeN0W!"

# Check if jq tool is available.
if ! command -v jq &> /dev/null
then
    echo "ERROR: jq could not be found. Please install 'jq' tool."
    exit 1
fi


DRY_RUN_ECHO=echo
if [[ "${DRY_RUN}" != *"yes"* ]] ; then
    DRY_RUN_ECHO=
fi
#echo "INFO: DRY_RUN_ECHO=$DRY_RUN_ECHO"

# Function to hide the Authorization token in the output
hide_token() {
    local input=$1
    local output
    output=$(echo "$input" | sed -E 's/(Authorization: Bearer )[^ ]+/\1*** /g')
    echo "$output"
}

# TODO: Validate admin access on SRC_JPD_URL and DST_JPD_URL endpoints.

for user in ${USER_LIST}
do 
    echo
    echo "INFO: Processing user: $user"
    src_status_code=$(curl --write-out '%{http_code}' --output /dev/null -k -s -H"Authorization: Bearer $SRC_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SRC_JPD_URL/artifactory/api/security/users/$user)
    if [[ "$src_status_code" -ne 200 ]] ; then
        echo "INFO: User: $user is not found in source JPD. So skipping. API Response: $src_status_code"
        continue
    fi

    dst_status_code=$(curl --write-out '%{http_code}' --output /dev/null -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $DST_JPD_URL/artifactory/api/security/users/$user)
    if [[ "$dst_status_code" -eq 200 ]] ; then
        echo "INFO: User: $user is found in destination JPD. So skipping. API Response: $dst_status_code"
        # continue
    else
        ### Create new user in the destination JPD. ###
        create_user_json='{"username": "'$user'","password": "'${DEFAULT_NEW_USER_PASSWORD}'","email": "'$user'","admin": false,"profile_updatable": true,"internal_password_disabled": false,"disable_ui_access": false}'
        # TODO: Copy user json values from SRC_JPD_URL and add password entry with default password value.
        dst_user_create_status=$($DRY_RUN_ECHO curl --write-out '%{http_code}' --output /dev/null -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" -XPOST $DST_JPD_URL/access/api/v2/users -d "${create_user_json}")
        if [ -z "$DRY_RUN_ECHO" ]; then
            echo "INFO: Created new user $user in destination JPD. API Response: ${dst_user_create_status}"
        else
            echo "API CALL: $(hide_token "${dst_user_create_status}")"
        fi
    fi

    user_groups=$(curl -k -fs -H"Authorization: Bearer $SRC_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SRC_JPD_URL/artifactory/api/security/users/$user | jq -r -c 'del( .groups[] |  select(. == "readers")) | .groups | join(",")')
    if [ ! -z "$user_groups" ]; then
        echo "INFO: User $user is member of $user_groups group(s)."
        # TODO: Check if groups are present in destination. If present, check and add user to the group. If not, create the group with user.
        user_group_list=$(echo $user_groups | tr ',' "\n")
        for user_group in ${user_group_list}
        do
            echo "INFO: Add group $user_group for user $user"
            src_grp_json=$(curl -k -s -H"Authorization: Bearer $SRC_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SRC_JPD_URL/access/api/v2/groups/$user_group | jq -r -c )
            #echo "DEBUG: src_grp_json = $src_grp_json"
            dst_grp_json=$(curl -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $DST_JPD_URL/access/api/v2/groups/$user_group | jq -r -c )
            #echo "DEBUG: dst_grp_json = $dst_grp_json"

            if [[ "$dst_grp_json" == *"$user_group"* ]] ; then
                echo "INFO: User group $user_group is already present in destination JPD."
            else 
                echo "INFO: User group $user_group is not present in destination JPD."
                ### Create new group and add user to the group in the destination JPD. ###

                create_group_to_user_json=$src_grp_json
                create_group_to_user_json=$(echo $create_group_to_user_json | jq -r -c 'del(.members)')
                dst_create_group_status_code=$($DRY_RUN_ECHO curl --write-out '%{http_code}' --output /dev/null -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" -XPOST $DST_JPD_URL/access/api/v2/groups --data "${create_group_to_user_json}" )
                if [ -z "$DRY_RUN_ECHO" ]; then
                    echo "INFO: Created group $user_group in destination JPD. API Response: ${dst_create_group_status_code}"
                else
                    echo "API CALL: $(hide_token "${dst_create_group_status_code}")"
                fi
            fi
            add_group_to_user_json='{"add": ["'$user_group'"]}'
            dst_add_group_status_code=$($DRY_RUN_ECHO curl --write-out '%{http_code}' --output /dev/null -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" -XPATCH $DST_JPD_URL/access/api/v2/users/$user/groups --data "${add_group_to_user_json}" )
            if [ -z "$DRY_RUN_ECHO" ]; then
                echo "INFO: Added group $user_group for user $user in destination JPD. API Response: ${dst_add_group_status_code}"
            else
                echo "API CALL: $(hide_token "${dst_add_group_status_code}")"
            fi
        done
    fi

    user_perms=$(curl -k -fs -H"Authorization: Bearer $SRC_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SRC_JPD_URL/artifactory/api/v2/security/permissions/users/$user | jq -r -c 'map(select(.name != "Anything")) | map(.name) | join(",")')
    if [ ! -z "$user_perms" ]; then
        echo "INFO: User $user is part of $user_perms permission target(s)."

        user_perm_list=$(echo $user_perms | tr ',' "\n")
        for perm_tgt in ${user_perm_list}
        do
            echo "INFO: Checking permission target: $perm_tgt for user $user"
            src_pt_json=$(curl -k -s -H"Authorization: Bearer $SRC_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $SRC_JPD_URL/artifactory/api/v2/security/permissions/$perm_tgt | jq -r -c )
            #echo "DEBUG: src_pt_json = $src_pt_json"
            dst_pt_json=$(curl -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" $DST_JPD_URL/artifactory/api/v2/security/permissions/$perm_tgt | jq -r -c )
            #echo "DEBUG: dst_pt_json = $dst_pt_json"

            if [[ "$dst_pt_json" == *"$perm_tgt"* ]] ; then
                echo "INFO: Permission target $perm_tgt is already present in destination JPD."
                ### Update existing permission target in the destination JPD. ###

                # TODO: Check if user is part of the perm target in the destination JPD. If not, append to the user list.
                src_pt_repo_user_cfg=$(echo $src_pt_json | jq -r -c '.repo.actions.users["'$user'"] == null')
                #echo "DEBUG: src_pt_repo_user_cfg = $src_pt_repo_user_cfg"
                src_pt_build_user_cfg=$(echo $src_pt_json | jq -r -c '.build.actions.users["'$user'"] == null')
                #echo "DEBUG: src_pt_build_user_cfg = $src_pt_build_user_cfg"
                upd_dst_pt_json=$dst_pt_json
                if [[ "$src_pt_repo_user_cfg" != "true" ]]; then
                    upd_dst_pt_json=$(echo $upd_dst_pt_json | jq -r -c '.repo.actions.users += {"'$user'" : '$src_pt_repo_user_cfg'}')
                fi
                if [[ "$src_pt_build_user_cfg"  != "true" ]]; then
                    upd_dst_pt_json=$(echo $upd_dst_pt_json | jq -r -c '.build.actions.users += {"'$user'" : '$src_pt_build_user_cfg'}')
                fi
                #echo "DEBUG: upd_dst_pt_json = $upd_dst_pt_json"
                if [[ "$dst_pt_json" == "$upd_dst_pt_json" ]]; then
                    echo "INFO: No updates needed on existing permission target $perm_tgt."
                else
                    dst_perm_update_status=$($DRY_RUN_ECHO curl --write-out '%{http_code}' -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" -XPUT $DST_JPD_URL/artifactory/api/v2/security/permissions/$perm_tgt --data "${upd_dst_pt_json}" )
                    if [ -z "$DRY_RUN_ECHO" ]; then
                        echo "INFO: Updated existing permission target $perm_tgt. API Response: ${dst_perm_update_status}"
                    else
                        echo "API CALL: $(hide_token "${dst_perm_update_status}")"
                    fi
                fi
            else 
                echo "INFO: Permission target $perm_tgt is not present in destination JPD."
                ### Create a new permission target in the destination JPD. ###
                
                #echo "DEBUG: New permission target json content: ${src_pt_json}"
                # TODO: Validate if all groups and all users in the user permission target json are valid in destination JPD.
                src_pt_repo_user_cfg=$(echo $src_pt_json | jq -r -c '.repo.actions.users["'$user'"] == null')
                src_pt_repo_user_present=$(echo $src_pt_json | jq -r -c '.repo.actions.users // empty')
                #echo "DEBUG: src_pt_repo_user_cfg = $src_pt_repo_user_cfg"
                src_pt_build_user_cfg=$(echo $src_pt_json | jq -r -c '.build.actions.users["'$user'"] == null')
                src_pt_build_user_present=$(echo $src_pt_json | jq -r -c '.build.actions.users // empty')
                #echo "DEBUG: src_pt_build_user_cfg = $src_pt_build_user_cfg"
                cp_src_pt_json=$src_pt_json
                if [[ ! -z "$src_pt_repo_user_present" ]]; then
                    cp_src_pt_json=$(echo $cp_src_pt_json | jq -r -c 'del(.repo.actions.users)')
                fi
                if [[ "$src_pt_repo_user_cfg" != "true" ]]; then
                    cp_src_pt_json=$(echo $cp_src_pt_json | jq -r -c '.repo.actions.users += {"'$user'" : '$src_pt_repo_user_cfg'}')
                fi
                if [[ ! -z "$src_pt_build_user_present" ]]; then
                    cp_src_pt_json=$(echo $cp_src_pt_json | jq -r -c 'del(.build.actions.users)')
                fi
                if [[ "$src_pt_build_user_cfg" != "true" ]]; then
                    cp_src_pt_json=$(echo $cp_src_pt_json | jq -r -c '.build.actions.users += {"'$user'" : '$src_pt_build_user_cfg'}')
                fi
                #echo "DEBUG: cp_src_pt_json = $cp_src_pt_json"
                dst_perm_create_status=$($DRY_RUN_ECHO curl --write-out '%{http_code}' -k -s -H"Authorization: Bearer $DST_JPD_AUTH_TOKEN" -H "Content-Type: application/json" -XPOST $DST_JPD_URL/artifactory/api/v2/security/permissions/$perm_tgt --data "${cp_src_pt_json}" )
                if [ -z "$DRY_RUN_ECHO" ]; then
                    echo "INFO: Created new permission target $perm_tgt. API Response: ${dst_perm_create_status}"
                else
                    echo "API CALL: $(hide_token "${dst_perm_create_status}")"
                fi
            fi
        done
    fi
done
echo THE END