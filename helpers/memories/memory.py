# Libraries for memory
from typing import Any
from langchain.memory import (
    ConversationBufferMemory, 
    ConversationSummaryBufferMemory,
    ConversationEntityMemory,
    CombinedMemory
)
from langchain_community.chat_message_histories import RedisChatMessageHistory

from langchain_openai import ChatOpenAI

# import configuration
from helpers.configs.configuration import Configs


class Memory:
    def __init__(self, name):
        db_url = Configs.db_url
        llm=ChatOpenAI(model='gpt-4', temperature=0.0, model_kwargs={"seed": 0}) 

        # Set up databases for storing memory content
        self.message_history = RedisChatMessageHistory(url=db_url, ttl=600, session_id=name)
        self.summary_history = RedisChatMessageHistory(url=db_url, ttl=600, session_id=name+"_summary")
        self.entity_history = RedisChatMessageHistory(url=db_url, ttl=600, session_id=name+"_entity")

        # Set up full conversation memory
        conv_memory = ConversationBufferMemory(chat_memory=self.message_history, memory_key="buffer_history", input_key="input", output_key='output') # output_key is added for measurement
        
        # Set up summarized memory
        summary_memory=ConversationSummaryBufferMemory(llm=llm, max_token_limit=300, memory_key="summary_history", input_key="input", output_key='output', chat_memory=self.summary_history)  

        # Set up entity memory
        entity_memory = ConversationEntityMemory(llm=llm, chat_memory=self.entity_history, chat_history_key="entity_history", input_key="input", output_key='output')

        # Combine all memories  
        self.memory = CombinedMemory(memories=[conv_memory, summary_memory, entity_memory]) 
    
    def get_memory(self):
        return self.memory

    def get_entity_memory(self):
        for item in self.memory.memories:
            if isinstance(item, ConversationEntityMemory):
                return item 
    
    def get_summary_memory(self):
        for item in self.memory.memories:
            if isinstance(item, ConversationSummaryBufferMemory):
                return item
    
    def get_long_term_full_memory(self):
        return self.message_history.messages # return the list of stored interaction history

    def get_long_term_summary_memory(self):
        return self.summary_history.messages
    
    def get_long_term_entity_memory(self):
        return self.entity_history.messages
        
    def clear_long_term_memory(self):
        self.message_history.clear()    
        self.summary_history.clear()
        self.entity_history.clear()

    def retrieve_entities(self, data):
        _input = {"input": data}
        entity_memory = self.get_entity_memory()
        entity_dict = entity_memory.load_memory_variables(_input)
        results = {}
        if "entities" in entity_dict:
            results = entity_dict["entities"]
        return str(results)
    
    # Use save_context method with passing inputs and outputs dictionaries
    def record_history(self, inputs, outputs):
        inputs_dict = {"input": inputs}  
        outputs_dict = {"output": outputs} #{"text": outputs}
        self.memory.save_context(inputs_dict, outputs_dict)


        