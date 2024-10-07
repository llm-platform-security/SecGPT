import ast
# Libraries for messages
from helpers.isc.message import Message


class SpokeOperator:
    def __init__(self, tool_name, functionality_list):
        self.tool_name = tool_name
        self.functionality_list = functionality_list
        self.spoke_id = None
        self.child_sock = None

    def parse_request(self, request):
        try:
            if request.startswith('{'):
                request = ast.literal_eval(request)#json.loads(request)
                functionality = request['functionality_request']
                request_body = request['request_body']
                data = ', '.join(f"{key}={repr(value)}" for key, value in request_body.items())
                request = f"{functionality}({data})"
            return request
            
        except Exception as e:
            print(e)
            return request
    
    
    # Format and send the probe message to the hub
    def probe_functionality(self, functionality:str):
        # check whether the functionality is in the functionality list
        if functionality not in self.functionality_list:
            return
        
        # format the functionality probe message
        probe_message = Message().function_probe_request(self.spoke_id, functionality)

        # make request to probe functionality request format
        self.child_sock.send(probe_message)

        request_format = self.child_sock.recv()
        
        request_schema = request_format['functionality_offered']
        return request_schema


    # Format and send the app request message to the hub
    def make_request(self, functionality: str, request: dict):
        # format the app request message
        app_request_message = Message().app_request(self.spoke_id, functionality, request)
        
        self.child_sock.send(app_request_message)

        response = self.child_sock.recv()
        
        return response['functionality_response']

    def check_format(self, format, instance_dict):
        for key in instance_dict:
            if key not in format:
                return False
        return True


    def return_response(self,  results):
        response = Message().final_response(self.spoke_id, results)
        
        self.child_sock.send(response)
                    