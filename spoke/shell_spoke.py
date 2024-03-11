# Library for prompt templates
from helpers.templates.prompt_templates import MyTemplates

# Library for memory
from helpers.memories.memory import Memory

# Libraries for LLMChain
from langchain.chains import LLMChain

# Library for configuration
from helpers.configs.configuration import Configs

# Libraries for LLMs
from langchain_openai import ChatOpenAI


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
            verbose=mode
        )

    # Execute the query directly using the LLM
    def llm_execute(self, query):
        summary_history = str(self.summary_memory.load_memory_variables({})['summary_history'])
        results = self.llm_chain.predict(input=query, chat_history=summary_history)
        self.memory_obj.record_history(query, results)
        return results
