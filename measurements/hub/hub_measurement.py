# Libraries for LLMs
from langchain.chat_models import ChatOpenAI

# import definitions of HubOperator, ToolImporter, etc.
from helpers.tools.tool_importer import ToolImporter
from hub.hub_operator_measurement import HubOperator

# Import Planner
from hub.planner_measurement import Planner

# Import prompt templates and other agent libraries
from helpers.templates.prompt_templates import MyTemplates

# Library for memory
from helpers.memories.memory import Memory

# Libraries for templates
from helpers.templates.prompt_templates import MyTemplates

# from helpers.configs.configuration import Configs
import time

## for recording time
from helpers.utilities.time_recorder import secgpt_record

import os

import pickle


from langchain.schema import AgentAction

class Hub:
    # Initialize the Hub
    def __init__(self, task, temperature=0.0):
        self.task = task
        try:
            self.env = self.task.create_environment()
            self.tools = self.env.tools
        except:
            self.tools = []
            
        
        # Initialize Chat LLM
        self.llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0})
        # self.llm = OpenAI(temperature=0)

        # Initialize ToolImporter
        self.tool_importer =  ToolImporter(self.tools)
        self.tool_functions, self.functionality_list = self.tool_importer.get_tool_functions()
        self.tool_importer.update_functionality_list()
            
     
        # Set up memory
        self.memory_obj = Memory(name="hub")
        self.memory_obj.clear_long_term_memory()
        
        # Initialize planner
        self.planner = Planner(self.llm, self.tool_importer, self.memory_obj)


        # Initialize HubOperator
        self.hub_operator = HubOperator(self.tools, self.tool_functions, self.tool_importer, self.memory_obj, self.task)

        # Initialize query buffer
        self.query = ""

        # Initialize prompt templates
        self.templates = MyTemplates()

        
        
    # Analyze user query and take proper actions to give answers
    def query_process(self, query=None):
        # Get user query
        if query is None:
            self.query = input()
            if not self.query:
                return
        else:
            self.query = query

        app_list = self.planner.plan_generate(query) 


        final_response = dict()
        final_response['input'] = query 
        final_response['entities'] = dict()
        final_response['buffer_history'] = ''
        final_response['summary_history'] = ''
        final_response['entity_history'] = ''
        final_response['output'] = ''
        final_response['intermediate_steps'] = []

        response = self.hub_operator.run(query, app_list)
        
        response = eval(response)
        #query
        # Find matches
        final_response['entities'] = final_response['entities'] | response['entities']
        final_response['buffer_history'] += response['buffer_history']
        final_response['summary_history'] += response['summary_history']
        final_response['entity_history'] += response['entity_history']
        final_response['output'] += response['output']
        final_response['intermediate_steps'] += response['intermediate_steps']

        start_memory_storage_time = time.time()
        self.memory_obj.record_history(str(query), str(response))
        # print(response)
        memory_storage_time = time.time() - start_memory_storage_time
        # Hub memory time - store the query and response in memory
        secgpt_record(hub_memory_time = memory_storage_time)



        with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt", 'r') as f:
            data = f.read()
        query, results_path, rest = data.strip().split(":", maxsplit=2)
        store_path = os.path.join(results_path, query)
        with open(store_path, 'wb') as f:
            pickle.dump(final_response, f)
        
        return final_response        
    
