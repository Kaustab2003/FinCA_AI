"""
Agents package - AI agent implementations
"""
from src.agents.base_agent import BaseAgent, AgentResponse
from src.agents.supervisor import SupervisorAgent
from src.agents.tax_agent import TaxCalculatorAgent
from src.agents.investment_agent import InvestmentAdvisorAgent
from src.agents.debt_agent import DebtManagerAgent
from src.agents.legal_agent import LegalAssistantAgent
from src.agents.expense_categorization_agent import ExpenseCategorizationAgent
from src.agents.insights_agent import InsightsAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.agents.document_parsing_agent import DocumentParsingAgent
from src.agents.conversational_data_entry_agent import ConversationalDataEntryAgent
from src.agents.behavioral_analysis_agent import BehavioralAnalysisAgent
from src.agents.calculation_explanation_agent import CalculationExplanationAgent

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'SupervisorAgent',
    'TaxCalculatorAgent',
    'InvestmentAdvisorAgent',
    'DebtManagerAgent',
    'LegalAssistantAgent',
    'ExpenseCategorizationAgent',
    'InsightsAgent',
    'RecommendationAgent',
    'DocumentParsingAgent',
    'BehavioralAnalysisAgent',
    'ConversationalDataEntryAgent',
    'CalculationExplanationAgent'
]
