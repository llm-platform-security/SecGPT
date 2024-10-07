# Libraries for vector databases
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

from langchain.tools import StructuredTool, Tool

# Libraries for configuration
from helpers.configs.configuration import Configs

# Libraries for specifications
import json
from datetime import datetime, date
from pydantic import Field, create_model

# Libraries for message
from helpers.isc.message import Message

# Library for configuration
from helpers.configs.configuration import Configs

# Libraries for google drive and gmail
from langchain.agents.agent_toolkits import GmailToolkit
from langchain.agents import load_tools

from langchain.chat_models import ChatOpenAI


from langchain.tools.render import render_text_description_and_args

# Tool retriever based on the tool description and user input
class ToolImporter:
    # Initialize the tool importer
    def __init__(self, tools=None):
        # Maintain a tool list
        if tools:
            self.tools = tools
        else:
            self.tools = []

        self.tool_name_obj_map = {t.name: t for t in self.tools}
        # Store the descriptions of tools into the vector database  
        if self.tools: 
            docs = [
                Document(page_content=t.description, metadata={"index": i})
                for i, t in enumerate(self.tools)
            ]
            vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
            self.retriever = vector_store.as_retriever()
        
        
    # Get the names of all tools
    def get_tool_names(self):
        tool_names = [t.name for t in self.tools]
        return tool_names

    # Get the list of tool objects
    def get_all_tools(self):
        return self.tools


    # Get the functionality of all tools
    def get_tool_functions(self):
        tool_function_dict = dict()
        function_list = list()
        
        for t in self.tools:
            tool_function_dict[t.name] = [t.name]
            function_list.append(t.name)
        
        return tool_function_dict, function_list

    def get_tool_description_and_args(self, tool_name):
        tool_obj = self.tool_name_obj_map[tool_name]
        return render_text_description_and_args([tool_obj])
    
    def update_functionality_list(self):
        detailed_functionality_dict = dict()
        for tool in self.tools:
            args_schema = str(tool.args)
            description = tool.description
            name = tool.name
            detailed_functionality_dict[name] = {
                "description": description,
                "args": args_schema
            }
    
        with open(Configs.functionalities_path, "r") as f:
            functionality_dict = json.load(f)
        

        functionality_dict["installed_functionalities"] = detailed_functionality_dict
        functionality_dict["available_functionalities"] = detailed_functionality_dict
        
        with open(Configs.functionalities_path, "w") as f:
            json.dump(functionality_dict, f, indent=4)
    
    
    def get_all_description_and_args(self):
        return render_text_description_and_args(self.tools)
    
    # Get the potential tool list based on user query
    def get_tools(self, query):
        docs = self.retriever.get_relevant_documents(query)
        tool_list = [self.tools[d.metadata["index"]] for d in docs]

        for tool in tool_list:
            # Check if any keyword related to a tool is in the user's query
            if not(tool.name in query or any(keyword in query for keyword in tool.description.split())):
                tool_list.remove(tool)

        str_list = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in tool_list]
        )
        
        return str_list


    # Create customized tool for isc
    def create_isc_tool(self, functionality_list, child_sock, id):
        # tool function definition
        
        # Format and send the probe message to the hub
        def probe_functionality(spoke_id: str, functionality:str):
            # check whether the functionality is in the functionality list
            spoke_id = id
            if functionality not in functionality_list:
                return "Functionality not found"
            
            # format the functionality probe message
            probe_message = Message().function_probe_request(spoke_id, functionality)

            # make request to probe functionality request format
            child_sock.send(probe_message)
            request_format = child_sock.recv()

            return request_format

        # Format and send the app request message to the hub
        # need to change the format of the request
        def make_request(spoke_id: str, functionality: str, request: dict):
            spoke_id = id
            # if functionality not in functionality_list:
            #     return "Functionality not found"

            # format the app request message
            app_request_message = Message().app_request(spoke_id, functionality, request)
            child_sock.send(app_request_message)
            response = child_sock.recv()

            return response

        tool_probe_functionality = StructuredTool.from_function(
            func=probe_functionality,
            name="probe_functionality",
            description="make request to probe the request format for invoking a functionality"
        )

        tool_make_request = StructuredTool.from_function(
            func=make_request,
            name="make_request",
            description="make request to collaborate with other tools after getting the response of probe_functionality."
        )

        return tool_probe_functionality, tool_make_request


def create_message_spoke_tool():
    
    def message_spoke(message:str):
        return message

    tool_message_spoke = Tool.from_function(
        func=message_spoke,
        name="message_spoke",
        description="send message from the spoke_operator to the spoke"
    )

    return tool_message_spoke
