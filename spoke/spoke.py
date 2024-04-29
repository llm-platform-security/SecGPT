# Libraries for LLMs
from langchain_openai import ChatOpenAI

# Library for memory
from helpers.memory.memory import Memory

# Libaries for prompt templates
from helpers.templates.prompt_templates import MyTemplates

# Libraries for agents
from langchain.agents import AgentExecutor 
from spoke.output_parser import SpokeParser
from langchain_core.runnables import RunnablePassthrough

# Libraries for spoke operator
from spoke.spoke_operator import SpokeOperator

# Libraries for tools and functionalities
import json
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.tools.render import render_text_description_and_args
from helpers.tools.tool_importer import create_message_spoke_tool
from helpers.tools.tool_importer import create_function_placeholder
from helpers.tools.tool_importer import get_annotation_text 

# Library for configuration
from helpers.configs.configuration import Configs 

# Library for sandboxing
from helpers.sandbox.sandbox import set_mem_limit, drop_perms


class Spoke():
    # Set up a counter to count the number of Spoke instances
    instance_count = 0
    
    # Initialize the Spoke
    def __init__(self, tool, functionalities, spec=None, temperature=0.0, flag=False):  
        Spoke.instance_count += 1
        
        self.return_intermediate_steps = flag

        if tool:
            self.tools = [tool]
            self.tool_name = tool.name 
        else:
            self.tools = []
            self.tool_name = ""
        
        self.tool_spec = spec
        self.functionalities = functionalities
        
        # Initialize functionality list
        functionalities_path = Configs.functionalities_path

        with open(functionalities_path, "r") as f:
            functionality_dict = json.load(f)

        self.installed_functionalities_info = functionality_dict["installed_functionalities"]
        self.installed_functionalities = list(filter(lambda x: x not in self.functionalities, functionality_dict["installed_functionalities"]))
    
        # Create a placeholder for each functionality
        func_placeholders = create_function_placeholder(self.installed_functionalities)
        
        self.enabled_annotations_info = functionality_dict["enabled_annotations"]
        self.enabled_annotations = list(filter(lambda x: x not in self.functionalities, functionality_dict["enabled_annotations"]))
        
        
        # Create a new LLM
        self.llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0})  

        # Set up memory
        if self.tool_name:
            self.memory_obj = Memory(name=self.tool_name)
        else:
            self.memory_obj = Memory(name="temp_spoke")
        self.memory_obj.clear_long_term_memory()    
        self.memory = self.memory_obj.get_memory()
        
        # Set up spoke operator
        self.spoke_operator = SpokeOperator(self.installed_functionalities, self.functionalities, self.tool_spec)

        # Set up prompt templates
        self.templates = MyTemplates()
        if self.tool_name in self.enabled_annotations_info:
            self.prompt = self.templates.annotation_spoke_prompt
            
            self.prompt = self.prompt.partial(
                tools=get_annotation_text([self.tool_name]) + render_text_description_and_args(list(func_placeholders)),
            )
            
            tool_functionality_list = func_placeholders
            
        else:
            self.prompt = self.templates.spoke_prompt
           
            missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
                self.prompt.input_variables
            )
            if missing_vars:
                raise ValueError(f"Prompt missing required variables: {missing_vars}")

            tool_functionality_list = self.tools + func_placeholders
            self.prompt = self.prompt.partial(
                tools=render_text_description_and_args(list(tool_functionality_list)),
                tool_names=", ".join([t.name for t in tool_functionality_list]),
            )
        
        self.llm_with_stop = self.llm.bind(stop=["Observation"])
        tool_functionality_list.append(create_message_spoke_tool())
        
        self.agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
            )
            | self.prompt
            | self.llm_with_stop
            | SpokeParser(functionality_list=self.installed_functionalities, spoke_operator=self.spoke_operator)
        )

        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent, tools=tool_functionality_list, verbose=Configs.debug_mode.value, memory=self.memory, handle_parsing_errors=True, return_intermediate_steps=self.return_intermediate_steps 
        )

    def execute(self, request, entities): 
        try:
            results = self.agent_chain.invoke({'input': request, 'entities': entities}, return_only_outputs=not self.return_intermediate_steps)
        except:
            results = {"output": "An error occurred during spoke execution."}
        finally: 
            return results
        
    def run_process(self, child_sock, request, spoke_id, entities):
        # Set seccomp and setrlimit 
        set_mem_limit()
        drop_perms()
        
        self.spoke_operator.spoke_id = spoke_id
        self.spoke_operator.child_sock = child_sock
        request_formatted, request = self.spoke_operator.parse_request(request)
        if request_formatted:
            results = self.execute(request, entities)
        else:
            results = {"output": "Invalid request format. Please provide a valid json blob."}
        self.spoke_operator.return_response(results, request_formatted, self.return_intermediate_steps)  
        
            

    @classmethod
    def get_instance_count(cls):
        return cls.instance_count
