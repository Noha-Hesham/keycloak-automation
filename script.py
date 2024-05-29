import openpyxl
import urllib3
import requests
import json

# Keycloak server details
url = "https://www.penta-b.online/keycloak/auth/realms/master/protocol/openid-connect/token"
userName = 'admin'
password = 'jjf777#kfd'
# Excel sheet details
EXCEL_FILE = 'groups_data.xlsx'
SHEET_NAME = 'Groups'

def getToken(url, password):
    payload = f'client_id=admin-cli&username={userName}&password={password}&grant_type=password'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return f"Bearer {response.json()['access_token']}"

def get_group_id(group_name, token):
    url = "https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/groups"

    payload = {}
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }

    groupLst = requests.request("GET", url, headers=headers, data=payload)
    try:
        for group in groupLst.json():
            if group['name'] == group_name:
                groupId = group['id']
                return groupId
    except:
        print(group_name, " is not exists")


def get_user_id(user_name, token):
    url = "https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/ui-ext/brute-force-user"

    payload = {}
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }

    usersLst = requests.request("GET", url, headers=headers, data=payload)
    try:
        for user in usersLst.json():
            if user['username'] == user_name:
                userId = user['id']
                return userId
    except:
        print(user_name, " is not exists")


def get_role_id(role_name, token):
    url = "https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/roles"

    payload = {}
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }

    rolesLst = requests.request("GET", url, headers=headers, data=payload)
    try:
        for role in rolesLst.json():
            if role['name'] == role_name:
                roleId = role['id']
                return roleId
    except:
        print(role_name, " is not exists")

def create_group(group_name, token):
    url = "https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/groups"

    payload = json.dumps({
            "name": group_name
            })
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def checkGroupUser(groupId, user_name):
    url = f"https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/groups/{groupId}/members"

    payload = {}
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        usersLst = response.json()
        if len(usersLst)>0:
            for user in usersLst:
                if user['name'] == user_name:
                    return True
                return False
        else:
            return False

    except Exception as e:
        print(e)

def checkGroupRole(groupId, role_name):
    url = f"https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/groups/{groupId}/role-mappings"

    payload = {}
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        realmMappings = response.json()
        rolesLst = realmMappings['realmMappings']
        if len(rolesLst)>0:
            for role in rolesLst:
                if role['name'] == role_name:
                    return True
                return False
        else:
            return False

    except Exception as e:
        print(e)

def addGroupUser(groupId, userId, token):
    url = f"https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/users/{userId}/groups/{groupId}"

    payload = json.dumps({})
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }
    try:
        response = requests.request("PUT", url, headers=headers, data=payload)
        print("userCreated", response.text)
    except Exception as e:
        print("failed to add user", e)

def addGroupRole(roleId, role_name, groupId, token):
    url = f"https://www.penta-b.online/keycloak/auth/admin/realms/signalcorps/groups/{groupId}/role-mappings/realm"

    payload = json.dumps([
    {
        "id": roleId,
        "name": role_name
    }
    ])
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'authorization': token,
    'content-type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print("roleCreated", response.text)
    except Exception as e:
        print(e, response.text)
    

    

def read_excel_data(file_name, sheet_name):
    wb = openpyxl.load_workbook(file_name)
    sheet = wb[sheet_name]
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)
    return data


if __name__ == '__main__':
    token = getToken(url, password)
    excel_data = read_excel_data(EXCEL_FILE, SHEET_NAME)
    
    for row in excel_data[1:]:  # Skip header row
        group_name, users_str, roles_str = row[0], row[1], row[2]
        users = users_str.split(',') if users_str else []
        roles = roles_str.split(',') if roles_str else []
        
        group_id = get_group_id(group_name, token)
        if group_id is None:
            create_group(group_name, token)
            group_id = get_group_id(group_name, token)
        for user in users:
            if not checkGroupUser(group_id, user):
                user_id = get_user_id(user, token)
                if user_id:
                    addGroupUser(group_id, user_id, token)

        for role in roles:
            if not checkGroupRole(group_id, role):
                role_id = get_role_id(role, token)
                if role_id:
                    addGroupRole(role_id,role, group_id,  token)
        print(group_name)
            
    print("done")