from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.prompts import PromptTemplate

class MyTemplates:
    def __init__(self):
        
        # Set up prompt template message for the hub planner
        template_planner_message = [SystemMessagePromptTemplate(prompt=PromptTemplate( \
            input_variables=['output_format', 'output_format_empty', 'tools'], template='# Prompt\n\nObjective:\nYour objective is to create a sequential workflow based on the users query.\n\nCreate a plan represented in JSON by only using the tools listed below. The workflow should be a JSON array containing only the tool name, function name and input. A step in the workflow can receive the output from a previous step as input. \n\nOutput example 1:\n{output_format}\n\nIf no tools are needed to address the user query, follow the following JSON format.\n\nOutput example 2:\n"{output_format_empty}"\n\nTools: {tools}\n\nYou MUST STRICTLY follow the above provided output examples. Only answer with the specified JSON format, no other text')),\
            HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['chat_history', 'input'], template='Chat History:\n\n{chat_history}\n\nQuery: {input}'))]

        planner_output_format = '''
        {
            "steps": 
            [
                {
                    "name": "Tool name 1",
                    "input": {
                        "query": str
                    },
                    "output": "result_1"
                },
                {
                    "name": "Tool name 2",
                    "input": {
                        "input": "<result_1>"
                    },
                    "output": "result_2"
                },
                {
                    "name": "Tool name 3",
                    "input": {
                        "query": str
                    },
                    "ouput": "result_3"
                }
            ]
        }
        '''
        # "goal": "Retrieve an email from the inbox using <Tool name 1>",
        planner_output_empty_format = '''
        {
            "steps": []
        }
        '''

        # Set up prompt template for the hub planner
        self.template_planner = ChatPromptTemplate(
            input_variables=['output_format', 'output_format_empty', 'tools', 'chat_history', 'input'], 
            messages= template_planner_message
        )
        
        self.template_planner = self.template_planner.partial(output_format=planner_output_format, output_format_empty=planner_output_empty_format)
        
        # Set up prompt template message for vanilla spoke
        template_llm_message = """You are a chatbot having a conversation with a human.
        
        {chat_history}
        
        Human: {input}
        Chatbot:"""

        # Set up prompt template for vanilla spoke
        self.template_llm = PromptTemplate(
            input_variables=["chat_history", "input"], template=template_llm_message
        )

        # Set up prompt template message for spoke execution
        spoke_prompt_messages = [SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['tool_names', 'tools'], template='Respond to the human as helpfully and accurately as possible. You have access to the following tools:\n\n{tools}\n\nUse a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).\n\nValid "action" values: "Final Answer" or {tool_names}\n\nProvide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{\n  "action": $TOOL_NAME,\n  "action_input": $INPUT\n}}\n```\n\nFollow this format:\n\nQuestion: input question to answer\nThought: consider previous and subsequent steps\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat Thought/Action/Observation N times)\nThought: I know what to respond\nAction:\n```\n{{\n  "action": "Final Answer",\n  "action_input": "Final response to human"\n}}\n\nBegin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation')), \
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entity_history'], template='Chat history:\n\n{summary_history}\n\nEntity history:\n\n{entities}\n\nQuestion: {input}\n\n{agent_scratchpad}\n (reminder to respond in a JSON blob no matter what)'))]

        # Set up prompt template for spoke execution
        self.spoke_prompt = ChatPromptTemplate(input_variables=['agent_scratchpad', 'input', 'summary_history', 'entities', 'tool_names', 'tools'], messages=spoke_prompt_messages)
        