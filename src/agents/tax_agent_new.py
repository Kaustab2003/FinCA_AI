"""
TaxCalculatorAgent - Income tax calculations and advice for India (Updated with Groq/DeepSeek)
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.config.settings import settings
from src.utils.logger import logger


class TaxCalculatorAgent(BaseAgent):
    """Specialized agent for Indian income tax calculations and advice"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        
        # Tax slabs for FY 2024-25 (AY 2025-26)
        self.old_regime_slabs = [
            (250000, 0),
            (500000, 0.05),
            (1000000, 0.20),
            (float('inf'), 0.30)
        ]
        
        self.new_regime_slabs = [
            (300000, 0),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float('inf'), 0.30)
        ]
        
        provider_info = self.ai_client.get_provider_info()
        logger.info(f"Initialized TaxCalculatorAgent with {provider_info['provider']} ({provider_info['model']})")
    
    def _get_agent_type(self) -> str:
        return "tax"
    
    def calculate_tax(self, income: float, regime: str = "new", deductions: Dict[str, float] = None) -> Dict[str, Any]:
        """Calculate income tax for FY 2024-25"""
        if deductions is None:
            deductions = {}
        
        taxable_income = income
        total_deductions = 0
        
        # Old regime allows deductions
        if regime == "old":
            # Section 80C (max 1.5L)
            section_80c = min(deductions.get('80c', 0), 150000)
            # Section 80D (25K-50K based on age)
            section_80d = min(deductions.get('80d', 0), 50000)
            # HRA
            hra = deductions.get('hra', 0)
            # Home loan interest (max 2L)
            home_loan = min(deductions.get('home_loan_interest', 0), 200000)
            
            total_deductions = section_80c + section_80d + hra + home_loan
            taxable_income = max(income - total_deductions, 0)
        
        # Calculate tax based on regime
        slabs = self.old_regime_slabs if regime == "old" else self.new_regime_slabs
        tax = 0
        prev_slab = 0
        
        for slab_limit, rate in slabs:
            if taxable_income > prev_slab:
                taxable_in_slab = min(taxable_income, slab_limit) - prev_slab
                tax += taxable_in_slab * rate
                prev_slab = slab_limit
            else:
                break
        
        # 4% cess
        cess = tax * 0.04
        total_tax = tax + cess
        
        # Rebate under section 87A (if income < 7L)
        rebate = 0
        if taxable_income <= 700000:
            rebate = min(total_tax, 25000 if regime == "new" else 12500)
        
        final_tax = max(total_tax - rebate, 0)
        
        return {
            'regime': regime,
            'gross_income': income,
            'total_deductions': total_deductions,
            'taxable_income': taxable_income,
            'tax_before_cess': tax,
            'cess': cess,
            'rebate': rebate,
            'final_tax': final_tax,
            'effective_tax_rate': (final_tax / income * 100) if income > 0 else 0
        }
    
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Process tax-related queries"""
        try:
            # Check if AI is available
            if not self.ai_client.is_available():
                return self._get_fallback_response(query, user_context)
            
            salary = user_context.get('salary', 1200000)
            old_tax = self.calculate_tax(salary, 'old', {'80c': 150000, '80d': 25000})
            new_tax = self.calculate_tax(salary, 'new')
            
            system_prompt = self._build_system_prompt()
            system_prompt += f"""

You are an expert Indian income tax advisor for FY 2024-25.

USER PROFILE:
- Annual Income: {self._format_currency(salary)}
- Old Regime Tax: {self._format_currency(old_tax['final_tax'])}
- New Regime Tax: {self._format_currency(new_tax['final_tax'])}

TAX REGIME COMPARISON (FY 2024-25):

OLD REGIME:
- Slabs: 0% up to ₹2.5L, 5% (2.5-5L), 20% (5-10L), 30% (>10L)
- Deductions: 80C (₹1.5L), 80D (₹25-50K), HRA, Home loan interest (₹2L)
- Standard deduction: ₹50K (salaried)

