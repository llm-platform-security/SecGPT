# Libraries for LLMs
from langchain_openai import ChatOpenAI

# import definitions of HubOperator, ToolImporter, etc.
from helpers.tools.tool_importer import ToolImporter
from hub.hub_operator import HubOperator 

# Import Planner
from hub.planner import Planner

# Library for memory
from helpers.memories.memory import Memory

# Library for parsing responses
import re

class Hub:
    # Initialize Hub
    def __init__(self, temperature=0.0):

        # Initialize Chat LLM
        self.llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0})

        # Initialize ToolImporter
        self.tool_importer =  ToolImporter()
        self.tools = self.tool_importer.get_all_tools()
        self.tool_functions, self.functionality_list = self.tool_importer.get_tool_functions()   

        # Set up memory
        self.memory_obj = Memory(name="hub")
        # Set the memory as session long-term memory
        self.memory_obj.clear_long_term_memory()

        # Initialize planner
        self.planner = Planner(self.llm, self.tool_importer, self.memory_obj)

        # Initialize HubOperator
        self.hub_operator = HubOperator(self.tools, self.tool_functions, self.tool_importer, self.memory_obj)

        # Initialize query buffer
        self.query = ""

    # Analyze user query and take proper actions to give answers
    def query_process(self, query=None):
        # Get user query
        if query is None:
            self.query = input()
            if not self.query:
                return
        else:
            self.query = query

        # Invoke the planner to select the appropriate apps
        app_list = self.planner.plan_generate(query)

        # Then, the hub operator will select the appropriate spoke to execute
        try:
            response = self.hub_operator.run(query, app_list)
        except Exception as e:
            print("SecGPT: An error occurred during execution.")
            print("Details: ", e)
            return
            
        # Record the chatting history to Hub's memory
        self.memory_obj.record_history(str(query), str(response))

        # Parse and display the response
        if response:
            if response[0] == '{': 
                pattern = r"[\"']output[\"']:\s*(['\"])(.*?)\1(?=,|\}|$)"
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    output = match.group(2)
                else:
                    output = response
                    
                if 'Response' in output:
                    try:
                        output = output.split('Response: ')[1]
                    except:
                        pass
            else:
                output = response
            print("SecGPT: " + output)
        else:
            print("SecGPT: ")
            