import os
from enum import Enum

class Mode(Enum):
    DEBUG = True
    NORMAL = False

class Configs:
    debug_mode = Mode.DEBUG 
    user_id = "0"
    root_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements"
    env_variables_path = os.path.join(root_path, "data/env_variables.json")
    db_url = "redis://localhost:6379/0"
    db_port = 6379
    permanent_permissions_path = os.path.join(root_path, "data/perm.json")
    functionalities_path = ""

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