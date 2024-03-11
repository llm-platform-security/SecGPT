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

def clear_temp_permissions():
    permissions = read_permissions_from_file()
    for user_id in permissions:
        for app in list(permissions[user_id]):
            for exec_or_data in list(permissions[user_id][app]):
                if not permissions[user_id][app][exec_or_data]:
                    del permissions[user_id][app][exec_or_data]
                elif permissions[user_id][app][exec_or_data] in PermissionType.SESSION:
                    del permissions[user_id][app][exec_or_data]
    write_permissions_to_file(permissions)

def set_permission(user_id, app, permission_type, exec_or_data):
    permissions = read_permissions_from_file()
    permissions[user_id] = permissions.get(user_id, {})
    permissions[user_id][app] = permissions[user_id].get(app, {})
    permissions[user_id][app][exec_or_data] = permission_type
    write_permissions_to_file(permissions)

def get_permission(user_id, app, exec_or_data):
    permissions = read_permissions_from_file()
    app_permissions = permissions.get(user_id, {}).get(app)
    if app_permissions:
        return app_permissions.get(exec_or_data)
    return None
    # return permissions.get(user_id, {}).get(app).get(exec_or_data)

def request_permission(user_id, app, action, exec_or_data):
    if exec_or_data == 'exec':
        action_type = 'execute'
    elif exec_or_data == 'data':
        action_type = 'access data'
    print("\n=====================================")
    print(f"Allow {app} to {action_type}")
    print(f"\nDetails: {action}\n")
    print("Choose permission type for this operation:")
    print("1. Allow Once")
    print("2. Allow for this Session")
    print("3. Always Allow")
    print("4. Don't Allow")
    print("=====================================\n")
    choice = input("Enter your choice: ")

    if choice == '1':
        set_permission(user_id, app, PermissionType.ONE_TIME, exec_or_data)
    elif choice == '2':
        set_permission(user_id, app, PermissionType.SESSION, exec_or_data)
    elif choice == '3':
        set_permission(user_id, app, PermissionType.PERMANENT, exec_or_data)
    else:
        return False

    return True

def get_user_consent(user_id, app, action, flag, exec_or_data='exec'):
    if flag == False:
        if exec_or_data == 'exec':
            print(f"\nWarning: {app} is not expected to be used and may pose security or privacy risks if being used.")
        elif exec_or_data == 'data':
            print(f"\nWarning: {app} is not expected to access your data and may pose security or privacy risks if gaining access.")

    permission_type = get_permission(user_id, app, exec_or_data)

    if exec_or_data == 'exec':
        permission_obj = 'Execution'
    elif exec_or_data == 'data':
        permission_obj = 'Data access'

    if not permission_type:
        if not request_permission(user_id, app, action, exec_or_data):
            print(f"{permission_obj} Permission denied for {app}.")
            return  False 
        permission_type = get_permission(user_id, app, exec_or_data)

    if permission_type == PermissionType.ONE_TIME:
        print(f"One-time {permission_obj} Permission granted for {app}.")
        set_permission(user_id, app, None, exec_or_data)  # Remove permission after use

    elif permission_type == PermissionType.SESSION:
        print(f"Session {permission_obj} Permission granted for {app}.")

    elif permission_type == PermissionType.PERMANENT:
        print(f"Permanent {permission_obj} Permission granted for {app}.")

    else:
        print(f"{permission_obj} Permission denied for {app}.")
        return False
    
    return True
