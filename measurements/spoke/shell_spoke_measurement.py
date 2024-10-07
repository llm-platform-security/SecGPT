from helpers.templates.prompt_templates import MyTemplates

# Library for memory
from helpers.memories.memory import Memory

from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.llms import OpenAI

# Libraries for LLMChain
from langchain.chains import LLMChain

# Library for configuration
from helpers.configs.configuration import Configs

# Libraries for LLMs
from langchain.chat_models import ChatOpenAI

import os

import pickle

import time

from helpers.utilities.time_recorder import secgpt_record

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser




class ShellSpoke:
    def __init__(self, temperature=0.0):
        # Initialize Chat LLM
        self.llm = ChatOpenAI(model='gpt-4', temperature=temperature, model_kwargs={"seed": 0})
        templates = MyTemplates()
        self.template_llm = templates.template_llm

        # Set up memory
        self.memory_obj = Memory(name="shell_spoke")
        self.memory_obj.clear_long_term_memory()
        self.memory = self.memory_obj.get_memory()
        self.summary_memory = self.memory_obj.get_summary_memory()
        
        # Get the mode of execution
        mode = Configs.debug_mode.value

        self.llm_chain = LLMChain(
            llm=self.llm,
            prompt=self.template_llm,
            verbose=mode,
        )

    # Execute the command directly using the LLM
    def llm_execute(self, query):
        start_memory_extraction_time = time.time()
        summary_history = str(self.summary_memory.load_memory_variables({})['summary_history'])
        memory_extraction_time = time.time() - start_memory_extraction_time

        # Spoke memory time - time to extract memory for the spoke
        secgpt_record(spoke_memory_time = memory_extraction_time)

        results = self.llm_chain.predict(input=query, chat_history=summary_history)

        with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt", 'r') as f:
            data = f.read()
        query, results_path, rest = data.strip().split(":", maxsplit=2)
        store_path = os.path.join(results_path, query)

        final_results = {"output": str(results), "intermediate_steps": []} 
        with open(store_path, 'wb') as f:
            pickle.dump(final_results, f)

        return final_results #results


class ShellSpokeExtraction:
    def __init__(self, task, temperature=0.0):
        # Initialize Chat LLM
        self.task = task
        self.llm = ChatOpenAI(model="gpt-4", temperature=temperature, model_kwargs={"seed": 0}).bind_functions(
            functions=[task.schema],
            function_call=task.schema.schema()["title"],
        )

        # Set up memory
        self.memory_obj = Memory(name="shell_spoke")
        self.memory_obj.clear_long_term_memory()
        self.memory = self.memory_obj.get_memory()
        

        self.output_parser = JsonOutputFunctionsParser()

        if task.name == "Chat Extraction":
            def format_run(dialogue_input: dict):
                question = dialogue_input["question"]
                answer = dialogue_input["answer"]
                return {
                    "dialogue": f"<question>\n{question}\n</question>\n"
                    f"<assistant-response>\n{answer}\n</assistant-response>"
                }
            self.extraction_chain = (
                format_run
                | task.instructions
                | self.llm
                | self.output_parser
                | (lambda x: {"output": x})
            ) 
        else:
            self.extraction_chain = task.instructions | self.llm | self.output_parser | (lambda x: {"output": x})

    # Execute the command directly using the LLM
    def llm_execute(self, query):
        start_memory_extraction_time = time.time()
        entities = self.memory_obj.retrieve_entities(query)
        memory_extraction_time = time.time() - start_memory_extraction_time
        
        # Spoke memory time - entity memory extraction from the spoke memory
        question, results_path = secgpt_record(spoke_memory_time = memory_extraction_time)

        if self.task.name == "Chat Extraction":
            question = query['question']
            answer = query['answer']
            start_llm_time = time.time()
            results = self.extraction_chain.invoke({'question': question, 'answer': answer, 'entities': entities})
            llm_time = time.time() - start_llm_time

        else:
            start_llm_time = time.time()
            results = self.extraction_chain.invoke({'input': query, 'entities': entities})
            llm_time = time.time() - start_llm_time

        # Spoke planning time - time to run the LLM for planning
        question, results_path = secgpt_record(spoke_planning_time = llm_time)
        
        start_memory_storage_time = time.time()
        self.memory_obj.record_history(str(query), str(results['output']))
        memory_storage_time = time.time() - start_memory_storage_time

        # Spoke memory time - time to store memory for the spoke
        question, results_path = secgpt_record(spoke_memory_time = memory_storage_time)


        store_path = os.path.join(results_path, question)
        with open(store_path, 'wb') as f:
            pickle.dump(results, f)
        
        
        return results

