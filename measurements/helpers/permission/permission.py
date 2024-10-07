import json
from helpers.configs.configuration import Configs

class PermissionType:
    ONE_TIME = 'one_time'
    SESSION = 'session'
    PERMANENT = 'permanent'

def read_permissions_from_file():
    try:
        perm_path = Configs.permanent_permissions_path
        with open(perm_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_permissions_to_file(permissions):
    perm_path = Configs.permanent_permissions_path
    with open(perm_path, 'w') as file:
        json.dump(permissions, file, indent=4)

def clear_session_permissions():
    permissions = read_permissions_from_file()
    for user_id in permissions:
        for app in list(permissions[user_id]):
            if permissions[user_id][app] == PermissionType.SESSION:
                del permissions[user_id][app]
    write_permissions_to_file(permissions)

def set_permission(user_id, app, permission_type):
    permissions = read_permissions_from_file()
    permissions[user_id] = permissions.get(user_id, {})
    permissions[user_id][app] = permission_type
    write_permissions_to_file(permissions)

def get_permission(user_id, app):
    permissions = read_permissions_from_file()
    return permissions.get(user_id, {}).get(app)

def request_permission(user_id, app, action):
    print(f"Permission request for app: {app}\n Action: {action}")
    print("Choose permission type for this app:")
    print("1. One-time")
    print("2. Session")
    print("3. Permanent")
    print("Others: None")
    choice = input("Enter your choice: ")

    if choice == '1':
        set_permission(user_id, app, PermissionType.ONE_TIME)
    elif choice == '2':
        set_permission(user_id, app, PermissionType.SESSION)
    elif choice == '3':
        set_permission(user_id, app, PermissionType.PERMANENT)
    else:
        print("No permission set.")
        return False

    return True

def get_user_consent(user_id, app, action, flag):
    if flag == False:
        print(f"{app} is not intended for the LLM-generated execution plan and could pose security or privacy risks. Please carefully grant it permission for execution.")
        # if not request_permission(user_id, app, action):
        #     print(f"Permission denied for {app}. Action cannot be performed.")
        #     return  False# Exit if permission setting fails or is invalid
        # permission_type = get_permission(user_id, app)
    # else: 
    permission_type = get_permission(user_id, app)

    if not permission_type:
        # print(f"No existing permission for {app}.")
        if not request_permission(user_id, app, action):
            print(f"Permission denied for {app}. Action cannot be performed.")
            return  False# Exit if permission setting fails or is invalid
        permission_type = get_permission(user_id, app)

    if permission_type == PermissionType.ONE_TIME:
        print(f"One-time permission granted for {app}. Proceeding with the action.")
        set_permission(user_id, app, None)  # Remove permission after use

    elif permission_type == PermissionType.SESSION:
        print(f"Session permission granted for {app}. Proceeding with the action.")

    elif permission_type == PermissionType.PERMANENT:
        print(f"Permanent permission granted for {app}. Proceeding with the action.")

    else:
        print(f"Permission denied for {app}. Action cannot be performed.")
        return False
    
    return True
