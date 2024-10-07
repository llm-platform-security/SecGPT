import os
from enum import Enum

class Mode(Enum):
    DEBUG = True
    NORMAL = False

class Configs:
    debug_mode = Mode.DEBUG 
    user_id = "0"
    # Set the root path of the project with absolute path
    root_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE"
    env_variables_path = os.path.join(root_path, "data/env_variables.json")
    db_url = "redis://127.0.0.1:6379/0" #localhost
    db_port = 6379
    tool_specifications_path = os.path.join(root_path, "helpers/tools/specifications")
    # Google account file or credentials
    credentials_path = os.path.join(root_path, "data/credentials.json")
    # Set the token file path for Gmail
    gmail_token_path = os.path.join(root_path, "data/gmail_token.json")
    # Set the token file path for Google Drive
    gdrive_token_path = os.path.join(root_path, "data/drive_token.json")
    # Set the folder that Google Drive can access 
    google_drive_folder = "root" # personal home folder
    permanent_permissions_path = os.path.join(root_path, "data/perm.json")
    functionalities_path = os.path.join(root_path, "data/functionalities.json")

    @classmethod
    def set_debug_mode(cls, debug_mode):
        if debug_mode:
            cls.debug_mode = Mode.DEBUG
        else: 
            cls.debug_mode = Mode.NORMAL   
            
    @classmethod
    def set_user_id(cls, user_id):
        cls.user_id = user_id
        
    @classmethod
    def set_functionalities_path(cls, path):
        cls.functionalities_path = path
        