# Libraries for LLMs
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

# Library for memory
from helpers.memories.memory import Memory


# Libaries for prompt templates
from helpers.templates.prompt_templates import MyTemplates

# Libraries for LLMChain
from langchain.chains import LLMChain

# Libraries for different types of agents
from langchain.agents import StructuredChatAgent, AgentExecutor

# Libraries for IPC
from helpers.isc.socket import Socket

# Libraries for spoke operator
from spoke.spoke_operator_measurement import SpokeOperator

# Format tool
import json

from langchain.schema.agent import AgentActionMessageLog, AgentFinish

from langchain.tools.render import render_text_description_and_args

from spoke.output_parser_measurement import SpokeParser

from helpers.configs.configuration import Configs 

from helpers.tools.tool_importer import create_message_spoke_tool

from langchain.tools import StructuredTool



class Spoke():
    # Set up counter to count the number of Spoke instances
    instance_count = 0
    
    # Initialize the Spoke
    def __init__(self, tool, functionalities, temperature=0.0, flag=False): 
        Spoke.instance_count += 1
        
        self.return_intermediate_steps = flag
        
        self.tool = tool
        self.tool_name = self.tool.name #+ load_tools(["requests_all"]) # when using chatgpt plugins, requests_all may be needed
        self.tool_description = render_text_description_and_args([self.tool])
        
        # Initialize functionality list
        functionalities_path = Configs.functionalities_path
        
        with open(functionalities_path, "r") as f:
            functionality_dict = json.load(f)

        self.installed_functionalities_info = functionality_dict["installed_functionalities"]
        self.installed_functionalities = list(filter(lambda x: x not in functionalities, functionality_dict["installed_functionalities"].keys()))

        
        # create a new LLM
        self.llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0}) #gpt-4 

        # set up prompt template
        self.templates = MyTemplates()

        # Set up memory
        self.memory_obj = Memory(name=self.tool_name)
        self.memory_obj.clear_long_term_memory()    
        self.memory = self.memory_obj.get_memory()
        self.summary_memory = self.memory_obj.get_summary_memory()
        

        # Set up spoke operator
        self.spoke_operator = SpokeOperator(self.tool_name, self.installed_functionalities)

       
        func_placeholders = []
        for func in self.installed_functionalities:
            func_placeholder = StructuredTool.from_function(
                func = (lambda *args, **kwargs: None),
                name = func,
                description = self.installed_functionalities_info[func]['description'],
            )
            func_placeholders.append(func_placeholder)
        
        tool_functionality_list = [self.tool] + func_placeholders
        self.prompt = StructuredChatAgent.create_prompt(
            tool_functionality_list,
            prefix=self.templates.prefix,
            suffix=self.templates.suffix,
            input_variables=["input", "summary_history", "agent_scratchpad", "entities"],
        )
        tool_functionality_list.append(create_message_spoke_tool())
        
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.agent = StructuredChatAgent(llm_chain=self.llm_chain, tools=tool_functionality_list, verbose=Configs.debug_mode.value, output_parser=SpokeParser(functionality_list=self.installed_functionalities, spoke_operator=self.spoke_operator))
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent, tools=tool_functionality_list, verbose=Configs.debug_mode.value, memory=self.memory, handle_parsing_errors=True, return_intermediate_steps=self.return_intermediate_steps
        ) 
        
        
    def execute(self, request, entities): 
        results = self.agent_chain.invoke({'input': request, 'entities': entities})
        return results
        

    def run_process(self, child_sock, request, spoke_id, entities): 
        self.spoke_operator.spoke_id = spoke_id
        self.spoke_operator.child_sock = child_sock
        request = self.spoke_operator.parse_request(request)
        results = self.execute(request, entities)
        self.spoke_operator.return_response(str(results))
        

    @classmethod
    def get_instance_count(cls):
        return cls.instance_count
