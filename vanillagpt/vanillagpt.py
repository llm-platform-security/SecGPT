from helpers.tools.tool_importer import ToolImporter
from helpers.memory.memory import Memory

from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI

from helpers.configs.configuration import Configs 

from helpers.templates.prompt_templates import MyTemplates

from langchain.tools.render import render_text_description_and_args
from langchain_core.runnables import RunnablePassthrough
from langchain.agents.format_scratchpad import format_log_to_str

from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from helpers.tools.tool_importer import get_annotation_text


class VanillaGPT:
    def __init__(self):
        self.tool_importer = ToolImporter()
        self.tools = self.tool_importer.get_all_tools()  
        self.annotation_tools = self.tool_importer.get_all_annotation_tools()  
        
        self.llm = ChatOpenAI(model='gpt-4', temperature=0.0, model_kwargs={"seed": 0})
        
        templates = MyTemplates()
        # If all tools are annotation tools, use the annotation prompt
        if self.tools == self.annotation_tools:
            self.prompt = templates.annotation_vanillagpt_prompt
            
            self.prompt = self.prompt.partial(
                tools=get_annotation_text([t.name for t in self.tools])
            )
            self.tools = []
        else:
            self.prompt = templates.vanillagpt_prompt   
            missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
                self.prompt.input_variables
            )
            if missing_vars:
                raise ValueError(f"Prompt missing required variables: {missing_vars}")
            self.prompt = self.prompt.partial(
                tools=render_text_description_and_args(list(self.tools)),
                tool_names=", ".join([t.name for t in self.tools]),
            )
        
        
        self.memory_obj = Memory(name = 'vanillagpt')
        self.memory_obj.clear_long_term_memory()
        self.memory = self.memory_obj.get_memory()
        

        self.llm_with_stop = self.llm.bind(stop=["Observation"])

        self.agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
            )
            | self.prompt
            | self.llm_with_stop
            | StructuredChatOutputParser()
        )
  
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent, tools=self.tools, memory=self.memory, verbose=Configs.debug_mode.value,  handle_parsing_errors=True, return_intermediate_steps=True
        )
    
    def query_process(self, query):
        entities = self.memory_obj.retrieve_entities(query)
        try:
            response = self.agent_chain.invoke({'input': query, 'entities': entities})
            if response:
                if type(response) == dict:
                    try:
                        output = response['output']
                    except:
                        output = response
                    
                    if 'Response' in output:
                        try:
                            output = output.split('Response: ')[1]
                        except:
                            pass
                else:
                    output = response
                print("VanillaGPT: " + output)
            else:
                print("VanillaGPT: ")
        except Exception as e:
            print("VanillaGPT: An error occurred during execution.")
            print("Details: ", e)
            pass
