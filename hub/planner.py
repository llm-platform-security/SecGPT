# Libraries for LLMs
from langchain_openai import ChatOpenAI

# Library for importing prompt templates
from helpers.templates.prompt_templates import MyTemplates

# Library for plan parsing
from langchain_core.output_parsers import JsonOutputParser


class Planner:
    def __init__(self, temperature=0.0):
        self.chat_llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0})

        templates = MyTemplates()
        self.template_plan = templates.template_planner

        self.parser = JsonOutputParser()
        
        self.llm_chain = self.template_plan | self.chat_llm | self.parser 

    # Generate a plan based on the user's query
    def plan_generate(self, query, tool_info, chat_history):            
        plan = self.llm_chain.invoke({"input": query, "tools": tool_info, "chat_history": chat_history})
        return plan
        