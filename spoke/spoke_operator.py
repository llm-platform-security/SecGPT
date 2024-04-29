# Libraries for processing json
from jsonschema import validate
import ast

# Libraries for messages
from helpers.isc.message import Message


class SpokeOperator:
    def __init__(self, functionality_list, functionalities, tool_spec):
        self.functionality_list = functionality_list
        self.tool_spec = tool_spec
        self.functionalities = functionalities
        self.spoke_id = None
        self.child_sock = None
        self.request_functionality = None
            

    def parse_request(self, request):
        is_formatted = True
        try:
            if request.startswith('{'):
                request = ast.literal_eval(request)
                self.request_functionality = request['functionality_request']
                
                request_body = request['request_body']

                if self.tool_spec:
                    request_schema = self.tool_spec['properties'][self.request_functionality]['properties']['request']
                    is_formatted = self.check_format(request_schema, request_body)
                    if is_formatted:
                        data = ', '.join(f"{key}={repr(value)}" for key, value in request_body.items())
                        request = f"{self.request_functionality}({data})"

            return is_formatted, request
            
        except Exception as e:
            return is_formatted, request
    
    # Format and send the probe message to the hub
    def probe_functionality(self, functionality:str):
        # check whether the functionality is in the functionality list
        if functionality not in self.functionality_list:
            return
        
        # format the functionality probe message
        probe_message = Message().function_probe_request(self.spoke_id, functionality)

        # Make request to probe functionality request format
        self.child_sock.send(probe_message)
        response = self.child_sock.recv()

        if response['message_type'] == 'function_probe_response':
            request_schema = response['functionality_offered']['properties'][functionality]['properties']['request']
            response_schema = response['functionality_offered']['properties'][functionality]['properties']['response']
        else:
            request_schema = None
            response_schema = None

        return response['message_type'], request_schema, response_schema

    # Format and send the app request message to the hub
    def make_request(self, functionality: str, request: dict):
        # format the app request message
        app_request_message = Message().app_request(self.spoke_id, functionality, request)
        self.child_sock.send(app_request_message)
        response = self.child_sock.recv()
        
        return response['message_type'], response['response']

    def check_format(self, format, instance_dict):
        try:
            validate(instance=instance_dict, schema=format)
            return True
        except:
            return False

    def return_response(self, results, request_formatted, return_intermediate_steps):
        if not return_intermediate_steps:
            validating_output = results['output']
            if self.tool_spec and request_formatted:
                if self.request_functionality:
                    response_schema = self.tool_spec['properties'][self.request_functionality]['properties']['response']
                    is_formatted = self.check_format(response_schema, validating_output)
                    if is_formatted:
                        response = Message().final_response(self.spoke_id, validating_output)
                        self.child_sock.send(response)
                        return
                else:
                    for functionality in self.functionalities:
                        response_schema = self.tool_spec['properties'][functionality]['properties']['response']
                        is_formatted = self.check_format(response_schema, validating_output)
                        if is_formatted:
                            response = Message().final_response(self.spoke_id, validating_output)
                            self.child_sock.send(response)
                            return
                
                results =  f"Invalid response format."

        response = Message().final_response(self.spoke_id, str(results))
        self.child_sock.send(response)