NEW REGIME (Default):
- Slabs: 0% up to ₹3L, 5% (3-6L), 10% (6-9L), 15% (9-12L), 20% (12-15L), 30% (>15L)
- No deductions (except employer contributions)
- Standard deduction: ₹50K (salaried)
- Rebate: Full tax waiver if income < ₹7L

KEY DEDUCTIONS (Old Regime):
1. Section 80C (₹1.5L max): PPF, ELSS, EPF, Life insurance, Home loan principal
2. Section 80D (₹25K-50K): Health insurance premiums
3. Section 80CCD(1B): Additional ₹50K for NPS
4. HRA: Actual HRA received (subject to limits)
5. Home loan interest: ₹2L max (self-occupied)

RECOMMENDATIONS:
- Choose OLD if: Have home loan, make 80C investments, high medical expenses
- Choose NEW if: No deductions, prefer simplicity, income < ₹7L or > ₹15L

Provide personalized tax advice based on user's profile.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            content = self.ai_client.chat_completion(messages, temperature=0.2, max_tokens=1200)
            
            provider_info = self.ai_client.get_provider_info()
            logger.info(f"Tax query processed with {provider_info['provider']}")
            
            return AgentResponse(
                content=content,
                agent_name=f"Tax Calculator ({provider_info['provider'].title()})",
                agent_type="tax",
                confidence=0.90,
                tools_used=['tax_calculator', 'regime_comparator', provider_info['model']],
                metadata={
                    'provider': provider_info['provider'],
                    'model': provider_info['model'],
                    'is_free': provider_info['is_free']
                }
            )
            
        except Exception as e:
            logger.error("Tax agent processing failed", error=str(e))
            return self._get_fallback_response(query, user_context)
    
    def _get_fallback_response(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Provide fallback response when AI is unavailable"""
        salary = user_context.get('salary', 1200000)
        old_tax = self.calculate_tax(salary, 'old', {'80c': 150000, '80d': 25000})
        new_tax = self.calculate_tax(salary, 'new')
        
        fallback_response = f"""**Tax Regime Comparison (FY 2024-25)**

For annual income of ₹{salary:,.0f}:

**Old Tax Regime:**
- Tax: ₹{old_tax['final_tax']:,.0f}
- With 80C (₹1.5L) & 80D (₹25K) deductions
- Effective rate: {old_tax['effective_tax_rate']:.2f}%
- Available deductions: 80C, 80D, HRA, Home loan

**New Tax Regime:**
- Tax: ₹{new_tax['final_tax']:,.0f}
- No deductions (simpler)
- Effective rate: {new_tax['effective_tax_rate']:.2f}%
- Lower tax slabs

**Recommendation:**
{'Choose **Old Regime** - Save ₹' + f"{new_tax['final_tax'] - old_tax['final_tax']:,.0f}" if old_tax['final_tax'] < new_tax['final_tax'] else 'Choose **New Regime** - Save ₹' + f"{old_tax['final_tax'] - new_tax['final_tax']:,.0f}"}

**Old Regime is better if you:**
- Have home loan (interest deduction up to ₹2L)
- Invest in 80C instruments (PPF, ELSS, EPF)
- Pay health insurance premiums (80D)
- Receive HRA

**New Regime is better if you:**
- Don't have many deductions
- Prefer simplicity
- Income < ₹7L (get rebate) or > ₹15L

**Tax Saving Tips:**
1. Max out 80C (₹1.5L): ELSS, PPF, EPF
2. 80D (₹25K-50K): Health insurance
3. NPS additional (₹50K): 80CCD(1B)
4. Home loan: Principal (80C) + Interest (deduction)

*Using smart fallback mode with real tax calculations*
"""
        
        return AgentResponse(
            content=fallback_response,
            agent_name="Tax Calculator (Fallback)",
            agent_type="tax",
            confidence=0.85,
            tools_used=['fallback_mode', 'tax_calculator'],
            metadata={'fallback': True, 'reason': 'AI provider unavailable'}
        )
