from datetime import datetime
from typing import Any, Optional
from python.helpers.extension import Extension
from python.helpers.mcp_handler import MCPConfig
from agent import Agent, LoopData
from python.helpers.localization import Localization


class SystemPrompt(Extension):

    async def execute(self, system_prompt: list[str] = [], loop_data: LoopData = LoopData(), **kwargs: Any):
        # append main system prompt and tools
        main = get_main_prompt(self.agent)
        tools = get_tools_prompt(self.agent)
        mcp_tools = get_mcp_tools_prompt(self.agent)

        system_prompt.append(main)
        system_prompt.append(tools)
        if mcp_tools:
            system_prompt.append(mcp_tools)


def get_main_prompt(agent: Agent):
    return agent.read_prompt("agent.system.main.md")


def get_tools_prompt(agent: Agent):
    prompt = agent.read_prompt("agent.system.tools.md")
    if agent.config.chat_model.vision:
        prompt += '\n' + agent.read_prompt("agent.system.tools_vision.md")

    # Add ACI tools information if available
    try:
        from python.helpers.aci_tool_interface import ACIToolInterface
        aci_interface = ACIToolInterface()
        if aci_interface.enabled:
            aci_prompt = agent.read_prompt("agent.system.tool.aci_tools.md")
            if aci_prompt:
                prompt += '\n\n' + aci_prompt

            # Add dynamic ACI tools information
            aci_tools_info = aci_interface.get_aci_tools_prompt()
            if aci_tools_info:
                prompt += '\n\n' + aci_tools_info
    except Exception as e:
        # Silently continue if ACI is not available
        pass

    return prompt


def get_mcp_tools_prompt(agent: Agent):
    mcp_config = MCPConfig.get_instance()
    if mcp_config.servers:
        pre_progress = agent.context.log.progress
        agent.context.log.set_progress("Collecting MCP tools") # MCP might be initializing, better inform via progress bar
        tools = MCPConfig.get_instance().get_tools_prompt()
        agent.context.log.set_progress(pre_progress) # return original progress
        return tools
    return ""
        
