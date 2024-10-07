from helpers.templates.prompt_templates import MyTemplates

# Library for generating lists
import ast

# Libraries for LLMChain
from langchain.chains import LLMChain

# for recording time
from helpers.utilities.time_recorder import secgpt_record
import time

class Planner:
    def __init__(self, llm, tool_importer, memory_obj):
        self.chat_llm = llm
        self.tool_importer = tool_importer
        self.memory_obj = memory_obj
        self.memory = self.memory_obj.get_memory()
        self.summary_memory = self.memory_obj.get_summary_memory()
        
        templates = MyTemplates()
        self.template_plan = templates.template_plan     
        
        self.llm_chain = LLMChain(
            llm=self.chat_llm,
            prompt=self.template_plan,
            verbose=False,
        )

    # Generate a plan based on the user's query
    def plan_generate(self, query):
        start_memory_extraction_time = time.time()
        summary_history = str(self.summary_memory.load_memory_variables({})['summary_history'])
        memory_extraction_time = time.time() - start_memory_extraction_time

        # Hub memory time - time to extract memory for the hub planner
        secgpt_record(hub_memory_time = memory_extraction_time)
        
        start_planning_time = time.time()
        plan = self.llm_chain.predict(input=query, tools=self.tool_importer.get_all_description_and_args(), chat_history=summary_history)
        planning_time = time.time() - start_planning_time
        secgpt_record(hub_planning_time = planning_time)   
        
        app_list = []
        if plan:
            if plan[0] == '[':
                app_list = ast.literal_eval(plan)
        return app_list
    