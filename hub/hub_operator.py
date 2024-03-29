# Library for Spoke
from spoke.spoke import Spoke

# Library for shell_spoke
from spoke.shell_spoke import ShellSpoke

# Libraries for IPC
import socket
import multiprocessing
from helpers.isc.socket import Socket
from helpers.isc.message import Message
import uuid

# Library for permission helper
from helpers.permission.permission import get_user_consent

# Library for configuration 
from helpers.configs.configuration import Configs

# Library for getting timeout setting
from helpers.sandbox.sandbox import TIMEOUT

# Library for parsing entities
import ast

# Set a start method for platforms other than Linux
import platform
if platform.system() != "Linux":
    from multiprocessing import set_start_method
    set_start_method("fork")


# HubOperator is used to route queries and manage the Spokes
class HubOperator:
    # Initialize the hub manager
    def __init__(self, tools, tool_functions, tool_importer, memory_obj):
        # Maintain tool information
        self.tool_functions = tool_functions

        self.function_tools = {}
        for tool, functions in self.tool_functions.items():
            for function in functions:
                self.function_tools[function] = tool

        self.tool_names =  list(self.tool_functions.keys())

        self.tools = tools

        # Maintain a dictionary of Spoke and tool mapping
        self.spoke_tool = {}

        # Maintain a shell spoke
        self.shell_spoke = None

        # Maintain a tool importer
        self.tool_importer = tool_importer

        # Maintain a memory object
        self.memory_obj = memory_obj

        # Maintain a spoke counter
        self.spoke_counter = 0

        # Get user_id
        self.user_id = Configs.user_id

        # Maintain an app list generated by the planner
        self.app_list = []

    # Run hub operator to route user queries
    def run(self, query, app_list):
        # Filter apps
        for app in app_list:
            if app not in self.tool_names:
                app_list.remove(app)
        self.app_list = app_list 
        if self.app_list == []:
            startup_app = ''
        else:
            startup_app = self.app_list[0]

        # Check whether to use the startup_app to solve the query
        if startup_app in self.tool_names: 
            entities = self.memory_obj.retrieve_entities(query)
            entity_dict = ast.literal_eval(entities)
            all_empty = all(value == '' for value in entity_dict.values())

            action_message = f'Your request "{query}" requires executing "{startup_app}"'#+ "\n" + "Shared Data: "+str(entities)
            consent = get_user_consent(self.user_id, startup_app, action_message, True, 'exec')        
            if consent:
                data_consent = True
                if not all_empty:
                    action_message = f'Your data "{entities}" is sharing with "{startup_app}"'
                    data_consent = get_user_consent(self.user_id, startup_app, action_message, True, 'data')
                if not data_consent or all_empty:
                    entities = "{}"
                results = self.execute_app_spoke(query, entities, startup_app, True)
            else:
                results = "User denied the request"
        else:
            if self.shell_spoke is None:
                self.shell_spoke = ShellSpoke()
            results = self.shell_spoke.llm_execute(query)
        return results


    def execute_app_spoke(self, query, entities, requested_app, flag=False):    
        print("Using " + requested_app + " spoke ...\n")
        # Check whether the Spoke exists
        if requested_app in self.spoke_tool.keys():
            # Use the existing Spoke to solve this step
            session_id = uuid.uuid4()
            spoke_id = self.spoke_tool[requested_app]['id']
            spoke_session_id = self.user_id + ":" + str(spoke_id) + ":" + str(session_id)
            spoke = self.spoke_tool[requested_app]['spoke']

            # create a tool after create sockets
            parent, child = socket.socketpair()
            parent_sock = Socket(parent)
            child_sock = Socket(child)

            p = multiprocessing.Process(target=spoke.run_process, args=(child_sock, query, spoke_session_id, entities))
            p.start()
            results = self.handle_request(parent_sock)
            p.join(timeout = TIMEOUT)
            child.close()
            return results


        else:
            # Create a new Spoke to solve this step
            # get the tool object based on the tool name
            tool = [t for t in self.tools if t.name == requested_app][0]

            tool_functionalities = self.tool_functions[tool.name]

            # create a tool after create sockets
            parent, child = socket.socketpair()
            parent_sock = Socket(parent)
            child_sock = Socket(child)

            session_id = uuid.uuid4()
            spoke_session_id = self.user_id + ":" + str(self.spoke_counter) + ":" + str(session_id)
            self.spoke_tool[requested_app] = {
                'id': self.spoke_counter,
                'spoke': Spoke(tool=tool, functionalities=tool_functionalities, flag=flag),
                'tool': tool
            } 
            self.spoke_counter += 1

            spoke = self.spoke_tool[requested_app]['spoke']

            p = multiprocessing.Process(target=spoke.run_process, args=(child_sock, query, spoke_session_id, entities))
            p.start()
            results = self.handle_request(parent_sock)
            p.join(timeout = TIMEOUT)
            child.close()
            return results

    # It should handle different types of requests/responses from Spokes
    def handle_request(self, parent_sock):
        while True:
            data = parent_sock.recv()

            if data['message_type'] == 'final_response':
                return data['response']

            if data['message_type'] == 'function_probe_request':
                function = data['requested_functionality']
                spoke_session_id = data['spoke_id']

                if function not in self.function_tools.keys():
                    response = Message().no_functionality_response(spoke_session_id, function)
                    parent_sock.send(response)
                    continue

                request_app = ""
                spoke_id = spoke_session_id.split(":")[1]
                for app, spoke in self.spoke_tool.items():
                    if str(spoke['id']) == spoke_id:
                        request_app = app
                        break

                app = self.function_tools[function]
                action_message = f'"{request_app}" requests to execute "{app}"'

                if app in self.app_list:
                    flag = True
                else:
                    flag = False

                consent = get_user_consent(self.user_id, app, action_message, flag, 'exec')

                if not consent:
                    response = Message().functionality_denial_response(spoke_session_id, function)            
                else:                    
                    functionality_spec = self.tool_importer.get_tool_function(app, function)
                    response = Message().function_probe_response(spoke_session_id, functionality_spec)

                parent_sock.send(response)

            if data['message_type'] == 'app_request':
                functionality_request = data['functionality_request']
                spoke_session_id = data['spoke_id']

                if functionality_request not in self.function_tools.keys():
                    response = Message().no_functionality_response(functionality_request)
                else:
                    tool = self.function_tools[functionality_request]

                    entities = self.memory_obj.retrieve_entities(str(data))
                    entity_dict = ast.literal_eval(entities)
                    all_empty = all(value == '' for value in entity_dict.values())


                    data_consent = True
                    if not all_empty:
                        if tool in self.app_list:
                            flag = True
                        else:
                            flag = False
                        action_message = f'Your data "{entities}" is sharing with "{tool}"'
                        data_consent = get_user_consent(self.user_id, tool, action_message, flag, 'data')
                    if not data_consent or all_empty:
                        entities = "{}"

                    app_response = self.execute_app_spoke(str(data), entities, tool, False)
                    response = Message().app_response(spoke_session_id, app_response)

                parent_sock.send(response)
                