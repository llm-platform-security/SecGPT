from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.tools.render import render_text_description_and_args
from langchain.tools import StructuredTool
import json

from src.config import specifications_path


class ToolImporter:
    # Initialize the tool importer
    def __init__(self, tools):
        self.tools = tools    
        self.tool_name_obj_map = {t.name: t for t in self.tools}
        
        # Store the descriptions of tools into the vector database  
        if self.tools: 
            docs = [
                Document(page_content=t.description, metadata={"index": i})
                for i, t in enumerate(self.tools)
            ]
            vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
            self.retriever = vector_store.as_retriever()
            
    # Get the list of tool objects
    def get_all_tools(self):
        return self.tools

    # Get the functionality of all tools
    def get_tool_functions(self):
        
        tool_function_dict = dict()
        function_list = list()
        
        for t in self.tools:
            try:
                with open(f"{specifications_path}/{t.name}.json", "r") as f:
                    schema = json.load(f)
                    functions = list()
                    for function in schema["properties"]:
                        functions.append(function)
                    tool_function_dict[t.name] = functions
                    function_list.extend(functions)
            except:
                tool_function_dict[t.name] = [t.name]
                function_list.append(t.name)
                continue
                    
        return tool_function_dict, function_list
        # Get the functionality of a specific tool

    # Get the functionality of a specific tool
    def get_tool_function(self, tool_name, function):
        with open(f"{specifications_path}/{tool_name}.json", "r") as f:
            schema = json.load(f)
            function_dict = schema
            return function_dict
            
    # Get the potential tool list based on user query
    def get_tools(self, query):
        docs = self.retriever.get_relevant_documents(query)
        tool_list = [self.tools[d.metadata["index"]] for d in docs]

        for tool in tool_list:
            # Check if any keyword related to a tool is in the user's query
            if not(tool.name in query or any(keyword in query for keyword in tool.description.split())):
                tool_list.remove(tool)
        
        str_list = render_text_description_and_args(tool_list)

        return str_list


# Create a tool for messaging between spoke_operator and spoke llm
def create_message_spoke_tool():
    
    def message_spoke(message:str):
        return message

    tool_message_spoke = StructuredTool.from_function(
        func=message_spoke,
        name="message_spoke",
        description="send message from the spoke_operator to the spoke LLM"
    )

    return tool_message_spoke

# Create a placeholder for functionalities
def create_function_placeholder(installed_functionalities):     
    func_placeholders = []
    for func in installed_functionalities:
        func_placeholder = StructuredTool.from_function(
            func = (lambda *args, **kwargs: None),
            name = func,
            description = func,
        )
        func_placeholders.append(func_placeholder)
    return func_placeholders
