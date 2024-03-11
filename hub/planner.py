# Library for importing prompt templates
from helpers.templates.prompt_templates import MyTemplates

# Library for generating lists
import ast

# Libraries for LLMChain
from langchain.chains import LLMChain

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
            verbose=False
        )

    # Generate a plan based on the user's query
    def plan_generate(self, query):
        summary_history = str(self.summary_memory.load_memory_variables({})['summary_history'])

        plan = self.llm_chain.predict(input=query, tools=self.tool_importer.get_tools(query), chat_history=summary_history)
        self.memory_obj.record_history(query, str({'output': plan}))

        app_list = []
        if plan:
            if plan[0] == '[':
                app_list = ast.literal_eval(plan)
        return app_list
    