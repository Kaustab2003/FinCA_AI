"""
Agents package - AI agent implementations
"""
from src.agents.base_agent import BaseAgent, AgentResponse
from src.agents.supervisor import SupervisorAgent
from src.agents.tax_agent import TaxCalculatorAgent
from src.agents.investment_agent import InvestmentAdvisorAgent
from src.agents.debt_agent import DebtManagerAgent
from src.agents.legal_agent import LegalAssistantAgent

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'SupervisorAgent',
    'TaxCalculatorAgent',
    'InvestmentAdvisorAgent',
    'DebtManagerAgent',
    'LegalAssistantAgent'
]
