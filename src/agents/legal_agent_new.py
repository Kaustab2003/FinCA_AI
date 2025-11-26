"""
LegalAssistantAgent - Financial law and compliance guidance (Updated with Groq/DeepSeek)
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.config.settings import settings
from src.utils.logger import logger


class LegalAssistantAgent(BaseAgent):
    """Specialized agent for financial legal queries and compliance"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        
        provider_info = self.ai_client.get_provider_info()
        logger.info(f"Initialized LegalAssistantAgent with {provider_info['provider']} ({provider_info['model']})")
    
    def _get_agent_type(self) -> str:
        return "legal"
    
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Process legal queries"""
        try:
            # Check if AI is available
            if not self.ai_client.is_available():
                return self._get_fallback_response(query, user_context)
            
            system_prompt = self._build_system_prompt()
            system_prompt += f"""

You are a financial legal advisor with expertise in Indian laws.

REGULATORY BODIES:
- RBI: Banking, lending, forex
- SEBI: Securities, mutual funds, stock market
- IRDAI: Insurance
- PFRDA: Pension and retirement funds

KEY FINANCIAL LAWS:
1. Income Tax Act, 1961
2. Banking Regulation Act, 1949
3. SEBI Act, 1992
4. Insurance Act, 1938
5. Consumer Protection Act, 2019

COMMON LEGAL SCENARIOS:

1. Loan Default:
   - 90-day NPA classification
   - SARFAESI Act for recovery
   - One-time settlement (OTS) option
   - Credit score impact

2. Nominee vs Legal Heir:
   - Nominee is trustee, not owner
   - Will supersedes nomination
   - Legal heirs have actual rights

3. Investment Fraud:
   - Report to SEBI/RBI/Police
   - File complaint in consumer forum
   - Check SEBI registered advisors

4. Insurance Claims:
   - Free look period: 15-30 days
   - Claim rejection: Appeal to ombudsman
   - Grace period for premium payment

5. Credit Score Disputes:
   - Free report once/year from CIBIL
   - Dispute errors within 30 days
   - Check all 4 bureaus

IMPORTANT DISCLAIMERS:
- This is general information, not legal advice
- Consult a lawyer for specific cases
- Laws change, verify current regulations
- Document everything in writing

User profile: Age {user_context.get('age', 25)}, Income {self._format_currency(user_context.get('salary', 0))}

Provide accurate legal information with appropriate disclaimers.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            content = self.ai_client.chat_completion(messages, temperature=0.2, max_tokens=1200)
            
            # Add disclaimer
            content += "\n\n⚠️ **Disclaimer**: This is general information only, not legal advice. For specific legal matters, please consult a qualified lawyer."
            
            provider_info = self.ai_client.get_provider_info()
            logger.info(f"Legal query processed with {provider_info['provider']}")
            
            return AgentResponse(
                content=content,
                agent_name=f"Legal Assistant ({provider_info['provider'].title()})",
                agent_type="legal",
                confidence=0.85,
                tools_used=['legal_kb', provider_info['model']],
                metadata={
                    'provider': provider_info['provider'],
                    'model': provider_info['model'],
                    'is_free': provider_info['is_free'],
                    'disclaimer_added': True
                }
            )
            
        except Exception as e:
            logger.error("Legal agent processing failed", error=str(e))
            return self._get_fallback_response(query, user_context)
    
    def _get_fallback_response(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Provide fallback response when AI is unavailable"""
        
        fallback_response = """**Financial Legal Information**

Here's general guidance on common financial legal matters in India:

**1. Loan Default & Recovery**
- Banks can't seize assets without court order
- 90-day notice before NPA classification
- Right to one-time settlement (OTS)
- Check SARFAESI Act provisions
- Credit score impact lasts 7 years

**2. Insurance Claims**
- Free-look period: 15-30 days to cancel
- Claim rejection: Appeal to Insurance Ombudsman
- Keep all documents: Policy, medical records, FIR
- Grace period for premium payment (usually 30 days)
- Nominee vs beneficiary distinction

**3. Investment Fraud**
- Report to SEBI (securities), RBI (banking), Cyber Crime
- File FIR within 3 months for better action
- Check SEBI registered advisors at sebi.gov.in
- Avoid guaranteed return schemes (illegal)
- Ponzi schemes: Report immediately

**4. Nominee vs Legal Heir**
- Nominee is trustee, not owner
- Legal heirs have actual inheritance rights
- Will supersedes nomination
- Update nominee after life events
- Joint accounts: Survivorship rules apply

**5. Credit Score Issues**
- Free CIBIL report once/year
- Dispute errors within 30 days
- Score improves over 6-12 months with good behavior
- Check all 4 bureaus: CIBIL, Experian, Equifax, CRIF
- Hard inquiries affect score temporarily

**6. Consumer Rights (Financial Products)**
- Banking Ombudsman for bank disputes
- Insurance Ombudsman for insurance issues
- SEBI SCORES for investment complaints
- File within time limits (usually 1 year)
- Free grievance redressal

**Key Regulations:**
- RBI: Banking & lending regulations
- SEBI: Investment & securities laws
- IRDAI: Insurance regulations
- Income Tax Act: Tax compliance
- Consumer Protection Act: Rights & remedies

**Important Numbers:**
- Banking Ombudsman: 1800 222 0001
- SEBI Complaints: 1800 266 7575
- Cyber Crime: 1930
- Consumer Helpline: 1915

⚠️ **Important Disclaimer**: This is general information only, not legal advice. Laws are complex and change frequently. For specific legal matters, please consult a qualified lawyer or legal professional.

*Using smart fallback mode with verified legal information*
"""
        
        return AgentResponse(
            content=fallback_response,
            agent_name="Legal Assistant (Fallback)",
            agent_type="legal",
            confidence=0.75,
            tools_used=['fallback_mode', 'legal_kb'],
            metadata={'fallback': True, 'reason': 'AI provider unavailable', 'disclaimer_added': True}
        )
