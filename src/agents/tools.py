"""Tool implementations for banking multi-agent system."""
from typing import Dict, Any


# --- Customer Support Agent Tools ---

async def search_knowledge_base(query: str) -> Dict[str, Any]:
    """Search the knowledge base for answers to customer questions."""
    return {
        "status": "success",
        "results": [
            {"title": "Password Reset", "content": f"To resolve '{query}': Navigate to Settings > Security > Reset Password. If locked out, contact support for manual verification."},
            {"title": "General FAQ", "content": "Our support team is available 24/7 via chat, phone, or email."}
        ]
    }


async def create_support_ticket(issue_description: str, customer_id: str, priority: str = "medium") -> Dict[str, Any]:
    """Create a support ticket for unresolved customer issues."""
    ticket_id = "TKT-48291"
    return {
        "status": "success",
        "ticket_id": ticket_id,
        "priority": priority,
        "speak": f"I've opened ticket {ticket_id} for you, and our team will get back to you within 4 hours.",
        "next": "Ask the caller if there is anything else you can help with."
    }


async def get_account_details(customer_id: str) -> Dict[str, Any]:
    """Retrieve customer account details for servicing."""
    return {
        "status": "success",
        "customer_id": customer_id,
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "+1-555-0142",
        "accounts": ["CHK-7821", "SAV-3344", "CC-9012"],
        "member_since": "2019-03-15",
        "tier": "Gold"
    }


# --- Banking Services Agent Tools ---

async def lookup_customer_crm(customer_id: str) -> Dict[str, Any]:
    """Look up customer profile and relationship history in CRM."""
    return {
        "status": "success",
        "customer_id": customer_id,
        "relationship_manager": "David Chen",
        "products_held": ["Checking", "Savings", "Credit Card"],
        "lifetime_value": "High",
        "last_interaction": "2026-06-01",
        "notes": "Interested in mortgage products. Pre-approved for premium credit card upgrade."
    }


async def get_product_info(product_type: str) -> Dict[str, Any]:
    """Retrieve detailed information about banking products."""
    products = {
        "credit_card": {
            "name": "Premium Rewards Card",
            "apr": "18.99%",
            "annual_fee": "$95",
            "rewards": "3x points on dining, 2x on travel, 1x everything else",
            "signup_bonus": "50,000 points after $3,000 spend in 90 days"
        },
        "personal_loan": {
            "name": "FlexLoan Personal",
            "apr_range": "6.99% - 15.49%",
            "amounts": "$5,000 - $50,000",
            "terms": "12 - 60 months",
            "funding_time": "Next business day"
        },
        "savings_account": {
            "name": "High-Yield Savings",
            "apy": "4.25%",
            "minimum_balance": "$500",
            "monthly_fee": "$0 with minimum balance",
            "features": "No withdrawal limits, FDIC insured"
        },
        "checking_account": {
            "name": "Everyday Checking",
            "monthly_fee": "$0 with direct deposit",
            "atm_network": "55,000+ fee-free ATMs",
            "features": "Mobile deposit, bill pay, Zelle"
        }
    }
    product = products.get(product_type, {"name": "Unknown", "details": "Product not found"})
    return {"status": "success", "product": product}


async def check_eligibility(customer_id: str, product_type: str) -> Dict[str, Any]:
    """Check customer eligibility for a banking product."""
    return {
        "status": "success",
        "customer_id": customer_id,
        "product_type": product_type,
        "credit_score_range": "740-760",
        "recommended_tier": "Premium",
        "summary": f"The customer qualifies and is pre-approved for the {product_type.replace('_', ' ')} at preferred rates."
    }


# --- Transactions Agent Tools ---

async def get_transaction_history(account_id: str, days: int = 30) -> Dict[str, Any]:
    """Retrieve transaction history for an account."""
    return {
        "status": "success",
        "account_id": account_id,
        "period": f"Last {days} days",
        "transactions": [
            {"date": "2026-06-10", "description": "Amazon.com", "amount": -89.99, "category": "Shopping"},
            {"date": "2026-06-09", "description": "Direct Deposit - Employer", "amount": 3250.00, "category": "Income"},
            {"date": "2026-06-08", "description": "Whole Foods Market", "amount": -67.43, "category": "Groceries"},
            {"date": "2026-06-07", "description": "Netflix", "amount": -15.99, "category": "Entertainment"},
            {"date": "2026-06-05", "description": "Shell Gas Station", "amount": -52.10, "category": "Transportation"},
        ],
        "balance": 8432.51
    }


async def file_dispute(account_id: str, transaction_id: str, reason: str) -> Dict[str, Any]:
    """File a dispute for a specific transaction."""
    dispute_id = "DSP-77201"
    return {
        "status": "success",
        "dispute_id": dispute_id,
        "account_id": account_id,
        "transaction_id": transaction_id,
        "reason": reason,
        "speak": f"I've filed dispute {dispute_id}. You'll see a provisional credit within 24 hours, and the investigation takes about 10 business days.",
        "next": "Ask the caller if there is anything else you can help with."
    }


async def get_spending_summary(account_id: str, month: str = "current") -> Dict[str, Any]:
    """Get spending summary and monitoring insights for an account."""
    return {
        "status": "success",
        "account_id": account_id,
        "month": month,
        "total_spending": 1842.30,
        "categories": {
            "Groceries": 412.50,
            "Dining": 289.00,
            "Transportation": 198.40,
            "Shopping": 534.20,
            "Entertainment": 108.20,
            "Bills & Utilities": 300.00
        },
        "alerts": [
            {"type": "budget_warning", "message": "Shopping spending is 20% above your monthly average"},
            {"type": "unusual_activity", "message": "No unusual activity detected this period"}
        ]
    }
