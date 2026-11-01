"""Agent configuration and definitions."""
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any
from src.agents.tools import (
    search_knowledge_base,
    create_support_ticket,
    get_account_details,
    lookup_customer_crm,
    get_product_info,
    check_eligibility,
    get_transaction_history,
    file_dispute,
    get_spending_summary,
)


@dataclass
class ToolDefinition:
    """Tool definition with schema and callable."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    callable: Callable


@dataclass
class Agent:
    """Agent configuration."""
    voice_id: str
    instruction: str
    tools: List[ToolDefinition] = field(default_factory=list)

    def __post_init__(self):
        if not self.voice_id:
            raise ValueError("voice_id required")
        if not self.instruction:
            raise ValueError("instruction required")


# Shared prompt sections, written to the Nova Sonic 2.5 prompting guide:
# one header convention, one rule per bullet, positive framing, silent tool-call turns.
_STYLE = (
    "[STYLE]\n"
    "- Be warm, professional, and helpful. Sound natural, direct, and human.\n"
    "- Answer the caller's question in 1-2 sentences, then expand only enough to be clear, "
    "3-5 short sentences total.\n"
    "- Speak in plain conversational sentences, like a phone call rather than a lecture or essay.\n"
)

_TOOL_RULES = (
    "[TOOL RULES]\n"
    "- When you call a tool, call it as your entire response for that turn and speak no words.\n"
    "- Call each tool at most once per turn, then speak to the caller about the result.\n"
    "- State that an action is done, and speak any ticket or reference number, "
    "only after the tool has returned it, using the tool's exact value.\n"
)

_TRANSFER_RULES = (
    "[TRANSFERS]\n"
    "- When the request belongs to another team, ask the caller whether they would like to be transferred, "
    "and wait for their answer.\n"
    "- After the caller agrees, call switch_agent with that team as your entire response.\n"
    "- If the caller prefers to stay, keep helping within your own area.\n"
)

_FINAL_CHECK = (
    "[FINAL CHECK]\n"
    "- Is this reply within my team's area?\n"
    "- If this turn is a tool call, is the tool call my whole response?\n"
    "- Does every number or confirmation I speak come from a tool result?\n"
    "- Is the reply 3-5 short spoken sentences with no lists?"
)


def _build_instruction(role: str, workflow: str, example: str) -> str:
    """Assemble an agent's system prompt from its own sections plus the shared ones."""
    return "\n".join([role, _STYLE, workflow, _TOOL_RULES, _TRANSFER_RULES, example, _FINAL_CHECK])


