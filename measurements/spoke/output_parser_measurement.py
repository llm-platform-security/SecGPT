from __future__ import annotations

import json
import logging
import re
from typing import Optional, Union, Any, List

from langchain.agents.agent import AgentOutputParser
from langchain.agents.structured_chat.prompt import FORMAT_INSTRUCTIONS
from langchain.output_parsers import OutputFixingParser
from langchain.pydantic_v1 import Field
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.schema.language_model import BaseLanguageModel

logger = logging.getLogger(__name__)


class SpokeParser(AgentOutputParser):
    """Output parser for the structured chat agent."""

    pattern = re.compile(r"```(?:json)?\n([\s\S]*?)\n```", re.DOTALL)  #r"```(?:json)?\n(.*?)```"
    functionality_list: Optional[List[str]] = None
    spoke_operator: Optional[Any] = None 


    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # try:
        action_match = self.pattern.search(text)
        if action_match is not None:
            # print("__________________________________________________")
            # print(text)
            # print("+++++++++++++++++++++++++++++++++++++++++++++")
            # print(action_match.group(1))
            # # print(action_match.group(1).strip())
            # print("__________________________________________________")
            response = json.loads(action_match.group(1).strip(), strict=False)
            if isinstance(response, list):
                # gpt turbo frequently ignores the directive to emit a single action
                logger.warning("Got multiple action responses: %s", response)
                response = response[0]
            if response["action"] == "Final Answer":
                return AgentFinish({"output": response["action_input"]}, text)
            elif response["action"] in self.functionality_list:
                request_functionality = response["action"]
                request_schema = self.spoke_operator.probe_functionality(request_functionality)
                action_dict = response.get("action_input", {})  
                functionality_response = self.spoke_operator.make_request(request_functionality, action_dict)
                return AgentAction("message_spoke", str(functionality_response), text)
                
            else:
                return AgentAction(
                    response["action"], response.get("action_input", {}), text
                )
        else:
            return AgentFinish({"output": text}, text)
        # except Exception as e:
        #     raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "structured_chat"
