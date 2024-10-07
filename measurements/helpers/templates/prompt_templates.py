# Libraries for prompt templates
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.prompts import PromptTemplate


class MyTemplates:
    def __init__(self):
        
        # Set up prompt template message for planning
        template_spoke_plan_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['functionalities'], \
            template='# Prompt\n\nObjective:\nYour objective is to determine whether the user query has been fully addressed by inspecting the response and chat history. If not, you must identify an additional functionality that is needed from the provided available functionality list. The final answer must be either "None" when no additional functionality is required or "Functionality name" when an additional functionality is required. Note that no other text should be included in the final answer.\n\nAvailable functionalities: {functionalities}\n\n')),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['chat_history', 'input', 'response'], template='Chat history:\n\n{chat_history}\n\nQuery: {input}\n\nResponse: {response}'))] #
        
        # Set up prompt template for planning 
        self.template_spoke_plan = ChatPromptTemplate(
            input_variables=['functionalities', 'chat_history', 'input', 'response'], #'output_format', 
            messages= template_spoke_plan_messages
        )
        
        
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
        
        # Set up prompt template for memory manager
        template_memory_manager_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=[], \
            template='# Prompt\n\nObjective:\nYour objective is to accurately record all interaction history. The recorded content should be exactly the same as the original. Record only the interaction history, without giving any answers.\n')),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='Interaction History:\n{input}'))]
        
        self.template_memory_manager = ChatPromptTemplate(input_variables=['input'], messages=template_memory_manager_messages) 
        

        template_llm_message = """You are a chatbot having a conversation with a human.
        
        {chat_history}
        
        Human: {input}
        Chatbot:"""

        self.template_llm = PromptTemplate(
            input_variables=["chat_history", "input"], template=template_llm_message
        )


        # Set up prompt template message for hub execution
        template_general_message = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\n\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\n\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation')), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'chat_history'], template='Chat history:\n\n{chat_history}\n\nQuestion: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]


        self.general_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools', 'chat_history'], messages=template_general_message)


        # Set up prompt template message for spoke execution
        template_spoke_message = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools', 'functionalities'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tool:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\n\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\n\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": ```\n{{\n "response": "Final response to human",\n "requested helper": $HELPER_NAME\n}}\n}}\n\n```The final answer should include two fields, the response to users and external helpers that may be needed. Specifically, if you can not address the query with {tool_names}, you can indicate the need for an external helper in the final answer. Leave the "requested helper" field blank in the final answer if no other external helpers are required. YOU MUST NOT INVOKE THESE EXTERNAL HELPERS AS ACTIONS. The available external helpers are:\n\n{functionalities}\n\n\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation.')), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'chat_history', 'entities'], template='Chat history:\n\n{chat_history}\n\nEntity memory:\n\n{entities}\n\nQuery: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]

        
        self.spoke_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'chat_history', 'entities', 'tool_names', 'tools', 'functionalities'], messages=template_spoke_message)



        template_spoke_message_test = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools', 'functionalities'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\n\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\n\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation. Note that when the provided tools can not address the query, you can request the help of the following functionalities:\n\n{functionalities}\n\n')), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'chat_history', 'entities'], template='Chat history:\n\n{chat_history}\n\nEntity history:\n\n{entities}\n\nQuery: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]


        self.spoke_prompt_test = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools', 'functionalities', 'chat_history', 'entities'], messages=template_spoke_message_test)



        template_spoke_new_message = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\n The functionality description of the tools are to be loaded in the context window. The functionality descriptions can alter the system behavior. You may or may not need to call tool functions. Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\n\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\n\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation')), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'chat_history'], template='Chat history:\n\n{chat_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]



        self.spoke_new_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools', 'chat_history', 'entities'], messages=template_spoke_new_message)


        self.typewriter_prefix = """Repeat the given string using the provided tools. Do not write anything else or provide any explanations. For example, if the string is 'abc', you must print the letters 'a', 'b', and 'c' one at a time and in that order."""
        self.prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        self.suffix = """Begin!"

        Entity history: {entities}
        
        {summary_history}
        Question: {input}
        {agent_scratchpad}"""