AGENTS = {
    "customer_support": Agent(
        voice_id="matthew",
        instruction=_build_instruction(
            role=(
                "[ROLE]\n"
                "- You are Matthew, a customer support specialist at a bank, for the whole conversation.\n"
                "- You handle account problems, complaints, frequently asked questions, and support tickets.\n"
            ),
            workflow=(
                "[WORKFLOW]\n"
                "- Acknowledge the issue and ask for the caller's customer ID if you do not have it yet.\n"
                "- Use search_knowledge_base to find the answer to the caller's question.\n"
                "- Use get_account_details with the customer ID before answering anything specific to their account.\n"
                "- If the issue is still unresolved, use create_support_ticket and share the ticket number it returns.\n"
            ),
            example=(
                "[EXAMPLE]\n"
                "Caller: My debit card keeps getting declined.\n"
                "Matthew: I'm sorry, that's frustrating. Could you tell me your customer ID so I can check your account?\n"
            ),
        ),
        tools=[
            ToolDefinition(
                name="search_knowledge_base",
                description="Searches the help center for answers to a customer question. Returns matching articles to explain to the caller.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The customer's question or issue to search for"}
                    },
                    "required": ["query"]
                },
                callable=search_knowledge_base
            ),
            ToolDefinition(
                name="create_support_ticket",
                description="Opens a support ticket for an issue that could not be resolved on the call. Returns the ticket number and expected response time.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_description": {"type": "string", "description": "Description of the customer's issue"},
                        "customer_id": {"type": "string", "description": "The customer's ID"},
                        "priority": {"type": "string", "description": "Ticket priority", "enum": ["low", "medium", "high"]}
                    },
                    "required": ["issue_description", "customer_id"]
                },
                callable=create_support_ticket
            ),
            ToolDefinition(
                name="get_account_details",
                description="Looks up a customer's profile and their account IDs from their customer ID. Use before answering account-specific questions.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer's ID"}
                    },
                    "required": ["customer_id"]
                },
                callable=get_account_details
            ),
        ]
    ),
    "banking_services": Agent(
        voice_id="amy",
        instruction=_build_instruction(
            role=(
                "[ROLE]\n"
                "- You are Amy, a banking services specialist, for the whole conversation.\n"
                "- You handle credit cards, loans, savings and checking accounts, and eligibility.\n"
            ),
            workflow=(
                "[WORKFLOW]\n"
                "- Ask for the caller's customer ID if you do not have it yet.\n"
                "- Use lookup_customer_crm to understand the caller's relationship with the bank.\n"
                "- Use get_product_info to describe a card, loan, or account.\n"
                "- Use check_eligibility before telling the caller whether they qualify.\n"
            ),
            example=(
                "[EXAMPLE]\n"
                "Caller: What kind of savings accounts do you have?\n"
                "Amy: We have a high-yield savings account that a lot of customers like. "
                "Would you like the rate and the minimum balance?\n"
            ),
        ),
        tools=[
            ToolDefinition(
                name="lookup_customer_crm",
                description="Looks up a customer's relationship with the bank from their customer ID, including products they hold and current offers.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer's ID"}
                    },
                    "required": ["customer_id"]
                },
                callable=lookup_customer_crm
            ),
            ToolDefinition(
                name="get_product_info",
                description="Returns rates, fees, and features for one banking product.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "product_type": {"type": "string", "description": "Type of banking product", "enum": ["credit_card", "personal_loan", "savings_account", "checking_account"]}
                    },
                    "required": ["product_type"]
                },
                callable=get_product_info
            ),
            ToolDefinition(
                name="check_eligibility",
                description="Checks whether a customer qualifies for a banking product. Returns the eligibility outcome to share with the caller.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "The customer's ID"},
                        "product_type": {"type": "string", "description": "Type of product to check eligibility for", "enum": ["credit_card", "personal_loan", "savings_account", "checking_account"]}
                    },
                    "required": ["customer_id", "product_type"]
                },
                callable=check_eligibility
            ),
        ]
    ),
    "transactions": Agent(
        voice_id="tiffany",
        instruction=_build_instruction(
            role=(
                "[ROLE]\n"
                "- You are Tiffany, a transactions specialist, for the whole conversation.\n"
                "- You handle transaction history, disputes, and spending insights.\n"
            ),
            workflow=(
                "[WORKFLOW]\n"
                "- Ask for the account ID of the account in question if you do not have it yet. "
                "An account ID looks like CHK-7821 and is different from the customer ID.\n"
                "- Use get_transaction_history to review recent activity.\n"
                "- Use file_dispute once the caller has confirmed which transaction to dispute and why.\n"
                "- Use get_spending_summary for spending insights and alerts.\n"
            ),
            example=(
                "[EXAMPLE]\n"
                "Caller: I think I was charged twice for something.\n"
                "Tiffany: That's worth checking right away. Which account was the charge on? "
                "The account ID is fine.\n"
            ),
        ),
        tools=[
            ToolDefinition(
                name="get_transaction_history",
                description="Returns recent transactions and the current balance for an account ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string", "description": "The account ID, for example CHK-7821"},
                        "days": {"type": "integer", "description": "Number of days of history to retrieve", "default": 30}
                    },
                    "required": ["account_id"]
                },
                callable=get_transaction_history
            ),
            ToolDefinition(
                name="file_dispute",
                description="Files a dispute for one transaction the caller has confirmed. Returns the dispute number and next steps.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string", "description": "The account ID"},
                        "transaction_id": {"type": "string", "description": "The transaction ID to dispute"},
                        "reason": {"type": "string", "description": "Reason for the dispute"}
                    },
                    "required": ["account_id", "transaction_id", "reason"]
                },
                callable=file_dispute
            ),
            ToolDefinition(
                name="get_spending_summary",
                description="Returns spending by category and any monitoring alerts for an account ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string", "description": "The account ID"},
                        "month": {"type": "string", "description": "Month to summarize (default: current)", "default": "current"}
                    },
                    "required": ["account_id"]
                },
                callable=get_spending_summary
            ),
        ]
    ),
}
