import os
import json
from helpers.configs.configuration import Configs
from helpers.permission.permission import clear_temp_permissions

def setup_environment():
    # Read and setup enjoinment variables here
    with open(Configs.env_variables_path, "r") as f:
        env_variables = json.load(f)
        for key, value in env_variables.items():
            os.environ[key] = value
    # Set google account file
    os.environ["GOOGLE_ACCOUNT_FILE"] = Configs.credentials_path
    # Clear session permissions
    clear_temp_permissions()
