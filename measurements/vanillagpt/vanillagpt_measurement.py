from helpers.memories.memory import Memory

from langchain.agents import StructuredChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain


from langchain_benchmarks.tool_usage.agents.adapters import apply_agent_executor_adapter
from langchain.schema.runnable import Runnable

import os
import pickle
import time

from helpers.utilities.time_recorder import plaingpt_record


class PlainGPT:
    def __init__(self, task):
        self.task = task
        self.env = self.task.create_environment()
        self.state_reader = self.env.read_state
        self.tools = self.env.tools
        
        
        self.llm = ChatOpenAI(model='gpt-4', temperature=0.0, model_kwargs={"seed": 0})   
        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        Entity history: {entities}
        
        {summary_history}
        Question: {input}
        {agent_scratchpad}"""

        
        self.prompt = StructuredChatAgent.create_prompt(
            self.tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "summary_history", "agent_scratchpad", "entities"], 
        )
        
        self.memory_obj = Memory(name = 'plaingpt')
        self.memory_obj.clear_long_term_memory()
        self.memory = self.memory_obj.get_memory()
        

        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.agent = StructuredChatAgent(llm_chain=self.llm_chain, tools=self.tools, verbose=True)
        
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent, tools=self.tools, memory=self.memory, verbose=False,  handle_parsing_errors=True, return_intermediate_steps=True
        ) 
    
    def query_process(self, query):
        start_memory_extraction_time = time.time()
        entities = self.memory_obj.retrieve_entities(query)
        memory_extraction_time = time.time() - start_memory_extraction_time
        
        question, results_path = plaingpt_record(memory_time = memory_extraction_time)

        results = self.agent_chain.invoke({'input': query, 'entities': entities})
        
        store_path = os.path.join(results_path, question)
        with open(store_path, 'wb') as f:
            pickle.dump(results, f)
            
        return results
        
    def __call__(self) -> Runnable:
        return apply_agent_executor_adapter(self.agent_chain, state_reader=self.state_reader)
    
    def create(self) -> Runnable:
        """Agent Executor"""
        # For backwards compatibility
        return self()

