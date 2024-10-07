#read and setup enjoinment variables here
import os
import json
from helpers.configs.configuration import Configs

from helpers.permission.permission import clear_session_permissions



def setup_environment():
    paths = Configs
    with open(paths.env_variables_path, "r") as f:
        env_variables = json.load(f)
        for key, value in env_variables.items():
            os.environ[key] = value
    clear_session_permissions()
    
    

