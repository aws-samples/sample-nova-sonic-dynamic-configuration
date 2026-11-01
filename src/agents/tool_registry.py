"""Unified tool registry derived from agent configurations."""
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, NamedTuple

from src.agents.agent_config import Agent, ToolDefinition


class ToolEntry(NamedTuple):
    """Internal storage for a registered tool."""
    callable: Callable
    schema: Dict[str, Any]


# Teams the caller can be transferred to, described for the switch_agent role parameter.
SWITCH_AGENT_ROLES: Dict[str, str] = {
    "customer_support": "account problems, complaints, frequently asked questions, support tickets",
    "banking_services": "credit cards, loans, savings and checking accounts, eligibility",
    "transactions": "transaction history, disputes, spending insights",
}


def build_switch_agent_schema(current_agent: str) -> Dict[str, Any]:
    """Build the switch_agent schema, offering only teams other than the current agent."""
    roles = {name: desc for name, desc in SWITCH_AGENT_ROLES.items() if name != current_agent}
    return {
        "toolSpec": {
            "name": "switch_agent",
            "description": (
                "Transfers the caller to another team, after the caller has agreed to the transfer. "
                "The new team continues the conversation with the full history."
            ),
            "inputSchema": {
                "json": json.dumps({
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "enum": list(roles),
                            "description": " ".join(f"{name}: {desc}." for name, desc in roles.items()),
                        }
                    },
                    "required": ["role"],
                })
            },
        }
    }


class ToolRegistry:
    """Single source of truth for tool schemas and callables, derived from agent configs."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolEntry] = {}
        self._agent_tool_names: Dict[str, List[str]] = {}

    def register(self, name: str, callable: Callable, schema: Dict[str, Any]) -> None:
        """Register a tool by name with its callable and schema."""
        self._tools[name] = ToolEntry(callable=callable, schema=schema)

    def get_schemas_for_agent(
        self, agent_name: str, agents: Dict[str, Agent]
    ) -> List[Dict[str, Any]]:
        """Return Bedrock-compatible tool schema list for an agent, including switch_agent."""
        schemas: List[Dict[str, Any]] = [build_switch_agent_schema(agent_name)]

        tool_names = self._agent_tool_names.get(agent_name, [])
        for name in tool_names:
            entry = self._tools.get(name)
            if entry is not None:
                schemas.append({
                    "toolSpec": {
                        "name": name,
                        "description": entry.schema.get("description", ""),
                        "inputSchema": {
                            "json": json.dumps(entry.schema.get("input_schema", {}))
                        },
                    }
                })

        return schemas

    async def execute(
        self, tool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Look up and execute a tool by name. Returns error dict for unknown tools."""
        entry = self._tools.get(tool_name)
        if entry is None:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            # Parse string content to dict if needed (matches ToolProcessor behavior)
            if isinstance(params.get("content"), str):
                params = json.loads(params["content"])
            elif "content" in params:
                params = params["content"]
            return await entry.callable(**params)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    @classmethod
    def from_agents(cls, agents: Dict[str, Agent]) -> "ToolRegistry":
        """Build registry from agent configurations."""
        registry = cls()

        for agent_name, agent in agents.items():
            tool_names: List[str] = []
            for tool_def in agent.tools:
                tool_names.append(tool_def.name)
                # Only register once (tools may be shared across agents)
                if tool_def.name not in registry._tools:
                    registry.register(
                        name=tool_def.name,
                        callable=tool_def.callable,
                        schema={
                            "description": tool_def.description,
                            "input_schema": tool_def.input_schema,
                        },
                    )
            registry._agent_tool_names[agent_name] = tool_names

        return registry
