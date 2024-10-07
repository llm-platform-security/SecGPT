

# Library for tool importer
from helpers.tools.tool_importer import ToolImporter

# Library for hub operator
from hub.hub_operator import HubOperator 

# Import Planner
from hub.planner import Planner

# Library for memory
from helpers.memory.memory import Memory

# Library for parsing responses
import re

class Hub:
    # Initialize Hub
    def __init__(self):

        # Initialize ToolImporter
        self.tool_importer =  ToolImporter()

        # Set up memory
        self.memory_obj = Memory(name="hub")
        # Set the memory as session long-term memory
        self.memory_obj.clear_long_term_memory()

        # Initialize planner
        self.planner = Planner()

        # Initialize HubOperator
        self.hub_operator = HubOperator(self.tool_importer, self.memory_obj)

        # Initialize query buffer
        self.query = ""

    # Analyze user queries and take proper actions to give answers
    def query_process(self, query=None):
        # Get user query
        if query is None:
            self.query = input()
            if not self.query:
                return
        else:
            self.query = query

        # Get the candidate tools
        tool_info = self.tool_importer.get_tools(self.query)

        # Retrieve the chat history to facilitate the planner
        summary_history = ''
        summary_memory = self.memory_obj.get_summary_memory()
        if summary_memory:
            summary_history = str(summary_memory.load_memory_variables({})['summary_history'])

        # Invoke the planner to select the appropriate apps
        replan_consent = False
        while True:
            plan = self.planner.plan_generate(self.query, tool_info, summary_history)

            # Then, the hub operator will select the appropriate spoke to execute
            try:
                replan_consent, response = self.hub_operator.run(query, plan)
            except Exception as e:
                print("\nSecGPT: An error occurred during execution.")
                print("Details: ", e)
                return
                
            # Record the chatting history to Hub's memory
            self.memory_obj.record_history(str(query), str(response))

            # Replan if the user does not consent
            if not replan_consent:
                break
            
            # Provide the planner with context that the user declined the previous plan
            summary_history = summary_history + "\n" + response

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
            print("IsolateGPT: " + output + "\n")
        else:
            print("IsolateGPT: \n")
            