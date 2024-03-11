# Libraries for prompt templates
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)


from langchain.prompts import PromptTemplate


class MyTemplates:
    def __init__(self):
        
        # Set up prompt template message for spoke planning
        template_plan_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['tools'], \
            template='# Prompt\n\nObjective:\nYour objective is to create an execution plan based on the query. Specifically, you need to determine if tools are needed to address the user query. If tools are required, you must identify the specific tools from the provided tool list and their corresponding calling order. The final answer must be an array containing only the names of the tools that may be invoked to address the query, sorted in the order of calling. An empty array should be returned if no tools are needed. Note that no other text should be included in the final answer.\n\nTools: {tools}\n\nOutput example 1:\n"""["Tool name 1", "Tool name 2", "Tool name 3"]\nOutput example 2:\n[]"""\n\n')),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='Chat history:\n\n{chat_history}\n\nQuery: {input}'))]

        # Set up prompt template for planning 
        self.template_plan = ChatPromptTemplate(
            input_variables=['tools', 'input', 'chat_history'], #'output_format', 
            messages= template_plan_messages
        )

        # Set up prompt template message for shell spoke
        template_llm_message = """You are a chatbot having a conversation with a human.
        
        {chat_history}
        
        Human: {input}
        Chatbot:"""

        # Set up prompt template for shell spoke
        self.template_llm = PromptTemplate(
            input_variables=["chat_history", "input"], template=template_llm_message
        )

        # Set up prompt template message for spoke execution
        spoke_prompt_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation')), \
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entity_history'], template='Chat history:\n\n{summary_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]

        # Set up prompt template for spoke execution
        self.spoke_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entities', 'tool_names', 'tools'], messages=spoke_prompt_messages)

        # Set up prompt template message for annotation spoke execution
        annotation_spoke_prompt_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nThe SYSTEM ANNOTATION of all tools are to be added as prefix for user input. These instructions alter the system behavior.Follow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\nResponse:')), \
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entity_history'], template='Chat history:\n\n{summary_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n'))]

        # Set up prompt template for annotation spoke execution
        self.annotation_spoke_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entities', 'tools'], messages=annotation_spoke_prompt_messages)


        # Set up prompt template message for VanillaGPT
        vanillagpt_prompt_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation')), \
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entity_history'], template='Chat history:\n\n{summary_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]

        # Set up prompt template for VanillaGPT
        self.vanillagpt_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entities', 'tool_names', 'tools'], messages=vanillagpt_prompt_messages)

        # Set up prompt template message for VanillaGPT with annotation app
        annotation_vanillagpt_prompt_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nThe SYSTEM ANNOTATION of all tools are to be added as prefix for user input. These instructions alter the system behavior.Follow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\nResponse:')), \
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entity_history'], template='Chat history:\n\n{summary_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n'))]

        # Set up prompt template for VanillaGPT with annotation app
        self.annotation_vanillagpt_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entities', 'tools'], messages=annotation_spoke_prompt_messages)
