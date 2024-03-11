from __future__ import annotations

import json
import logging
import re
from typing import Optional, Union, Any, List

from langchain.agents.agent import AgentOutputParser
from langchain.agents.structured_chat.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

logger = logging.getLogger(__name__)

# Library for validating root domains
from helpers.sandbox.sandbox import is_request_allowed


class SpokeParser(AgentOutputParser):
    """Output parser for the structured chat agent."""

    pattern = re.compile(r"```(?:json)?\n([\s\S]*?)\n```", re.DOTALL)  #r"```(?:json)?\n(.*?)```"
    functionality_list: Optional[List[str]] = None
    spoke_operator: Optional[Any] = None 
    
    called_functionalities: Optional[dict] = {}

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            action_match = self.pattern.search(text)
            if action_match is not None:
                response = json.loads(action_match.group(1).strip(), strict=False)
                if isinstance(response, list):
                    # gpt turbo frequently ignores the directive to emit a single action
                    logger.warning("Got multiple action responses: %s", response)
                    response = response[0]
                if response["action"] == "Final Answer":
                    return AgentFinish({"output": response["action_input"]}, text)
                elif response["action"] in self.functionality_list:
                    request_functionality = response["action"]
                    action_dict = response.get("action_input", {})  
                    
                    if request_functionality not in self.called_functionalities:
                        message_type, request_schema, response_schema = self.spoke_operator.probe_functionality(request_functionality)
                        
                        if message_type != "function_probe_response" or request_schema is None or response_schema is None:
                            message = f"Could not probe {request_functionality} functionality. YOU MUST NOT PROBE {request_functionality} AGAIN!"
                            # return AgentFinish({"output": message}, text)
                            return AgentAction("message_spoke", message, text)
                        
                        self.called_functionalities[request_functionality] = {}
                        self.called_functionalities[request_functionality]["request_schema"] = request_schema
                        self.called_functionalities[request_functionality]["response_schema"] = response_schema
                    
                    else:
                        request_schema = self.called_functionalities[request_functionality]["request_schema"]
                        response_schema = self.called_functionalities[request_functionality]["response_schema"]

                    is_formatted = self.spoke_operator.check_format(request_schema, action_dict)
                    if is_formatted:
                        message_type, response = self.spoke_operator.make_request(request_functionality, action_dict)
                        if message_type != "app_response":
                            message = f"Could not make request to {request_functionality}. YOU MUST NOT REQUEST {request_functionality} AGAIN!"
                            # return AgentFinish({"output": message}, text)
                            return AgentAction("message_spoke", message, text)
                        
                        is_response_formatted = self.spoke_operator.check_format(response_schema, response)
                        
                        if is_response_formatted:
                            message = str(response)
                            return AgentAction("message_spoke", message, text)
                        else:
                            message = request_functionality+"s' response is not well formatted"
                            return AgentAction("message_spoke", message, text)                        
                    else:
                        message  = "Create an functionality request based on this specification (Note: Include necessary properties): "+str(request_schema["properties"])
                        return AgentAction("message_spoke", message, text)
                    
                else:
                    action_input = response.get("action_input", {})
                    if "url" in list(action_input.keys()):
                        url = action_input["url"]
                        if not is_request_allowed(url):
                            message = f"The request to {url} is denied! DO NOT REQUEST {url} AGAIN."
                            return AgentAction("message_spoke", message, text)
                          
                    return AgentAction(
                        response["action"], action_input, text
                    ) 
            else:
                return AgentFinish({"output": text}, text)
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "structured_chat"