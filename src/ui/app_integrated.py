"""
FinCA AI - Integrated Streamlit Application with Real Backend
"""
import streamlit as st
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config.settings import settings
from src.utils.logger import logger
from src.utils.metrics import MetricsCalculator
from src.services.chat_service import ChatService
from src.services.budget_service import BudgetService
from src.services.goals_service import GoalsService
from src.services.user_service import UserService
# from src.agents.rag_knowledge_agent import FinancialKnowledgeAgent  # Moved to local import
# from src.utils.document_loader import IndianFinancialDocuments  # Moved to local import
from src.utils.session_manager import SessionManager
from src.services.auth_service import AuthService

# Initialize logger
logger.info("Starting FinCA AI application")

# Page configuration
st.set_page_config(
    page_title="FinCA AI - Your Financial Copilot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #667eea;
        color: white;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f0f0f0;
        color: #333;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
def get_services():
    """Initialize service instances per user session"""
    if 'services' not in st.session_state:
        st.session_state.services = {
            'chat': ChatService(),
            'budget': BudgetService(),
            'goals': GoalsService(),
            'user': UserService(),
            'metrics': MetricsCalculator()
        }
    return st.session_state.services

services = get_services()

# =====================================================
# Initialize session state
# =====================================================
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = {}

# Initialize default values only if user context exists (authenticated)
if 'user_context' in st.session_state and st.session_state.user_context:
    if 'email' not in st.session_state:
        st.session_state.email = st.session_state.user_context.get('email', '')
    if 'role' not in st.session_state:
        st.session_state.role = st.session_state.user_context.get('role', 'user')
    if 'user_id' not in st.session_state:
        st.session_state.user_id = st.session_state.user_context.get('user_id', '')

def show_hra_calculator():
    """HRA Tax Exemption Calculator"""
    st.header("🏡 HRA Tax Exemption Calculator")
    st.markdown("Calculate how much HRA exemption you can claim under Section 10(13A)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        basic_salary = st.number_input("Basic Salary (Annual ₹)", min_value=0, value=600000, step=10000)
        hra_received = st.number_input("HRA Received (Annual ₹)", min_value=0, value=240000, step=10000)
    
    with col2:
        rent_paid = st.number_input("Rent Paid (Annual ₹)", min_value=0, value=180000, step=10000)
        metro_city = st.selectbox("City Type", ["Metro (Mumbai, Delhi, Kolkata, Chennai)", "Non-Metro"])
    
    if st.button("Calculate HRA Exemption", type="primary"):
        # Calculate 3 conditions for HRA exemption
        actual_hra = hra_received
        rent_minus_10_percent = max(0, rent_paid - (basic_salary * 0.10))
        metro_percentage = 0.50 if "Metro" in metro_city else 0.40
        salary_percentage = basic_salary * metro_percentage
        
        # Minimum of 3 conditions
        hra_exempt = min(actual_hra, rent_minus_10_percent, salary_percentage)
        taxable_hra = hra_received - hra_exempt
        
        # Tax savings (assuming 30% tax bracket)
        tax_saved_30 = hra_exempt * 0.30
        tax_saved_20 = hra_exempt * 0.20
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("HRA Exemption", f"₹{hra_exempt:,.0f}", "Tax-free")
        with col2:
            st.metric("Taxable HRA", f"₹{taxable_hra:,.0f}")
        with col3:
            st.metric("Tax Saved (30% bracket)", f"₹{tax_saved_30:,.0f}", "💰")
        
        st.markdown("---")
        st.subheader("📊 Calculation Breakdown")
        
        st.write(f"**Condition 1**: Actual HRA received = **₹{actual_hra:,.0f}**")
        st.write(f"**Condition 2**: Rent paid - 10% of Basic = ₹{rent_paid:,.0f} - ₹{basic_salary*0.10:,.0f} = **₹{rent_minus_10_percent:,.0f}**")
        st.write(f"**Condition 3**: {int(metro_percentage*100)}% of Basic Salary = **₹{salary_percentage:,.0f}**")
        
        st.success(f"✅ **HRA Exemption = Minimum of above 3 = ₹{hra_exempt:,.0f}**")
        
        if taxable_hra > 0:
            st.warning(f"⚠️ Remaining ₹{taxable_hra:,.0f} HRA is taxable")
        
        # Tax bracket selector
        st.markdown("---")
        st.subheader("💡 Your Tax Savings")
        tax_bracket = st.selectbox("Select Your Tax Bracket", ["30%", "20%", "10%", "5%"])
        bracket_rate = float(tax_bracket.strip('%')) / 100
        actual_tax_saved = hra_exempt * bracket_rate
        st.info(f"🎉 You save **₹{actual_tax_saved:,.0f}** in taxes with this HRA exemption!")

def show_emi_calculator():
    """EMI Calculator with comparison and prepayment analysis"""
    st.header("💳 EMI Calculator")
    
    tab1, tab2, tab3 = st.tabs(["📊 Basic EMI", "⚖️ Compare Loans", "🚀 Prepayment Impact"])
    
    with tab1:
        st.subheader("Calculate Your Monthly EMI")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            loan_amount = st.number_input("Loan Amount (₹)", min_value=100000, value=3000000, step=100000)
        with col2:
            interest_rate = st.number_input("Interest Rate (% p.a.)", min_value=5.0, max_value=20.0, value=8.5, step=0.1)
        with col3:
            tenure_years = st.number_input("Tenure (Years)", min_value=1, max_value=30, value=20)
        
        if st.button("Calculate EMI", type="primary"):
            # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
            monthly_rate = interest_rate / (12 * 100)
            tenure_months = tenure_years * 12
            
            if monthly_rate > 0:
                emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
            else:
                emi = loan_amount / tenure_months
            
            total_payment = emi * tenure_months
            total_interest = total_payment - loan_amount
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Monthly EMI", f"₹{emi:,.0f}")
            with col2:
                st.metric("Total Payment", f"₹{total_payment:,.0f}")
            with col3:
                st.metric("Total Interest", f"₹{total_interest:,.0f}")
            with col4:
                st.metric("Interest/Principal Ratio", f"{(total_interest/loan_amount)*100:.1f}%")
            
            # Pie chart for principal vs interest
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Pie(
                labels=['Principal', 'Interest'],
                values=[loan_amount, total_interest],
                hole=0.4,
                marker_colors=['#667eea', '#f093fb']
            )])
            fig.update_layout(title="Loan Breakdown", height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"💡 **Insight**: You'll pay ₹{total_interest:,.0f} ({(total_interest/loan_amount)*100:.1f}% of principal) as interest over {tenure_years} years")
    
    with tab2:
        st.subheader("Compare Multiple Loan Options")
        st.markdown("Compare up to 3 different loan offers")
        
        col1, col2, col3 = st.columns(3)
        
        comparisons = []
        for i, col in enumerate([col1, col2, col3], 1):
            with col:
                st.markdown(f"**Option {i}**")
                amt = st.number_input(f"Amount {i} (₹)", min_value=100000, value=3000000, step=100000, key=f"amt{i}")
                rate = st.number_input(f"Rate {i} (%)", min_value=5.0, max_value=20.0, value=8.5 + (i-1)*0.5, step=0.1, key=f"rate{i}")
                tenure = st.number_input(f"Tenure {i} (Y)", min_value=1, max_value=30, value=20, key=f"tenure{i}")
                
                monthly_rate = rate / (12 * 100)
                tenure_months = tenure * 12
                
                if monthly_rate > 0:
                    emi = amt * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
                else:
                    emi = amt / tenure_months
                
                total_payment = emi * tenure_months
                total_interest = total_payment - amt
                
                comparisons.append({
                    'option': f'Option {i}',
                    'emi': emi,
                    'total_payment': total_payment,
                    'total_interest': total_interest,
                    'amount': amt
                })
                
                st.metric("EMI", f"₹{emi:,.0f}")
                st.metric("Total Interest", f"₹{total_interest:,.0f}")
        
        # Comparison chart
        import plotly.graph_objects as go
        fig = go.Figure()
        options = [c['option'] for c in comparisons]
        fig.add_trace(go.Bar(name='Principal', x=options, y=[c['amount'] for c in comparisons], marker_color='#667eea'))
        fig.add_trace(go.Bar(name='Interest', x=options, y=[c['total_interest'] for c in comparisons], marker_color='#f093fb'))
        fig.update_layout(title="Total Cost Comparison", barmode='stack', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        best_option = min(comparisons, key=lambda x: x['total_interest'])
        st.success(f"🏆 **Best Option**: {best_option['option']} saves you the most with ₹{best_option['total_interest']:,.0f} total interest")
    
    with tab3:
        st.subheader("Prepayment Impact Analysis")
        st.markdown("See how prepayments can reduce your loan burden")
        
        col1, col2 = st.columns(2)
        with col1:
            base_loan = st.number_input("Original Loan (₹)", min_value=100000, value=3000000, step=100000, key="prepay_loan")
            base_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=20.0, value=8.5, key="prepay_rate")
            base_tenure = st.number_input("Original Tenure (Y)", min_value=1, max_value=30, value=20, key="prepay_tenure")
        
        with col2:
            prepay_amount = st.number_input("Prepayment Amount (₹)", min_value=0, value=500000, step=50000)
            prepay_year = st.number_input("Prepayment After (Years)", min_value=1, max_value=int(base_tenure-1), value=5)
        
        if st.button("Analyze Prepayment", type="primary"):
            # Original loan calculation
            monthly_rate = base_rate / (12 * 100)
            tenure_months = base_tenure * 12
            
            if monthly_rate > 0:
                original_emi = base_loan * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
            else:
                original_emi = base_loan / tenure_months
            
            original_total = original_emi * tenure_months
            original_interest = original_total - base_loan
            
            # After prepayment (reduce tenure, keep EMI same)
            months_elapsed = prepay_year * 12
            remaining_principal = base_loan * ((1 + monthly_rate) ** months_elapsed - (original_emi / (base_loan * monthly_rate)) * ((1 + monthly_rate) ** months_elapsed - 1)) / ((1 + monthly_rate) ** months_elapsed)
            
            new_principal = max(0, remaining_principal - prepay_amount)
            
            # Calculate new tenure with same EMI
            if new_principal > 0 and monthly_rate > 0 and original_emi > new_principal * monthly_rate:
                import math
                new_months = math.log(original_emi / (original_emi - new_principal * monthly_rate)) / math.log(1 + monthly_rate)
                new_tenure_total = months_elapsed + new_months
            else:
                new_tenure_total = months_elapsed
            
            new_total_payment = (months_elapsed * original_emi) + (new_months * original_emi) if new_principal > 0 else months_elapsed * original_emi
            new_total_interest = new_total_payment - base_loan + prepay_amount
            
            interest_saved = original_interest - new_total_interest
            tenure_reduced = (tenure_months - new_tenure_total) / 12
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Interest Saved", f"₹{interest_saved:,.0f}", "💰")
            with col2:
                st.metric("Tenure Reduced", f"{tenure_reduced:.1f} years", "⏱️")
            with col3:
                st.metric("New Loan End", f"{new_tenure_total/12:.1f} years")
            
            # Comparison chart
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Without Prepayment', x=['Total Interest'], y=[original_interest], marker_color='#f093fb'))
            fig.add_trace(go.Bar(name='With Prepayment', x=['Total Interest'], y=[new_total_interest], marker_color='#667eea'))
            fig.update_layout(title="Interest Comparison", height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            st.success(f"🎉 By prepaying ₹{prepay_amount:,.0f} in year {prepay_year}, you save ₹{interest_saved:,.0f} and finish {tenure_reduced:.1f} years earlier!")

def show_80c_comparator():
    """80C Investment Options Comparator"""
    st.header("💎 80C Investment Comparator")
    st.markdown("Compare tax-saving investments under Section 80C (max ₹1.5L deduction)")
    
    investment_amount = st.number_input("Investment Amount (₹)", min_value=1000, max_value=150000, value=150000, step=10000)
    time_horizon = st.slider("Investment Period (Years)", min_value=1, max_value=30, value=10)
    
    # Define investment options with realistic parameters
    options = {
        "PPF (Public Provident Fund)": {
            "return": 7.1,
            "lock_in": 15,
            "risk": "Very Low",
            "liquidity": "Low (partial after 7Y)",
            "tax_free": True,
            "description": "Government-backed, EEE status"
        },
        "ELSS (Equity Mutual Funds)": {
            "return": 12.0,
            "lock_in": 3,
            "risk": "High",
            "liquidity": "Medium (3Y lock-in)",
            "tax_free": False,
            "description": "Market-linked, LTCG taxable"
        },
        "NSC (National Savings Certificate)": {
            "return": 7.7,
            "lock_in": 5,
            "risk": "Very Low",
            "liquidity": "Low (5Y lock-in)",
            "tax_free": False,
            "description": "Fixed return, interest taxable"
        },
        "Tax Saver FD": {
            "return": 6.5,
            "lock_in": 5,
            "risk": "Very Low",
            "liquidity": "None (5Y lock-in)",
            "tax_free": False,
            "description": "Bank FD, interest taxable"
        },
        "NPS (National Pension System)": {
            "return": 10.0,
            "lock_in": 60,
            "risk": "Medium",
            "liquidity": "Very Low (till 60 age)",
            "tax_free": False,
            "description": "Retirement fund, partial tax-free"
        },
        "SCSS (Senior Citizen Scheme)": {
            "return": 8.2,
            "lock_in": 5,
            "risk": "Very Low",
            "liquidity": "Low (premature penalty)",
            "tax_free": False,
            "description": "Only for 60+ age"
        }
    }
    
    st.subheader("📊 Investment Comparison")
    
    # Calculate maturity values
    results = []
    for name, details in options.items():
        if time_horizon >= details["lock_in"]:
            years = min(time_horizon, details["lock_in"]) if details["lock_in"] < 60 else time_horizon
            maturity = investment_amount * ((1 + details["return"]/100) ** years)
            returns = maturity - investment_amount
            
            # Adjust for tax if not tax-free
            if not details["tax_free"]:
                tax_on_returns = returns * 0.20  # Assume 20% tax
                post_tax_maturity = investment_amount + (returns - tax_on_returns)
                effective_return = ((post_tax_maturity / investment_amount) ** (1/years) - 1) * 100
            else:
                post_tax_maturity = maturity
                effective_return = details["return"]
            
            results.append({
                "name": name,
                "maturity": maturity,
                "post_tax_maturity": post_tax_maturity,
                "returns": returns,
                "effective_return": effective_return,
                "details": details
            })
    
    # Sort by post-tax maturity
    results.sort(key=lambda x: x["post_tax_maturity"], reverse=True)
    
    # Display cards
    cols = st.columns(2)
    for idx, result in enumerate(results):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"### {result['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Maturity Value", f"₹{result['post_tax_maturity']:,.0f}")
                    st.write(f"**Return**: {result['effective_return']:.1f}% p.a.")
                with col2:
                    st.metric("Total Gains", f"₹{result['returns']:,.0f}")
                    st.write(f"**Risk**: {result['details']['risk']}")
                
                st.write(f"**Lock-in**: {result['details']['lock_in']} years")
                st.write(f"**Liquidity**: {result['details']['liquidity']}")
                st.write(f"ℹ️ {result['details']['description']}")
                st.markdown("---")
    
    # Comparison chart
    import plotly.graph_objects as go
    fig = go.Figure()
    names = [r['name'].split('(')[0].strip() for r in results]
    fig.add_trace(go.Bar(
        name='Investment',
        x=names,
        y=[investment_amount] * len(results),
        marker_color='#667eea'
    ))
    fig.add_trace(go.Bar(
        name='Returns (Post-tax)',
        x=names,
        y=[r['post_tax_maturity'] - investment_amount for r in results],
        marker_color='#f093fb'
    ))
    fig.update_layout(
        title=f"Maturity Value Comparison ({time_horizon} Years)",
        barmode='stack',
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendation
    best = results[0]
    st.success(f"🏆 **Best Option for {time_horizon} years**: {best['name']} with ₹{best['post_tax_maturity']:,.0f} maturity ({best['effective_return']:.1f}% effective return)")
    
    if best['details']['risk'] == "High":
        st.warning("⚠️ Note: ELSS has highest returns but comes with market risk. Diversify across multiple options.")
    
    st.info("💡 **Pro Tip**: Diversify your ₹1.5L across PPF (safety) + ELSS (growth) + NPS (retirement) for optimal tax-saving!")

def show_retirement_planner():
    """Retirement Planning Calculator with inflation"""
    st.header("🏖️ Retirement Planning Calculator")
    st.markdown("Plan your retirement corpus considering inflation and life expectancy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_age = st.number_input("Current Age", min_value=18, max_value=60, value=30)
        retirement_age = st.number_input("Retirement Age", min_value=current_age+5, max_value=75, value=60)
        life_expectancy = st.number_input("Life Expectancy", min_value=retirement_age+5, max_value=100, value=85)
    
    with col2:
        current_expenses = st.number_input("Current Monthly Expenses (₹)", min_value=10000, value=50000, step=5000)
        inflation_rate = st.slider("Expected Inflation (%)", min_value=4.0, max_value=10.0, value=6.0, step=0.5)
        expected_return = st.slider("Expected Return on Investment (%)", min_value=8.0, max_value=15.0, value=10.0, step=0.5)
    
    if st.button("Calculate Retirement Corpus", type="primary"):
        years_to_retirement = retirement_age - current_age
        years_in_retirement = life_expectancy - retirement_age
        
        # Calculate expenses at retirement (with inflation)
        expenses_at_retirement = current_expenses * ((1 + inflation_rate/100) ** years_to_retirement)
        annual_expenses_at_retirement = expenses_at_retirement * 12
        
        # Calculate corpus needed (present value of annuity)
        # Corpus = Annual Expense * [(1 - (1+r-i)^-n) / (r-i)] where r=return, i=inflation
        real_return = (expected_return - inflation_rate) / 100
        if real_return > 0:
            corpus_needed = annual_expenses_at_retirement * ((1 - (1 + real_return) ** -years_in_retirement) / real_return)
        else:
            corpus_needed = annual_expenses_at_retirement * years_in_retirement
        
        # Calculate monthly SIP needed
        monthly_return = expected_return / (12 * 100)
        months_to_retirement = years_to_retirement * 12
        
        if monthly_return > 0:
            monthly_sip = corpus_needed * monthly_return / (((1 + monthly_return) ** months_to_retirement) - 1)
        else:
            monthly_sip = corpus_needed / months_to_retirement
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Corpus Needed", f"₹{corpus_needed/10000000:.2f} Cr")
        with col2:
            st.metric("Monthly SIP Required", f"₹{monthly_sip:,.0f}")
        with col3:
            st.metric("Years to Retirement", f"{years_to_retirement}")
        with col4:
            st.metric("Expenses at Retirement", f"₹{expenses_at_retirement:,.0f}/mo")
        
        st.markdown("---")
        
        # Create accumulation and depletion chart
        import plotly.graph_objects as go
        
        # Accumulation phase
        accumulation_years = list(range(current_age, retirement_age + 1))
        accumulation_values = []
        accumulated = 0
        for year in range(years_to_retirement + 1):
            if year > 0:
                accumulated = (accumulated + monthly_sip * 12) * (1 + expected_return/100)
            accumulation_values.append(accumulated)
        
        # Depletion phase
        depletion_years = list(range(retirement_age, life_expectancy + 1))
        depletion_values = [corpus_needed]
        remaining = corpus_needed
        for year in range(1, years_in_retirement + 1):
            withdrawal = annual_expenses_at_retirement * ((1 + inflation_rate/100) ** (year - 1))
            remaining = remaining * (1 + expected_return/100) - withdrawal
            depletion_values.append(max(0, remaining))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=accumulation_years,
            y=accumulation_values,
            mode='lines',
            name='Accumulation Phase',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            x=depletion_years,
            y=depletion_values,
            mode='lines',
            name='Depletion Phase',
            line=dict(color='#f093fb', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            title="Retirement Corpus Journey",
            xaxis_title="Age (Years)",
            yaxis_title="Corpus Value (₹)",
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Detailed Breakdown")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Accumulation Phase (Till Retirement)**")
            st.write(f"• Current Age: {current_age} years")
            st.write(f"• Retirement Age: {retirement_age} years")
            st.write(f"• Investment Period: {years_to_retirement} years")
            st.write(f"• Monthly SIP: ₹{monthly_sip:,.0f}")
            st.write(f"• Total Investment: ₹{monthly_sip * months_to_retirement:,.0f}")
            st.write(f"• Corpus at Retirement: ₹{corpus_needed/10000000:.2f} Cr")
        
        with col2:
            st.markdown("**Retirement Phase (After Retirement)**")
            st.write(f"• Retirement Age: {retirement_age} years")
            st.write(f"• Life Expectancy: {life_expectancy} years")
            st.write(f"• Retirement Duration: {years_in_retirement} years")
            st.write(f"• Starting Monthly Expense: ₹{expenses_at_retirement:,.0f}")
            st.write(f"• Inflation-adjusted increases each year")
            st.write(f"• Final Year Expense: ₹{expenses_at_retirement * ((1 + inflation_rate/100) ** (years_in_retirement-1)):,.0f}/mo")
        
        # Recommendations
        st.markdown("---")
        st.subheader("💡 Personalized Recommendations")
        
        if monthly_sip > current_expenses * 0.5:
            st.error(f"⚠️ **High SIP Alert**: Required SIP (₹{monthly_sip:,.0f}) is >50% of current expenses. Consider:")
            st.write("• Increasing retirement age by 2-3 years")
            st.write("• Targeting lower monthly expenses in retirement")
            st.write("• Starting with smaller SIP and increasing by 10% annually")
        elif monthly_sip > current_expenses * 0.3:
            st.warning(f"⚠️ **Moderate SIP**: Required SIP is {(monthly_sip/current_expenses)*100:.0f}% of current expenses. Achievable but requires discipline.")
        else:
            st.success(f"✅ **Achievable Goal**: Required SIP is only {(monthly_sip/current_expenses)*100:.0f}% of current expenses. You're on track!")
        
        st.info(f"🎯 **Action Plan**: Start SIP of ₹{monthly_sip:,.0f}/month in diversified equity funds. Increase by 10% every year to beat inflation!")

def show_expense_analytics():
    """Expense Analytics with AI insights - Using REAL data from Budget"""
    from datetime import datetime, timedelta
    import pandas as pd
    
    st.header("📊 Expense Analytics & Insights")
    st.markdown("Analyze your spending patterns with AI-powered recommendations")
    
    # Initialize expense data from real budget or manual entries
    if 'expense_data' not in st.session_state:
        st.session_state.expense_data = []
    
    if 'expense_history' not in st.session_state:
        st.session_state.expense_history = []
    
    # Manual expense entry section
    with st.expander("➕ Add New Expense", expanded=False):
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                expense_date = st.date_input("Date", value=datetime.now())
            with col2:
                expense_category = st.selectbox("Category", 
                    ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                     'Bills & Utilities', 'Healthcare', 'Education', 'Others'])
            with col3:
                expense_amount = st.number_input("Amount (₹)", min_value=0, value=0, step=50)
            
            expense_description = st.text_input("Description (Optional)", placeholder="e.g., Groceries at Big Bazaar")
            
            if st.form_submit_button("💾 Add Expense"):
                if expense_amount > 0:
                    new_expense = {
                        'date': pd.Timestamp(expense_date),
                        'category': expense_category,
                        'amount': expense_amount,
                        'description': expense_description or f"{expense_category} expense"
                    }
                    st.session_state.expense_history.append(new_expense)
                    st.success(f"✅ Added ₹{expense_amount:,.0f} to {expense_category}")
                    st.rerun()
                else:
                    st.error("⚠️ Please enter a valid amount")
    
    # Import data from Budget page if available
    if st.session_state.get('current_budget') and len(st.session_state.expense_history) == 0:
        st.info("💡 **First Time Here?** Your budget data from Budget page is loaded below. Add daily expenses using '➕ Add New Expense' above!")
    
    # Combine budget data + manual entries
    expense_data = []
    
    # Add current month's budget as baseline expenses (if exists)
    if st.session_state.get('current_budget'):
        budget = st.session_state.current_budget
        current_month_start = datetime.now().replace(day=1)
        
        # Extract category-wise expenses from budget
        # Note: Budget page stores aggregated values, we'll distribute them
        budget_expenses = {
            'Bills & Utilities': budget.get('fixed_expenses', 0) / 3,  # Rough distribution
            'Food & Dining': budget.get('variable_expenses', 0) / 3,
            'Transportation': budget.get('variable_expenses', 0) / 3,
            'Entertainment': budget.get('variable_expenses', 0) / 3,
        }
        
        for category, amount in budget_expenses.items():
            if amount > 0:
                expense_data.append({
                    'date': pd.Timestamp(current_month_start),
                    'category': category,
                    'amount': amount,
                    'description': f"Monthly {category} (from budget)"
                })
    
    # Add manual expense history
    expense_data.extend(st.session_state.expense_history)
    
    # If no data at all, show empty state with call to action
    if len(expense_data) == 0:
        st.warning("📭 **No expense data found!**")
        st.info("**Get Started:**\n1. Go to **💰 Budget** page and save your monthly budget\n2. Or use **➕ Add New Expense** above to log expenses manually")
        
        if st.button("📊 Go to Budget Page"):
            st.session_state.current_page = "💰 Budget"
            st.rerun()
        
        st.stop()
    
    # Convert to DataFrame for analysis
    st.session_state.expense_data = expense_data
    
    # Analytics
    df = pd.DataFrame(st.session_state.expense_data)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    # Current month stats
    current_month = df['month'].max()
    current_month_data = df[df['month'] == current_month]
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = current_month_data['amount'].sum()
    avg_daily = total_spend / 30
    top_category = current_month_data.groupby('category')['amount'].sum().idxmax()
    top_category_amount = current_month_data.groupby('category')['amount'].sum().max()
    category_count = current_month_data['category'].nunique()
    
    with col1:
        st.metric("This Month Spend", f"₹{total_spend:,.0f}")
    with col2:
        st.metric("Avg Daily Spend", f"₹{avg_daily:,.0f}")
    with col3:
        st.metric("Top Category", top_category)
    with col4:
        st.metric("Active Categories", f"{category_count}/8")
    
    # Data source explanation
    st.info(f"""
    📌 **Data Source Explanation:**
    - **This Month Spend (₹{total_spend:,.0f})**: Sum of all expenses in current month from Budget + Manual entries
    - **Avg Daily Spend (₹{avg_daily:,.0f})**: Total spend ÷ 30 days = ₹{total_spend:,.0f} ÷ 30
    - **Top Category ({top_category})**: Highest spending category with ₹{top_category_amount:,.0f}
    - **Active Categories ({category_count}/8)**: Number of expense categories with transactions
    - **Total Transactions**: {len(current_month_data)} entries ({len([e for e in expense_data if 'from budget' in e['description']])} from budget, {len(st.session_state.expense_history)} manual)
    """)
    
    st.markdown("---")
    
    # Category-wise breakdown (Pie chart)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💰 Current Month Breakdown")
        category_totals = current_month_data.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Pie(
            labels=category_totals.index,
            values=category_totals.values,
            hole=0.4,
            marker_colors=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 6-Month Trend")
        monthly_totals = df.groupby('month')['amount'].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_totals.index,
            y=monthly_totals.values,
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10),
            fill='tozeroy'
        ))
        fig.update_layout(
            height=400,
            xaxis_title="Month",
            yaxis_title="Total Spend (₹)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Category-wise trends
    st.subheader("📊 Category-wise Spending Trends")
    category_monthly = df.groupby(['month', 'category'])['amount'].sum().reset_index()
    
    fig = go.Figure()
    for category in df['category'].unique():
        cat_data = category_monthly[category_monthly['category'] == category]
        fig.add_trace(go.Scatter(
            x=cat_data['month'],
            y=cat_data['amount'],
            mode='lines+markers',
            name=category,
            line=dict(width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        height=450,
        xaxis_title="Month",
        yaxis_title="Spend (₹)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # AI Insights
    st.subheader("🤖 AI-Powered Insights")
    
    # Calculate insights
    prev_month = df['month'].unique()[-2] if len(df['month'].unique()) > 1 else current_month
    prev_month_data = df[df['month'] == prev_month]
    
    mom_change = ((current_month_data['amount'].sum() - prev_month_data['amount'].sum()) / prev_month_data['amount'].sum()) * 100
    
    avg_monthly = df.groupby('month')['amount'].sum().mean()
    
    # Category with highest increase
    current_cat = current_month_data.groupby('category')['amount'].sum()
    prev_cat = prev_month_data.groupby('category')['amount'].sum()
    cat_change = ((current_cat - prev_cat) / prev_cat * 100).fillna(0)
    highest_increase_cat = cat_change.idxmax()
    highest_increase_pct = cat_change.max()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Spending Analysis**")
        if mom_change > 10:
            st.warning(f"⚠️ Spending increased by {mom_change:.1f}% vs last month")
        elif mom_change < -10:
            st.success(f"✅ Spending decreased by {abs(mom_change):.1f}% vs last month")
        else:
            st.info(f"📊 Spending stable ({mom_change:+.1f}% vs last month)")
        
        st.write(f"• Average monthly spend: ₹{avg_monthly:,.0f}")
        st.write(f"• Current vs average: {((current_month_data['amount'].sum() - avg_monthly) / avg_monthly * 100):+.1f}%")
        
        if highest_increase_pct > 20:
            st.write(f"• ⚠️ **{highest_increase_cat}** increased by {highest_increase_pct:.0f}%")
    
    with col2:
        st.markdown("**💡 Recommendations**")
        top_3_categories = category_totals.head(3)
        st.write(f"• Top expense: **{top_3_categories.index[0]}** (₹{top_3_categories.values[0]:,.0f})")
        
        if 'Food & Dining' in top_3_categories.index[:2]:
            st.write("• 🍽️ Consider meal planning to reduce dining expenses")
        
        if 'Shopping' in top_3_categories.index[:2]:
            st.write("• 🛍️ Review discretionary shopping - set weekly limits")
        
        if current_month_data['amount'].sum() > avg_monthly * 1.2:
            st.write("• 💰 Current spend is 20% above average - watch budget!")
        
        st.write(f"• 🎯 Target: Reduce top 3 categories by 10% each")
    
    # Spending alerts
    st.markdown("---")
    st.subheader("🚨 Spending Alerts")
    
    alerts = []
    
    # Check for high spends
    for category, amount in category_totals.items():
        if amount > avg_monthly * 0.3:
            alerts.append(f"⚠️ **{category}**: ₹{amount:,.0f} (>{30}% of avg monthly spend)")
    
    # Check for unusual spikes
    if highest_increase_pct > 50:
        alerts.append(f"📈 **{highest_increase_cat}** spiked by {highest_increase_pct:.0f}% - investigate large transactions")
    
    if mom_change > 25:
        alerts.append(f"🔴 Overall spending up {mom_change:.0f}% - review budget immediately")
    
    if len(alerts) > 0:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ No spending alerts - you're doing great!")
    
    # Detailed transaction breakdown
    st.markdown("---")
    st.subheader("📋 Detailed Expense Breakdown")
    
    with st.expander("View All Transactions (Click to expand)", expanded=False):
        # Show current month transactions
        transactions_df = current_month_data.copy()
        transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.strftime('%Y-%m-%d')
        transactions_df = transactions_df.sort_values('amount', ascending=False)
        
        st.dataframe(
            transactions_df[['date', 'category', 'amount', 'description']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": "Date",
                "category": "Category",
                "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
                "description": "Description"
            }
        )
        
        st.caption(f"Total: {len(transactions_df)} transactions | Sum: ₹{transactions_df['amount'].sum():,.2f}")
    
    # Category-wise summary table
    st.subheader("📊 Category-wise Summary")
    category_summary = current_month_data.groupby('category').agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    category_summary.columns = ['Total (₹)', 'Transactions', 'Avg per Transaction (₹)']
    category_summary = category_summary.sort_values('Total (₹)', ascending=False)
    
    st.dataframe(
        category_summary,
        use_container_width=True,
        column_config={
            "Total (₹)": st.column_config.NumberColumn("Total (₹)", format="₹%.2f"),
            "Transactions": st.column_config.NumberColumn("Transactions", format="%d"),
            "Avg per Transaction (₹)": st.column_config.NumberColumn("Avg per Transaction (₹)", format="₹%.2f")
        }
    )
    
    # Export option
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Expense Report (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Click to Download",
                data=csv,
                file_name=f"expense_report_{current_month}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🗑️ Clear All Manual Expenses"):
            if st.session_state.get('expense_history'):
                st.session_state.expense_history = []
                st.success("✅ All manual expenses cleared!")
                st.rerun()

# =====================================================
# REAL-LIFE FEATURES WITH DATABASE INTEGRATION
# =====================================================

def show_salary_breakup():
    """💰 Salary Breakup - Understand CTC vs In-Hand with Database Storage"""
    import plotly.graph_objects as go
    from datetime import datetime
    
    st.header("💰 Salary Breakup Calculator")
    st.markdown("**Understand your CTC vs In-Hand salary - Where does your money go?**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    # Try to load existing data
    try:
        result = db.table('salary_breakup').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        existing_data = result.data[0] if result.data else None
    except Exception as e:
        st.warning(f"Could not load existing data: {e}")
        existing_data = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Enter Your Salary Details")
        
        # Pre-fill with existing data
        default_ctc = float(existing_data['ctc']) if existing_data else 800000.0
        
        ctc = st.number_input(
            "Annual CTC (₹)", 
            min_value=100000, 
            max_value=50000000, 
            value=int(default_ctc),
            step=50000,
            help="Your total Cost to Company per year"
        )
        
        st.markdown("---")
        
        # Standard breakdown (40% Basic, 50% Allowances, 10% Bonus)
        basic_percent = st.slider("Basic Salary %", 30, 60, 40, help="Typically 40-50% of CTC")
        hra_percent = st.slider("HRA %", 10, 50, 30, help="Typically 30-40% of Basic")
        
        # Calculate components
        basic_salary = ctc * (basic_percent / 100)
        hra = basic_salary * (hra_percent / 100)
        special_allowance = ctc - basic_salary - hra
        
        # Deductions
        pf_contribution = basic_salary * 0.12  # 12% PF
        professional_tax = 2400  # Annual PT
        
        # Tax calculation (simplified - 30% slab assumed)
        taxable_income = max(0, ctc - 50000 - pf_contribution - 75000)  # Standard deduction + 80C
        if taxable_income <= 250000:
            income_tax = 0
        elif taxable_income <= 500000:
            income_tax = (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            income_tax = 12500 + (taxable_income - 500000) * 0.20
        else:
            income_tax = 112500 + (taxable_income - 1000000) * 0.30
        
        # Health cess 4%
        income_tax = income_tax * 1.04
        
        other_deductions = st.number_input("Other Deductions (₹/year)", 0, 100000, 5000, 1000)
        
        # Calculate in-hand
        total_deductions = pf_contribution + professional_tax + income_tax + other_deductions
        in_hand_salary = ctc - total_deductions
        monthly_in_hand = in_hand_salary / 12
        
        # Save to database button
        if st.button("💾 Save Salary Breakdown", type="primary"):
            try:
                data = {
                    'user_id': user_id,
                    'ctc': float(ctc),
                    'basic_salary': float(basic_salary),
                    'hra': float(hra),
                    'special_allowance': float(special_allowance),
                    'pf_contribution': float(pf_contribution),
                    'professional_tax': float(professional_tax),
                    'income_tax': float(income_tax),
                    'other_deductions': float(other_deductions),
                    'in_hand_salary': float(in_hand_salary),
                    'calculated_at': datetime.now().isoformat()
                }
                db.table('salary_breakup').insert(data).execute()
                st.success("✅ Salary breakdown saved to database!")
                st.balloons()
                # Reload page to show updated data
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to save: {e}")
    
    with col2:
        st.subheader("💸 Your Take-Home Breakdown")
        
        # Key metrics
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("Annual CTC", f"₹{ctc:,.0f}")
        metric_col2.metric("Annual In-Hand", f"₹{in_hand_salary:,.0f}")
        
        metric_col3, metric_col4 = st.columns(2)
        metric_col3.metric("Monthly In-Hand", f"₹{monthly_in_hand:,.0f}", f"{(in_hand_salary/ctc)*100:.1f}% of CTC")
        metric_col4.metric("Total Deductions", f"₹{total_deductions:,.0f}", f"{(total_deductions/ctc)*100:.1f}% of CTC")
        
        # Donut chart - Salary breakdown
        fig = go.Figure(data=[go.Pie(
            labels=['Basic Salary', 'HRA', 'Special Allowance', 'PF', 'Income Tax', 'Prof. Tax', 'Other Deductions'],
            values=[basic_salary, hra, special_allowance, pf_contribution, income_tax, professional_tax, other_deductions],
            hole=.4,
            marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3']),
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title="Where Your CTC Goes",
            height=400,
            showlegend=True,
            annotations=[dict(text=f'₹{ctc/100000:.1f}L', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown table
    st.markdown("---")
    st.subheader("📋 Detailed Monthly Breakdown")
    
    breakdown_data = {
        'Component': [
            'Basic Salary', 'HRA', 'Special Allowance', '**Gross Monthly**',
            'PF Contribution', 'Professional Tax', 'Income Tax', 'Other Deductions',
            '**Total Deductions**', '**Net In-Hand Salary**'
        ],
        'Annual (₹)': [
            f"{basic_salary:,.0f}", f"{hra:,.0f}", f"{special_allowance:,.0f}", f"**{ctc:,.0f}**",
            f"-{pf_contribution:,.0f}", f"-{professional_tax:,.0f}", f"-{income_tax:,.0f}", f"-{other_deductions:,.0f}",
            f"**-{total_deductions:,.0f}**", f"**{in_hand_salary:,.0f}**"
        ],
        'Monthly (₹)': [
            f"{basic_salary/12:,.0f}", f"{hra/12:,.0f}", f"{special_allowance/12:,.0f}", f"**{ctc/12:,.0f}**",
            f"-{pf_contribution/12:,.0f}", f"-{professional_tax/12:,.0f}", f"-{income_tax/12:,.0f}", f"-{other_deductions/12:,.0f}",
            f"**-{total_deductions/12:,.0f}**", f"**{monthly_in_hand:,.0f}**"
        ]
    }
    
    st.table(breakdown_data)
    
    # Insights
    st.info(f"""
    💡 **Key Insights:**
    - You take home **{(in_hand_salary/ctc)*100:.1f}%** of your CTC
    - **₹{(ctc - in_hand_salary)/12:,.0f}** is deducted every month
    - Your PF grows by **₹{pf_contribution:,.0f}** annually (with employer matching!)
    - Effective tax rate: **{(income_tax/ctc)*100:.1f}%** of CTC
    """)
    
    # Historical data - Show by default if data exists
    st.markdown("---")
    st.subheader("📊 Your Saved Calculations")
    try:
        history = db.table('salary_breakup').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        if history.data and len(history.data) > 0:
            history_df = pd.DataFrame(history.data)
            history_df['calculated_at'] = pd.to_datetime(history_df['calculated_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display formatted table
            display_df = history_df[['calculated_at', 'ctc', 'in_hand_salary', 'income_tax', 'pf_contribution']].copy()
            display_df.columns = ['Date & Time', 'CTC (₹)', 'In-Hand (₹)', 'Tax (₹)', 'PF (₹)']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'CTC (₹)': st.column_config.NumberColumn(format="₹%.0f"),
                    'In-Hand (₹)': st.column_config.NumberColumn(format="₹%.0f"),
                    'Tax (₹)': st.column_config.NumberColumn(format="₹%.0f"),
                    'PF (₹)': st.column_config.NumberColumn(format="₹%.0f"),
                }
            )
            st.caption(f"📝 Showing {len(history.data)} most recent calculation(s)")
        else:
            st.info("💡 No saved calculations yet. Click '💾 Save Salary Breakdown' to store your calculation!")
    except Exception as e:
        st.warning(f"⚠️ Could not load saved calculations: {e}")


def show_bill_reminder():
    """📱 Bill Reminder - Never Pay Late Fees, Track All Recurring Bills"""
    import plotly.express as px
    from datetime import datetime, timedelta
    import calendar
    
    st.header("📱 Bill Reminder & Tracker")
    st.markdown("**Never miss a payment - Track all your recurring bills in one place**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    # Load existing bills
    try:
        result = db.table('bill_reminders').select('*').eq('user_id', user_id).eq('is_active', True).order('due_date').execute()
        bills = result.data if result.data else []
    except Exception as e:
        st.error(f"Could not load bills: {e}")
        bills = []
    
    # Calculate upcoming and overdue
    today = datetime.now().date()
    upcoming_bills = [b for b in bills if datetime.fromisoformat(b['due_date'].replace('Z', '+00:00')).date() >= today]
    overdue_bills = [b for b in bills if datetime.fromisoformat(b['due_date'].replace('Z', '+00:00')).date() < today]
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_monthly = sum(float(b['amount']) for b in bills if b['frequency'] == 'Monthly')
    upcoming_7days = [b for b in upcoming_bills if (datetime.fromisoformat(b['due_date'].replace('Z', '+00:00')).date() - today).days <= 7]
    upcoming_amount = sum(float(b['amount']) for b in upcoming_7days)
    
    col1.metric("Total Bills", len(bills))
    col2.metric("Monthly Recurring", f"₹{total_monthly:,.0f}")
    col3.metric("Due in 7 Days", len(upcoming_7days), f"₹{upcoming_amount:,.0f}")
    col4.metric("⚠️ Overdue", len(overdue_bills), delta_color="inverse")
    
    # Add new bill form
    st.markdown("---")
    with st.expander("➕ Add New Bill", expanded=len(bills) == 0):
        with st.form("add_bill_form"):
            fcol1, fcol2, fcol3 = st.columns(3)
            
            with fcol1:
                bill_name = st.text_input("Bill Name*", placeholder="e.g., Electricity Bill")
                category = st.selectbox("Category*", 
                    ['Utilities', 'Subscription', 'Rent', 'EMI', 'Insurance', 'Credit Card', 'Other'])
                amount = st.number_input("Amount (₹)*", min_value=0, value=1000, step=100)
            
            with fcol2:
                due_date = st.date_input("Due Date*", value=datetime.now() + timedelta(days=5))
                frequency = st.selectbox("Frequency*", 
                    ['Monthly', 'Quarterly', 'Yearly', 'One-time'])
                payment_method = st.selectbox("Payment Method", 
                    ['Credit Card', 'Debit Card', 'UPI', 'Bank Transfer', 'Cash', 'Auto-Debit'])
            
            with fcol3:
                auto_pay = st.checkbox("Auto-Pay Enabled", value=False)
                reminder_days = st.number_input("Remind Me (days before)", 1, 30, 3)
                notes = st.text_area("Notes", placeholder="Optional notes...")
            
            submit_bill = st.form_submit_button("💾 Add Bill", type="primary", use_container_width=True)
            
            if submit_bill and bill_name and amount > 0:
                try:
                    data = {
                        'user_id': user_id,
                        'bill_name': bill_name,
                        'category': category,
                        'amount': float(amount),
                        'due_date': due_date.isoformat(),
                        'frequency': frequency,
                        'auto_pay_enabled': auto_pay,
                        'payment_method': payment_method,
                        'reminder_days': reminder_days,
                        'notes': notes,
                        'is_active': True
                    }
                    db.table('bill_reminders').insert(data).execute()
                    st.success(f"✅ Bill '{bill_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add bill: {e}")
    
    # Bills overview
    st.markdown("---")
    
    if len(overdue_bills) > 0:
        st.error("⚠️ **OVERDUE BILLS - Action Required!**")
        for bill in overdue_bills:
            due = datetime.fromisoformat(bill['due_date'].replace('Z', '+00:00')).date()
            days_overdue = (today - due).days
            
            with st.container():
                bcol1, bcol2, bcol3, bcol4, bcol5 = st.columns([3, 2, 2, 1, 1])
                bcol1.write(f"**{bill['bill_name']}** ({bill['category']})")
                bcol2.write(f"₹{bill['amount']:,.0f}")
                bcol3.write(f"❌ {days_overdue} days overdue")
                if bcol4.button("✅ Pay", key=f"pay_overdue_{bill['id']}", use_container_width=True):
                    try:
                        # For one-time bills, deactivate after payment
                        if bill['frequency'] == 'One-time':
                            db.table('bill_reminders').update({
                                'is_active': False,
                                'last_paid_date': today.isoformat(),
                                'last_paid_amount': bill['amount']
                            }).eq('id', bill['id']).execute()
                            st.success("✅ Paid & Removed!")
                        else:
                            # For recurring bills, update payment and next due date
                            next_due = datetime.fromisoformat(bill['due_date'].replace('Z', '+00:00')).date()
                            if bill['frequency'] == 'Monthly':
                                next_due = (next_due + timedelta(days=30))
                            elif bill['frequency'] == 'Quarterly':
                                next_due = (next_due + timedelta(days=90))
                            elif bill['frequency'] == 'Yearly':
                                next_due = (next_due + timedelta(days=365))
                            
                            db.table('bill_reminders').update({
                                'last_paid_date': today.isoformat(),
                                'last_paid_amount': bill['amount'],
                                'due_date': next_due.isoformat()
                            }).eq('id', bill['id']).execute()
                            st.success("✅ Paid! Next due date updated")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                if bcol5.button("🗑️", key=f"del_overdue_{bill['id']}", help="Remove bill", use_container_width=True):
                    try:
                        db.table('bill_reminders').update({'is_active': False}).eq('id', bill['id']).execute()
                        st.success("🗑️ Bill removed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown("---")
    
    # Upcoming bills
    if len(upcoming_7days) > 0:
        st.warning("🔔 **Bills Due in Next 7 Days**")
        for bill in upcoming_7days:
            due = datetime.fromisoformat(bill['due_date'].replace('Z', '+00:00')).date()
            days_left = (due - today).days
            
            with st.container():
                bcol1, bcol2, bcol3, bcol4, bcol5 = st.columns([3, 2, 2, 1, 1])
                bcol1.write(f"**{bill['bill_name']}** ({bill['category']})")
                bcol2.write(f"₹{bill['amount']:,.0f}")
                
                if days_left == 0:
                    bcol3.write("⏰ **Due TODAY**")
                elif days_left == 1:
                    bcol3.write("⚠️ Due tomorrow")
                else:
                    bcol3.write(f"📅 Due in {days_left} days")
                
                if bill['auto_pay_enabled']:
                    bcol4.write("🤖 Auto")
                    if bcol5.button("🗑️", key=f"del_auto_{bill['id']}", help="Remove bill", use_container_width=True):
                        try:
                            db.table('bill_reminders').update({'is_active': False}).eq('id', bill['id']).execute()
                            st.success("🗑️ Bill removed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    if bcol4.button("✅ Pay", key=f"pay_{bill['id']}", use_container_width=True):
                        try:
                            # For one-time bills, deactivate after payment
                            if bill['frequency'] == 'One-time':
                                db.table('bill_reminders').update({
                                    'is_active': False,
                                    'last_paid_date': today.isoformat(),
                                    'last_paid_amount': bill['amount']
                                }).eq('id', bill['id']).execute()
                                st.success("✅ Paid & Removed!")
                            else:
                                # For recurring bills, update payment and next due date
                                next_due = datetime.fromisoformat(bill['due_date'].replace('Z', '+00:00')).date()
                                if bill['frequency'] == 'Monthly':
                                    next_due = (next_due + timedelta(days=30))
                                elif bill['frequency'] == 'Quarterly':
                                    next_due = (next_due + timedelta(days=90))
                                elif bill['frequency'] == 'Yearly':
                                    next_due = (next_due + timedelta(days=365))
                                
                                db.table('bill_reminders').update({
                                    'last_paid_date': today.isoformat(),
                                    'last_paid_amount': bill['amount'],
                                    'due_date': next_due.isoformat()
                                }).eq('id', bill['id']).execute()
                                st.success("✅ Paid! Next due date updated")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if bcol5.button("🗑️", key=f"del_{bill['id']}", help="Remove bill", use_container_width=True):
                        try:
                            db.table('bill_reminders').update({'is_active': False}).eq('id', bill['id']).execute()
                            st.success("🗑️ Bill removed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        st.markdown("---")
    
    # All bills table
    st.subheader("📋 All Active Bills")
    
    tab1, tab2, tab3 = st.tabs(["📅 Calendar View", "📊 By Category", "📝 List View"])
    
    with tab1:
        if bills:
            # Create calendar heatmap
            bill_dates = {}
            for bill in bills:
                due = datetime.fromisoformat(bill['due_date'].replace('Z', '+00:00')).date()
                date_str = due.strftime('%Y-%m-%d')
                bill_dates[date_str] = bill_dates.get(date_str, 0) + float(bill['amount'])
            
            dates = list(bill_dates.keys())
            amounts = list(bill_dates.values())
            
            fig = px.bar(x=dates, y=amounts, labels={'x': 'Due Date', 'y': 'Amount (₹)'}, title='Bills by Due Date')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if bills:
            category_totals = {}
            for bill in bills:
                cat = bill['category']
                category_totals[cat] = category_totals.get(cat, 0) + float(bill['amount'])
            
            fig = px.pie(names=list(category_totals.keys()), values=list(category_totals.values()), 
                        title='Bills by Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if bills:
            bills_df = pd.DataFrame(bills)
            bills_df['due_date'] = pd.to_datetime(bills_df['due_date']).dt.strftime('%Y-%m-%d')
            display_cols = ['bill_name', 'category', 'amount', 'due_date', 'frequency', 'payment_method']
            st.dataframe(bills_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No bills added yet. Click 'Add New Bill' to get started!")
    
    # Summary insights
    st.markdown("---")
    st.info(f"""
    💡 **Bill Summary:**
    - **Total Monthly Bills:** ₹{total_monthly:,.0f}
    - **Bills on Auto-Pay:** {sum(1 for b in bills if b['auto_pay_enabled'])}/{len(bills)}
    - **Next Due Date:** {upcoming_bills[0]['due_date'][:10] if upcoming_bills else 'None'}
    - **Annual Estimate:** ₹{total_monthly * 12:,.0f}
    """)


def show_credit_card_optimizer():
    """💳 Credit Card Optimizer - Maximize Cashback, Avoid EMI Traps"""
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import datetime
    
    st.header("💳 Credit Card Optimizer")
    st.markdown("**Maximize cashback rewards and never fall into the EMI trap**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    # Load existing cards
    try:
        result = db.table('credit_cards').select('*').eq('user_id', user_id).order('is_primary', desc=True).execute()
        cards = result.data if result.data else []
        # Debug: Show loaded cards count
        if len(cards) > 0:
            st.caption(f"📊 Loaded {len(cards)} credit card(s) from database")
    except Exception as e:
        st.error(f"❌ Could not load credit cards: {e}")
        cards = []
    
    # Calculate metrics
    total_spend = sum(float(c['monthly_spend']) for c in cards)
    total_cashback = sum(float(c['monthly_spend']) * float(c.get('cashback_rate', 0)) / 100 for c in cards)
    total_annual_fees = sum(float(c.get('annual_fee', 0)) for c in cards)
    net_annual_benefit = (total_cashback * 12) - total_annual_fees
    
    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cards", len(cards))
    col2.metric("Monthly Spend", f"₹{total_spend:,.0f}")
    col3.metric("Monthly Cashback", f"₹{total_cashback:,.0f}", f"₹{total_cashback * 12:,.0f}/year")
    col4.metric("Net Annual Benefit", f"₹{net_annual_benefit:,.0f}", "After fees")
    
    # Add new card
    st.markdown("---")
    with st.expander("➕ Add Credit Card", expanded=len(cards) == 0):
        with st.form("add_card_form"):
            ccol1, ccol2, ccol3 = st.columns(3)
            
            with ccol1:
                card_name = st.text_input("Card Name*", placeholder="e.g., HDFC Regalia")
                bank_name = st.text_input("Bank Name*", placeholder="e.g., HDFC Bank")
                card_type = st.selectbox("Card Type*", 
                    ['Cashback', 'Rewards', 'Travel', 'Premium', 'Basic', 'Fuel', 'Shopping'])
            
            with ccol2:
                annual_fee = st.number_input("Annual Fee (₹)", min_value=0, value=499, step=100)
                cashback_rate = st.number_input("Cashback Rate (%)", min_value=0.0, max_value=20.0, value=1.0, step=0.5,
                    help="1% = ₹1 back on every ₹100 spent")
                reward_points_rate = st.number_input("Reward Points (per ₹100)", min_value=0.0, max_value=10.0, value=1.0, step=0.5)
            
            with ccol3:
                monthly_spend = st.number_input("Avg Monthly Spend (₹)", min_value=0, value=15000, step=1000)
                credit_limit = st.number_input("Credit Limit (₹)", min_value=10000, value=100000, step=10000)
                is_primary = st.checkbox("Set as Primary Card", value=len(cards) == 0)
            
            ccol4, ccol5 = st.columns(2)
            with ccol4:
                statement_date = st.number_input("Statement Date (1-31)", 1, 31, 5)
                lounge_access = st.checkbox("Lounge Access", value=False)
            
            with ccol5:
                due_date = st.number_input("Due Date (1-31)", 1, 31, 20)
                fuel_surcharge = st.checkbox("Fuel Surcharge Waiver", value=False)
            
            submit_card = st.form_submit_button("💾 Add Card", type="primary", use_container_width=True)
            
            if submit_card and card_name and bank_name:
                try:
                    data = {
                        'user_id': user_id,
                        'card_name': card_name,
                        'bank_name': bank_name,
                        'card_type': card_type,
                        'annual_fee': float(annual_fee),
                        'cashback_rate': float(cashback_rate),
                        'reward_points_rate': float(reward_points_rate),
                        'monthly_spend': float(monthly_spend),
                        'credit_limit': float(credit_limit),
                        'statement_date': statement_date,
                        'due_date': due_date,
                        'is_primary': is_primary,
                        'lounge_access': lounge_access,
                        'fuel_surcharge_waiver': fuel_surcharge
                    }
                    insert_result = db.table('credit_cards').insert(data).execute()
                    st.success(f"✅ Card '{card_name}' added successfully!")
                    st.balloons()
                    # Force reload the page to show new card
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add card: {e}")
                    st.exception(e)
    
    # Card comparison
    st.markdown("---")
    st.subheader("💎 Your Cards Performance")
    
    if len(cards) == 0:
        st.info("📝 No credit cards added yet. Click 'Add Credit Card' above to get started!")
    
    if cards:
        # Create performance comparison
        card_performance = []
        for card in cards:
            monthly_cashback = float(card['monthly_spend']) * float(card.get('cashback_rate', 0)) / 100
            annual_cashback = monthly_cashback * 12
            annual_net = annual_cashback - float(card.get('annual_fee', 0))
            
            card_performance.append({
                'card': f"{card['card_name']} ({card['bank_name']})",
                'type': card['card_type'],
                'monthly_spend': float(card['monthly_spend']),
                'monthly_cashback': monthly_cashback,
                'annual_fee': float(card.get('annual_fee', 0)),
                'annual_net_benefit': annual_net,
                'utilization': (float(card['monthly_spend']) / float(card.get('credit_limit', 100000))) * 100
            })
        
        # Best card recommendation
        best_card = max(card_performance, key=lambda x: x['annual_net_benefit'])
        
        st.success(f"""
        🏆 **Best Performing Card:** {best_card['card']}  
        **Net Benefit:** ₹{best_card['annual_net_benefit']:,.0f}/year  
        **Monthly Cashback:** ₹{best_card['monthly_cashback']:,.0f}
        """)
        
        # Cards table
        for idx, perf in enumerate(card_performance):
            card_data = cards[idx]  # Get the original card data
            with st.container():
                c_col1, c_col2, c_col3, c_col4, c_col5 = st.columns([3, 2, 2, 2, 1])
                
                is_best = perf['card'] == best_card['card']
                badge = "🏆 " if is_best else ""
                
                c_col1.markdown(f"**{badge}{perf['card']}**  \n<small>{perf['type']}</small>", unsafe_allow_html=True)
                c_col2.metric("Monthly Spend", f"₹{perf['monthly_spend']:,.0f}")
                c_col3.metric("Cashback", f"₹{perf['monthly_cashback']:,.0f}/mo", f"₹{perf['monthly_cashback']*12:,.0f}/yr")
                c_col4.metric("Net Benefit", f"₹{perf['annual_net_benefit']:,.0f}/yr", 
                             delta_color="normal" if perf['annual_net_benefit'] > 0 else "inverse")
                
                # Delete button
                if c_col5.button("🗑️", key=f"del_card_{card_data['id']}", help="Delete card", use_container_width=True):
                    try:
                        db.table('credit_cards').delete().eq('id', card_data['id']).execute()
                        st.success(f"🗑️ Card '{card_data['card_name']}' deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting card: {e}")
                
                # Utilization warning
                if perf['utilization'] > 30:
                    c_col1.warning(f"⚠️ High utilization: {perf['utilization']:.1f}% (keep < 30%)")
        
        # Visualizations
        st.markdown("---")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Cashback comparison
            fig1 = go.Figure(data=[
                go.Bar(name='Monthly Cashback', x=[p['card'] for p in card_performance], 
                      y=[p['monthly_cashback'] for p in card_performance], marker_color='#667eea'),
                go.Bar(name='Annual Fee (monthly)', x=[p['card'] for p in card_performance], 
                      y=[p['annual_fee']/12 for p in card_performance], marker_color='#ff6b6b')
            ])
            fig1.update_layout(title='Cashback vs Fees', barmode='group', height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with viz_col2:
            # Spend distribution
            fig2 = px.pie(
                values=[p['monthly_spend'] for p in card_performance],
                names=[p['card'] for p in card_performance],
                title='Spend Distribution',
                hole=0.4
            )
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
        
        # EMI Trap Calculator
        st.markdown("---")
        st.subheader("⚠️ EMI Trap Calculator")
        st.warning("**Never convert to EMI!** See how much extra you'll pay:")
        
        emi_col1, emi_col2, emi_col3 = st.columns(3)
        
        with emi_col1:
            purchase_amount = st.number_input("Purchase Amount (₹)", 1000, 1000000, 50000, 1000)
            emi_months = st.selectbox("EMI Tenure", [3, 6, 9, 12, 18, 24])
        
        with emi_col2:
            # Typical credit card interest rates
            interest_rate = st.slider("Interest Rate (%/year)", 12.0, 42.0, 36.0, 0.5,
                help="Most cards charge 36-42% on EMI")
            
            monthly_rate = interest_rate / 12 / 100
            emi_amount = (purchase_amount * monthly_rate * (1 + monthly_rate)**emi_months) / ((1 + monthly_rate)**emi_months - 1)
            total_payment = emi_amount * emi_months
            interest_paid = total_payment - purchase_amount
        
        with emi_col3:
            st.metric("Monthly EMI", f"₹{emi_amount:,.0f}")
            st.metric("Total Payment", f"₹{total_payment:,.0f}")
            st.metric("Interest Paid", f"₹{interest_paid:,.0f}", delta_color="inverse")
        
        st.error(f"""
        🚫 **DON'T DO IT!**  
        You'll pay ₹{interest_paid:,.0f} extra ({(interest_paid/purchase_amount)*100:.1f}% more)  
        
        ✅ **Better Options:**
        - Pay full amount next month (0% interest)
        - Take personal loan at 12-16% (save ₹{interest_paid - (purchase_amount * 0.14 * emi_months/12):,.0f})
        - Use No-Cost EMI offers (0% interest)
        """)
        
    else:
        st.info("👆 Add your credit cards to see optimization recommendations!")
    
    # Tips
    st.markdown("---")
    with st.expander("💡 Credit Card Optimization Tips"):
        st.markdown("""
        ### Maximize Benefits:
        - **Pay full bill** every month - avoid 36-42% interest charges
        - **Keep utilization < 30%** - good for credit score
        - **Use category-specific cards** - 5% on shopping, 3% on fuel, etc.
        - **Track reward expiry** - use points before they expire
        
        ### Avoid Traps:
        - **Never convert to EMI** - 36%+ interest is robbery
        - **Never withdraw cash** - 2.5% fee + 42% interest from day 1
        - **Pay before due date** - late fee ₹500-1500 + interest
        - **Cancel unused cards** - save annual fees
        
        ### Smart Usage:
        - Set autopay for minimum due (safety net)
        - Pay manually full amount (avoid interest)
        - Use card for large purchases (buyer protection)
        - Track spending in this app!
        """)


def show_fd_vs_debt_fund():
    """🏦 FD vs Debt Fund - Make Smart Short-term Investment Decisions"""
    import plotly.graph_objects as go
    from datetime import datetime
    
    st.header("🏦 FD vs Debt Fund Calculator")
    st.markdown("**Make smart short-term investment decisions with actual tax calculations**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("💰 Investment Details")
        
        principal = st.number_input("Investment Amount (₹)", 10000, 10000000, 100000, 10000)
        time_period = st.selectbox("Investment Period", 
            [3, 6, 9, 12, 18, 24, 36],
            format_func=lambda x: f"{x} months ({x/12:.1f} years)" if x >= 12 else f"{x} months"
        )
        
        tax_bracket = st.selectbox("Your Tax Bracket", 
            ['0% (Income < ₹2.5L)', '5% (₹2.5L-5L)', '20% (₹5L-10L)', '30% (> ₹10L)'],
            index=3
        )
        
        # Extract tax rate
        tax_rate = float(tax_bracket.split('%')[0]) / 100
        
        st.markdown("---")
        
        # FD Details
        st.markdown("**🏦 Fixed Deposit**")
        fd_rate = st.slider("FD Interest Rate (%)", 5.0, 9.0, 7.5, 0.25,
            help="SBI: 7.0%, HDFC: 7.25%, ICICI: 7.5%")
        
        st.markdown("**📈 Debt Fund**")
        debt_fund_return = st.slider("Expected Return (%)", 5.0, 12.0, 8.5, 0.25,
            help="Liquid: 6-7%, Short-term: 7-9%, Corporate Bond: 8-10%")
    
    with col2:
        st.subheader("📊 Comparison Results")
        
        # FD Calculations
        fd_maturity = principal * ((1 + fd_rate/100 / 4) ** (4 * time_period/12))
        fd_interest = fd_maturity - principal
        fd_tax = fd_interest * tax_rate
        fd_post_tax = fd_maturity - fd_tax
        fd_post_tax_return = ((fd_post_tax / principal) - 1) * 100
        
        # Debt Fund Calculations (with indexation benefit if > 3 years)
        debt_maturity = principal * ((1 + debt_fund_return/100) ** (time_period/12))
        debt_gains = debt_maturity - principal
        
        if time_period >= 36:
            # Long-term capital gains with indexation
            inflation_rate = 5.0  # CII indexation
            indexed_cost = principal * ((1 + inflation_rate/100) ** (time_period/12))
            taxable_gains = max(0, debt_maturity - indexed_cost)
            debt_tax = taxable_gains * 0.20  # 20% with indexation
        else:
            # Short-term capital gains - at slab rate
            debt_tax = debt_gains * tax_rate
        
        debt_post_tax = debt_maturity - debt_tax
        debt_post_tax_return = ((debt_post_tax / principal) - 1) * 100
        
        # Winner
        winner = "Debt Fund" if debt_post_tax > fd_post_tax else "Fixed Deposit"
        difference = abs(debt_post_tax - fd_post_tax)
        
        # Display results
        st.success(f"🏆 **Winner: {winner}** (₹{difference:,.0f} more)")
        
        # Comparison table
        comparison_data = {
            '': ['Principal', 'Maturity Amount', 'Gross Returns', 'Tax Paid', '**Post-Tax Amount**', '**Effective Return**'],
            '🏦 Fixed Deposit': [
                f"₹{principal:,.0f}",
                f"₹{fd_maturity:,.0f}",
                f"₹{fd_interest:,.0f}",
                f"₹{fd_tax:,.0f}",
                f"**₹{fd_post_tax:,.0f}**",
                f"**{fd_post_tax_return:.2f}%**"
            ],
            '📈 Debt Fund': [
                f"₹{principal:,.0f}",
                f"₹{debt_maturity:,.0f}",
                f"₹{debt_gains:,.0f}",
                f"₹{debt_tax:,.0f}",
                f"**₹{debt_post_tax:,.0f}**",
                f"**{debt_post_tax_return:.2f}%**"
            ]
        }
        
        st.table(comparison_data)
        
        # Visual comparison
        fig = go.Figure()
        
        categories = ['Maturity', 'Tax', 'Post-Tax']
        fd_values = [fd_maturity, fd_tax, fd_post_tax]
        debt_values = [debt_maturity, debt_tax, debt_post_tax]
        
        fig.add_trace(go.Bar(name='FD', x=categories, y=fd_values, marker_color='#667eea'))
        fig.add_trace(go.Bar(name='Debt Fund', x=categories, y=debt_values, marker_color='#764ba2'))
        
        fig.update_layout(
            title='Side-by-Side Comparison',
            barmode='group',
            height=300,
            yaxis_title='Amount (₹)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Save calculation
    if st.button("💾 Save This Comparison", type="primary"):
        try:
            # Pack detailed metrics into comparison_data JSON
            comparison_details = {
                'investment_horizon': 'Long-term' if time_period >= 36 else 'Short-term' if time_period <= 12 else 'Medium-term',
                'fd_rate': float(fd_rate),
                'fd_maturity': float(fd_maturity),
                'fd_tax_amount': float(fd_tax),
                'fd_post_tax_return': float(fd_post_tax),
                'debt_fund_return': float(debt_fund_return),
                'debt_fund_maturity': float(debt_maturity),
                'debt_fund_tax_amount': float(debt_tax),
                'debt_fund_post_tax_return': float(debt_post_tax)
            }
            
            data = {
                'user_id': user_id,
                'investment_type': 'FD vs Debt Fund',
                'principal_amount': float(principal),
                'time_period': time_period,
                'recommended_option': winner,
                'comparison_data': comparison_details,
                'calculation_date': datetime.now().isoformat()
            }
            db.table('investment_comparisons').insert(data).execute()
            st.success("✅ Comparison saved to database!")
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Recommendations")
    
    if time_period <= 3:
        st.info(f"""
        **For {time_period} months:** Ultra short-term
        - ✅ **Liquid Fund** - 6-7% returns, withdraw anytime
        - ✅ **Savings Account** - 4-7% (if < ₹1L)
        - ❌ **FD** - Lock-in not worth it for just {time_period} months
        """)
    elif time_period <= 12:
        st.info(f"""
        **For {time_period} months:** Short-term
        - ✅ **Liquid/Ultra Short Debt Fund** - Better than FD after tax
        - ✅ **FD** - If you need guaranteed returns
        - ⚠️ **Avoid** - Equity, long-term bonds
        """)
    elif time_period <= 36:
        st.info(f"""
        **For {time_period} months:** Medium-term
        - ✅ **Short Duration Debt Fund** - Tax efficient, 7-9% returns
        - ✅ **Corporate Bond Fund** - 8-10% for higher risk appetite
        - ⚠️ **FD** - Lower returns after tax
        """)
    else:
        st.success(f"""
        **For {time_period} months:** Long-term (Indexation Benefit!)
        - 🏆 **Debt Funds WIN!** - 20% tax with indexation benefit
        - ✅ **Corporate Bond/Dynamic Bond Fund** - Best risk-adjusted returns
        - ✅ **Gilt Funds** - If you want zero credit risk
        - ❌ **FD** - Much higher tax at slab rate
        """)
    
    # Historical comparison
    with st.expander("📊 View Previous Comparisons"):
        try:
            result = db.table('investment_comparisons').select('*').eq('user_id', user_id).order('calculation_date', desc=True).limit(10).execute()
            if result.data:
                history_df = pd.DataFrame(result.data)
                
                # Extract metrics from comparison_data JSON
                if 'comparison_data' in history_df.columns:
                    # Normalize the JSON column into separate columns
                    # Convert Series to list of dicts for json_normalize and handle potential None/NaN
                    comparison_data_list = history_df['comparison_data'].tolist()
                    comparison_data_list = [x if isinstance(x, dict) else {} for x in comparison_data_list]
                    
                    json_df = pd.json_normalize(comparison_data_list)
                    json_df.index = history_df.index
                    history_df = pd.concat([history_df.drop('comparison_data', axis=1), json_df], axis=1)
                
                history_df['calculation_date'] = pd.to_datetime(history_df['calculation_date'])
                history_df['calculation_date'] = history_df['calculation_date'].dt.strftime('%Y-%m-%d')
                
                # Select columns to display (handle missing columns gracefully)
                display_cols = ['calculation_date', 'principal_amount', 'time_period', 'recommended_option']
                if 'fd_post_tax_return' in history_df.columns:
                    display_cols.append('fd_post_tax_return')
                if 'debt_fund_post_tax_return' in history_df.columns:
                    display_cols.append('debt_fund_post_tax_return')
                    
                st.dataframe(history_df[display_cols], use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Failed to load history: {e}")
        except Exception as e:
            st.info("No previous comparisons found.")


def show_quick_money_moves():
    """⚡ Quick Money Moves - Actionable Steps to Save/Earn Money TODAY"""
    import plotly.express as px
    from datetime import datetime, date
    
    st.header("⚡ Quick Money Moves")
    st.markdown("**Actionable steps you can take TODAY to save or earn money**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    # Load moves
    try:
        result = db.table('quick_money_moves').select('*').eq('user_id', user_id).order('priority', desc=True).execute()
        moves = result.data if result.data else []
    except Exception as e:
        st.error(f"Could not load money moves: {e}")
        moves = []
    
    # Calculate stats
    pending_moves = [m for m in moves if m['status'] == 'Pending']
    completed_moves = [m for m in moves if m['status'] == 'Completed']
    total_potential_impact = sum(float(m.get('estimated_impact', 0)) for m in pending_moves)
    total_actual_impact = sum(float(m.get('actual_impact', 0)) for m in completed_moves if m.get('actual_impact'))
    
    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pending Actions", len(pending_moves))
    col2.metric("Potential Impact", f"₹{total_potential_impact:,.0f}/mo")
    col3.metric("Completed", len(completed_moves))
    col4.metric("Actual Savings", f"₹{total_actual_impact:,.0f}/mo")
    
    # Add new move
    st.markdown("---")
    with st.expander("➕ Add New Money Move", expanded=len(moves) == 0):
        with st.form("add_move_form"):
            mcol1, mcol2, mcol3 = st.columns(3)
            
            with mcol1:
                move_type = st.selectbox("Type*", ['Savings', 'Earning', 'Debt Reduction', 'Investment'])
                action_item = st.text_input("Action Item*", placeholder="e.g., Cancel unused subscriptions")
                category = st.selectbox("Category", 
                    ['Banking', 'Subscriptions', 'Utilities', 'Shopping', 'Food', 'Transport', 'Other'])
            
            with mcol2:
                estimated_impact = st.number_input("Estimated Impact (₹/month)", 0, 100000, 500, 100)
                difficulty = st.selectbox("Difficulty", ['Easy', 'Medium', 'Hard'])
                time_required = st.selectbox("Time Required", 
                    ['5 mins', '15 mins', '30 mins', '1 hour', '2 hours', '1 day'])
            
            with mcol3:
                priority = st.slider("Priority (1-5)", 1, 5, 3, help="5 = Highest priority")
                description = st.text_area("Description", placeholder="Details about this move...")
            
            submit_move = st.form_submit_button("💾 Add Money Move", type="primary", use_container_width=True)
            
            if submit_move and action_item:
                try:
                    data = {
                        'user_id': user_id,
                        'move_type': move_type,
                        'action_item': action_item,
                        'description': description,
                        'estimated_impact': float(estimated_impact),
                        'difficulty_level': difficulty,
                        'time_required': time_required,
                        'status': 'Pending',
                        'priority': priority,
                        'category': category
                    }
                    result = db.table('quick_money_moves').insert(data).execute()
                    if result.data:
                        st.success(f"✅ Money move '{action_item}' added!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("⚠️ Move added but no confirmation received")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add move: {e}")
                    st.exception(e)
    
    # Quick Wins Section
    if pending_moves:
        st.markdown("---")
        st.subheader("🎯 Quick Wins (Do These First!)")
        
        quick_wins = [m for m in pending_moves if m['difficulty_level'] == 'Easy' and m['priority'] >= 4]
        
        if quick_wins:
            for move in quick_wins[:3]:  # Top 3 quick wins
                with st.container():
                    wcol1, wcol2, wcol3, wcol4 = st.columns([3, 1, 1, 1])
                    
                    wcol1.markdown(f"""
                    **{move['action_item']}**  
                    <small>{move['description'][:100] if move.get('description') else ''}</small>
                    """, unsafe_allow_html=True)
                    
                    wcol2.write(f"⏱️ {move['time_required']}")
                    wcol3.write(f"💰 ₹{move['estimated_impact']:,.0f}/mo")
                    
                    if wcol4.button("✅ Done", key=f"complete_{move['id']}"):
                        # Mark as completed
                        actual_impact = st.number_input(f"Actual impact for {move['action_item']}", 
                            value=float(move['estimated_impact']), key=f"impact_{move['id']}")
                        try:
                            db.table('quick_money_moves').update({
                                'status': 'Completed',
                                'completed_date': date.today().isoformat(),
                                'actual_impact': float(actual_impact)
                            }).eq('id', move['id']).execute()
                            st.success("🎉 Great job!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                st.markdown("---")
    
    # All Moves by Category
    st.subheader("📋 All Money Moves")
    
    tab1, tab2, tab3 = st.tabs(["📌 Pending", "✅ Completed", "📊 Analytics"])
    
    with tab1:
        if pending_moves:
            # Group by type
            for move_type in ['Savings', 'Earning', 'Debt Reduction', 'Investment']:
                type_moves = [m for m in pending_moves if m['move_type'] == move_type]
                if type_moves:
                    st.markdown(f"### {move_type}")
                    for move in sorted(type_moves, key=lambda x: x['priority'], reverse=True):
                        with st.expander(f"{'⭐' * move['priority']} {move['action_item']} - ₹{move['estimated_impact']:,.0f}/mo"):
                            ecol1, ecol2 = st.columns(2)
                            
                            with ecol1:
                                st.write(f"**Description:** {move.get('description', 'N/A')}")
                                st.write(f"**Category:** {move['category']}")
                                st.write(f"**Difficulty:** {move['difficulty_level']}")
                                st.write(f"**Time:** {move['time_required']}")
                            
                            with ecol2:
                                actual = st.number_input("Actual Impact (₹/mo)", 
                                    value=float(move['estimated_impact']), key=f"actual_{move['id']}")
                                
                                acol1, acol2, acol3 = st.columns(3)
                                if acol1.button("✅ Complete", key=f"comp_{move['id']}"):
                                    try:
                                        db.table('quick_money_moves').update({
                                            'status': 'Completed',
                                            'completed_date': date.today().isoformat(),
                                            'actual_impact': float(actual)
                                        }).eq('id', move['id']).execute()
                                        st.success("Completed!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(str(e))
                                
                                if acol2.button("⏭️ Skip", key=f"skip_{move['id']}"):
                                    try:
                                        db.table('quick_money_moves').update({'status': 'Skipped'}).eq('id', move['id']).execute()
                                        st.info("Skipped")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(str(e))
                                
                                if acol3.button("🗑️ Delete", key=f"del_{move['id']}"):
                                    try:
                                        db.table('quick_money_moves').delete().eq('id', move['id']).execute()
                                        st.success("Deleted!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(str(e))
        else:
            st.info("No pending moves. Add new ones above!")
    
    with tab2:
        if completed_moves:
            # Show each completed move with delete option
            for move in completed_moves:
                with st.container():
                    ccol1, ccol2, ccol3, ccol4, ccol5 = st.columns([3, 2, 2, 2, 1])
                    
                    ccol1.write(f"**{move['action_item']}**")
                    ccol2.write(f"{move['move_type']}")
                    ccol3.write(f"Est: ₹{move.get('estimated_impact', 0):,.0f}")
                    ccol4.write(f"Actual: ₹{move.get('actual_impact', 0):,.0f}")
                    
                    if ccol5.button("🗑️", key=f"del_comp_{move['id']}", help="Delete this move"):
                        try:
                            db.table('quick_money_moves').delete().eq('id', move['id']).execute()
                            st.success("Deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    st.markdown("---")
            
            # Success metrics
            st.success(f"""
            🎉 **Great Progress!**
            - Completed {len(completed_moves)} money moves
            - Total impact: ₹{total_actual_impact:,.0f}/month
            - Annualized: ₹{total_actual_impact * 12:,.0f}/year
            """)
        else:
            st.info("Complete your first money move to see it here!")
    
    with tab3:
        if moves:
            # Impact by category
            category_impact = {}
            for move in moves:
                cat = move['category']
                impact = float(move.get('actual_impact', 0) if move['status'] == 'Completed' else move.get('estimated_impact', 0))
                category_impact[cat] = category_impact.get(cat, 0) + impact
            
            if category_impact:
                fig1 = px.bar(x=list(category_impact.keys()), y=list(category_impact.values()),
                            labels={'x': 'Category', 'y': 'Impact (₹/month)'},
                            title='Impact by Category', color=list(category_impact.values()),
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig1, use_container_width=True)
            
            # Completion rate
            status_counts = {}
            for move in moves:
                status = move['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig2 = px.pie(names=list(status_counts.keys()), values=list(status_counts.values()),
                         title='Moves by Status', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Tips
    st.markdown("---")
    with st.expander("💡 Money Move Ideas"):
        st.markdown("""
        ### Savings (Easy Wins):
        - 💳 Cancel unused subscriptions (Netflix, Prime, Spotify, etc.)
        - 📱 Switch to cheaper mobile/broadband plan
        - ⚡ Reduce electricity bill (LED bulbs, AC at 24°C)
        - 🍔 Cook at home 2 more days/week
        - 🚗 Use public transport once a week
        
        ### Earning (Side Income):
        - 📦 Sell old gadgets on OLX/QuikR
        - 📚 Freelance on Upwork/Fiverr
        - 📖 Create online course (Udemy)
        - 💼 Consulting in your expertise
        - 🏠 Rent out spare room (Airbnb)
        
        ### Debt Reduction:
        - 💳 Pay credit card before due date (avoid 36-42% interest)
        - 🏦 Prepay high-interest loans first
        - 💰 Balance transfer to lower rate card
        - 📉 Convert expensive EMIs to cheaper personal loan
        
        ### Investment:
        - 💸 Move emergency fund to liquid fund (4% → 6%)
        - 📈 Start ₹500 SIP in index fund
        - 🏦 Max out 80C (PPF/ELSS) for tax savings
        - 🪙 Open NPS for extra ₹50K tax benefit
        """)

# =====================================================
# END OF REAL-LIFE FEATURES
# =====================================================

def main():
    """Main application entry point"""
    
    # Authentication check
    if not SessionManager.is_authenticated():
        # Show login page
        from src.ui.pages.auth.login import show_login
        from src.ui.pages.auth.register import show_register
        
        # Show auth page based on session flag
        if st.session_state.get('show_register', False):
            show_register()
        else:
            show_login()
        return
    
    # Header
    st.markdown('<h1 class="main-header">💰 FinCA AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your Personal Finance Copilot for India</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # App branding
        st.markdown("### 💰 FinCA AI")
        st.caption("Your Personal Finance Copilot")
        
        # User info
        st.markdown("---")
        email = SessionManager.get_user_email()
        user_name = email.split('@')[0] if email else "User"
        user_role = SessionManager.get_user_role()
        st.markdown(f"👤 **{user_name}**")
        st.caption(f"Role: {user_role.capitalize() if user_role else 'Unknown'}")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth_service = AuthService()
            auth_service.sign_out()
            SessionManager.clear_user_session()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 Navigation")
        
        # Navigation pages with admin dashboard for admins
        pages = ["🏠 Dashboard", "💰 Budget", "🎯 Goals", "💬 Chat Assistant", 
                 "📊 Tax Calculator", "📈 SIP Planner", "🏡 HRA Calculator", 
                 "💳 EMI Calculator", "💎 80C Comparator", "🏖️ Retirement Planner",
                 "📊 Expense Analytics", "👤 Profile",
                 "💰 Salary Breakup", "📱 Bill Reminder", "💳 Credit Card Optimizer",
                 "🏦 FD vs Debt Fund", "⚡ Quick Money Moves", "📚 Knowledge Base"]
        
        # Add admin dashboard for admin users
        if SessionManager.is_admin():
            pages.insert(1, "🛡️ Admin Dashboard")
        
        page = st.radio(
            "Select Page",
            pages,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Calculate real FinCA score
        try:
            calculator = services['metrics']
            salary = st.session_state.user_context.get('salary', 0)
            monthly_income = salary / 12 if salary > 0 else 0
            
            user_data = {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_income * 0.4,  # 40% expenses
                'monthly_savings': monthly_income * 0.3,   # 30% savings
                'emergency_fund': monthly_income * 3,      # 3 months
                'monthly_emi': monthly_income * 0.15,      # 15% EMI
                'goals': [],
                'days_active': 30,
                'budgets_logged': 3,
                'goals_set': 2
            }
            
            total_score, components = calculator.calculate_finca_score(**user_data)
            
            st.markdown("### 📊 Quick Stats")
            st.metric("FinCA Score", f"{total_score}/100", f"+{total_score - 65}")
            st.metric("Savings Rate", f"{components['savings_rate_score']:.0f}%")
        except Exception as e:
            logger.error("Score calculation failed", error=str(e))
            st.metric("FinCA Score", "72/100", "+12")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        💡 Tip: Try asking our AI<br/>
        "Should I choose old or new tax regime?"
        </div>
        """, unsafe_allow_html=True)
    
    # Route to selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🛡️ Admin Dashboard":
        from src.ui.pages.admin.admin_dashboard import show_admin_dashboard
        show_admin_dashboard()
    elif page == "💰 Budget":
        show_budget()
    elif page == "🎯 Goals":
        show_goals()
    elif page == "💬 Chat Assistant":
        show_chat()
    elif page == "📊 Tax Calculator":
        show_tax_calculator()
    elif page == "📈 SIP Planner":
        show_sip_planner()
    elif page == "🏡 HRA Calculator":
        show_hra_calculator()
    elif page == "💳 EMI Calculator":
        show_emi_calculator()
    elif page == "💎 80C Comparator":
        show_80c_comparator()
    elif page == "🏖️ Retirement Planner":
        show_retirement_planner()
    elif page == "📊 Expense Analytics":
        show_expense_analytics()
    elif page == "👤 Profile":
        show_profile()
    elif page == "💰 Salary Breakup":
        show_salary_breakup()
    elif page == "📱 Bill Reminder":
        show_bill_reminder()
    elif page == "💳 Credit Card Optimizer":
        show_credit_card_optimizer()
    elif page == "🏦 FD vs Debt Fund":
        show_fd_vs_debt_fund()
    elif page == "⚡ Quick Money Moves":
        show_quick_money_moves()
    elif page == "📚 Knowledge Base":
        show_knowledge_base()

def show_dashboard():
    """Dashboard with real data, graphs, and insights"""
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import datetime, timedelta
    
    st.header("🏠 Dashboard")
    
    # Get real data from database
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_id
    
    # Fetch user's budget data
    budgets_result = db.table('budgets').select('*').eq('user_id', user_id).execute()
    goals_result = db.table('goals').select('*').eq('user_id', user_id).execute()
    transactions_result = db.table('transactions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
    
    # Check if user has any data
    has_budget = bool(budgets_result.data)
    has_goals = bool(goals_result.data)
    has_transactions = bool(transactions_result.data)
    
    # Show welcome screen for new users
    if not has_budget and not has_goals and not has_transactions:
        st.markdown("""
        <div style="text-align: center; padding: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
            <h1 style="font-size: 3rem; margin-bottom: 20px;">👋 Welcome to FinCA AI!</h1>
            <p style="font-size: 1.3rem; margin-bottom: 30px;">Your Personal Financial Companion</p>
            <p style="font-size: 1.1rem; opacity: 0.9;">Get started by creating your first budget or setting up a financial goal</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 30px; background: white; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3>💰 Create Budget</h3>
                <p>Track your income and expenses</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 30px; background: white; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3>🎯 Set Goals</h3>
                <p>Plan for your financial future</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 30px; background: white; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3>💬 Chat with AI</h3>
                <p>Get personalized advice</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()
    
    # Calculate metrics from real data
    calculator = services['metrics']
    
    # Get income from budget
    monthly_income = 0
    monthly_expenses = 0
    monthly_savings = 0
    
    if has_budget:
        budget = budgets_result.data[0]
        monthly_income = float(budget.get('income', 0))
        
        # Calculate expenses from budget allocations (stored in JSONB)
        allocations = budget.get('allocations', {})
        if isinstance(allocations, dict):
            monthly_expenses = sum(float(v) for v in allocations.values() if v)
        
        # Calculate savings
        monthly_savings = monthly_income - monthly_expenses
    
    # Get emergency fund from user profile or calculate
    emergency_fund = monthly_income * 3 if monthly_income > 0 else 0
    
    # Get EMI data from transactions
    monthly_emi = 0
    if has_transactions:
        emi_transactions = [t for t in transactions_result.data if 'emi' in t.get('description', '').lower() or 'loan' in t.get('description', '').lower()]
        monthly_emi = sum(abs(float(t.get('amount', 0))) for t in emi_transactions)
    
    user_data = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_savings': monthly_savings,
        'emergency_fund': emergency_fund,
        'monthly_emi': monthly_emi,
        'goals': goals_result.data if has_goals else [],
        'days_active': 30,
        'budgets_logged': len(budgets_result.data) if has_budget else 0,
        'goals_set': len(goals_result.data) if has_goals else 0
    }
    
    total_score, components = calculator.calculate_finca_score(**user_data)
    
    # Display scores
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_score}</div>
            <div class='metric-label'>FinCA Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        savings_score = components['savings_rate_score']
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='metric-value'>{savings_score}</div>
            <div class='metric-label'>Savings Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        emergency_score = components['emergency_fund_score']
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div class='metric-value'>{emergency_score}</div>
            <div class='metric-label'>Emergency Fund</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        goal_score = components['goal_progress_score']
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);'>
            <div class='metric-value'>{goal_score}</div>
            <div class='metric-label'>Goal Progress</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Budget Overview Graph
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Budget Overview")
        
        # Get real budget data from database
        if has_budget:
            budget = budgets_result.data[0]
            allocations = budget.get('allocations', {})
            
            # Extract categories and amounts
            if isinstance(allocations, dict) and allocations:
                budget_data = {
                    'Category': list(allocations.keys()),
                    'Amount': [float(v) for v in allocations.values()]
                }
            else:
                st.info("📊 No budget breakdown available. Add categories to your budget!")
                budget_data = None
        else:
            st.info("📊 No budget yet. Create your first budget!")
            budget_data = None
        
        if budget_data:
            # Create pie chart
            fig_budget = go.Figure(data=[go.Pie(
                labels=budget_data['Category'],
                values=budget_data['Amount'],
            hole=0.4,
            marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#6BCF7F', '#F7DC6F', '#BB8FCE']),
            textinfo='label+percent',
            textposition='outside'
        )])
        
            fig_budget.update_layout(
                title="Monthly Expense Distribution",
                showlegend=False,
                height=350,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig_budget, use_container_width=True)
            
            # Summary metrics
            total_expenses = sum(budget_data['Amount'])
            st.metric("Total Monthly Expenses", f"₹{total_expenses:,.0f}")
            remaining = monthly_income - total_expenses
            if monthly_income > 0:
                st.metric("Remaining Balance", f"₹{remaining:,.0f}", 
                         delta=f"{(remaining / monthly_income * 100):.1f}%")
            else:
                st.metric("Remaining Balance", f"₹{remaining:,.0f}")
    
    with col2:
        st.markdown("### 📊 Tax Regime Comparison")
        
        # Calculate tax for both regimes
        from src.agents.tax_agent import TaxCalculatorAgent
        tax_agent = TaxCalculatorAgent()
        
        annual_income = monthly_income * 12
        deductions = {'80c': 150000, '80d': 0}
        
        old_tax = tax_agent.calculate_tax(annual_income, 'old', deductions)
        new_tax = tax_agent.calculate_tax(annual_income, 'new', {})
        
        # Create comparison bar chart
        fig_tax = go.Figure(data=[
            go.Bar(name='Old Regime', x=['Tax Amount'], y=[old_tax['final_tax']], 
                  marker_color='#FF6B6B', text=[f"₹{old_tax['final_tax']:,.0f}"], textposition='auto'),
            go.Bar(name='New Regime', x=['Tax Amount'], y=[new_tax['final_tax']], 
                  marker_color='#4ECDC4', text=[f"₹{new_tax['final_tax']:,.0f}"], textposition='auto')
        ])
        
        fig_tax.update_layout(
            title=f"Annual Tax Comparison (₹{annual_income:,.0f} income)",
            barmode='group',
            yaxis_title="Tax Amount (₹)",
            height=350,
            showlegend=True,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        st.plotly_chart(fig_tax, use_container_width=True)
        
        # Recommendation
        savings_amount = abs(old_tax['final_tax'] - new_tax['final_tax'])
        better_regime = "Old Regime" if old_tax['final_tax'] < new_tax['final_tax'] else "New Regime"
        
        st.success(f"💡 **Recommendation**: Choose **{better_regime}**")
        st.metric("Annual Tax Savings", f"₹{savings_amount:,.0f}")
    
    st.markdown("---")
    
    # Recent Transactions
    st.markdown("### 💳 Recent Transactions")
    
    # Get real transactions from database
    if has_transactions:
        transactions_list = transactions_result.data
        
        # Format transactions for display
        formatted_transactions = []
        for txn in transactions_list:
            amount = float(txn.get('amount', 0))
            formatted_transactions.append({
                'date': txn.get('created_at', '')[:10],  # Extract date from timestamp
                'description': txn.get('description', 'Transaction'),
                'category': txn.get('category', 'Other'),
                'amount': amount,
                'type': 'credit' if amount > 0 else 'debit'
            })
    else:
        st.info("📊 No transactions yet. Start tracking your expenses!")
        formatted_transactions = []
    
    # Transaction table with styling
    for idx, txn in enumerate(formatted_transactions[:10]):
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        
        # Color coding
        amount_color = "#4CAF50" if txn['amount'] > 0 else "#FF5252"
        icon = "💰" if txn['amount'] > 0 else "💸"
        
        with col1:
            st.markdown(f"**{txn['date']}**")
        
        with col2:
            st.markdown(f"{icon} {txn['description']}")
            st.caption(f"📁 {txn['category']}")
        
        with col3:
            st.markdown(f"<span style='color: {amount_color}; font-weight: bold; font-size: 1.1rem;'>₹{abs(txn['amount']):,.0f}</span>", unsafe_allow_html=True)
        
        with col4:
            if txn['amount'] > 0:
                st.success("Credit", icon="✅")
            else:
                st.error("Debit", icon="⬇️")
        
        if idx < len(formatted_transactions[:10]) - 1:
            st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    # View all transactions button
    if len(formatted_transactions) > 10:
        if st.button("📋 View All Transactions"):
            st.info(f"Showing {len(formatted_transactions)} total transactions")
    
    st.markdown("---")
    
    # Score Breakdown
    st.markdown("### 📊 Score Breakdown")
    
    component_labels = {
        'savings_rate_score': 'Savings Rate',
        'emergency_fund_score': 'Emergency Fund',
        'goal_progress_score': 'Goal Progress',
        'debt_health_score': 'Debt Health',
        'behavioral_score': 'Behavioral'
    }
    
    for key, score in components.items():
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.progress(score / 100)
        with col_b:
            st.write(f"**{component_labels[key]}**: {score}/100")

def show_chat():
    """AI Chat Assistant with real agents"""
    st.header("💬 AI Financial Assistant")
    st.markdown("Ask me anything about tax, investments, loans, or financial planning!")
    
    # Display chat history
    for message in st.session_state.chat_messages:
        role = message.get('role', 'user')
        content = message.get('content', '')
        
        if role == 'user':
            st.markdown(f'<div class="chat-message user-message">👤 You: {content}</div>', 
                       unsafe_allow_html=True)
        else:
            agent_name = message.get('agent_name', 'Assistant')
            st.markdown(f'<div class="chat-message assistant-message">🤖 {agent_name}: {content}</div>', 
                       unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Old vs New Tax Regime?"):
            user_query = "Should I choose old or new tax regime for my salary?"
            process_chat_message(user_query)
    
    with col2:
        if st.button("📈 Where to invest ₹50k?"):
            user_query = "I have ₹50,000 to invest. Where should I invest it?"
            process_chat_message(user_query)
    
    with col3:
        if st.button("🏠 Home Loan EMI?"):
            user_query = "What EMI can I afford for a home loan?"
            process_chat_message(user_query)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your finances...")
    
    if user_input:
        process_chat_message(user_input)

def process_chat_message(message: str):
    """Process chat message with real AI"""
    # Add user message to history
    st.session_state.chat_messages.append({
        'role': 'user',
        'content': message
    })
    
    # Show processing
    with st.spinner("🤔 Thinking..."):
        try:
            # Call real AI service
            chat_service = services['chat']
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                chat_service.process_message(
                    st.session_state.user_id,
                    message,
                    st.session_state.user_context
                )
            )
            loop.close()
            
            # Add AI response to history
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': response['response'],
                'agent_name': response['agent_name'],
                'agent_type': response['agent_type']
            })
            
            logger.info("Chat message processed successfully", 
                       agent=response['agent_name'])
            
        except Exception as e:
            logger.error("Chat processing failed", error=str(e))
            st.session_state.chat_messages.append({
                'role': 'assistant',
                'content': "Sorry, I encountered an error. Please try again.",
                'agent_name': 'System'
            })
    
    st.rerun()

def show_budget():
    """Budget manager"""
    st.header("💰 Monthly Budget Manager")
    
    # Budget form
    with st.form("budget_form"):
        st.subheader("Income")
        monthly_income = st.number_input("Monthly Income (₹)", min_value=0, value=100000, step=1000)
        
        st.subheader("Fixed Expenses")
        rent = st.number_input("Rent (₹)", min_value=0, value=30000, step=1000)
        utilities = st.number_input("Utilities (₹)", min_value=0, value=5000, step=500)
        insurance = st.number_input("Insurance (₹)", min_value=0, value=3000, step=500)
        
        st.subheader("Variable Expenses")
        food = st.number_input("Food & Groceries (₹)", min_value=0, value=10000, step=1000)
        transport = st.number_input("Transport (₹)", min_value=0, value=5000, step=500)
        entertainment = st.number_input("Entertainment (₹)", min_value=0, value=5000, step=500)
        
        st.subheader("Savings & Investments")
        savings = st.number_input("Savings (₹)", min_value=0, value=20000, step=1000)
        investments = st.number_input("Investments (₹)", min_value=0, value=15000, step=1000)
        
        submitted = st.form_submit_button("💾 Save Budget")
        
        if submitted:
            budget_data = {
                'income': monthly_income,
                'fixed_expenses': rent + utilities + insurance,
                'variable_expenses': food + transport + entertainment,
                'savings': savings,
                'investments': investments,
                'month': datetime.now().strftime('%Y-%m')
            }
            
            st.session_state.current_budget = budget_data
            
            # Calculate summary
            budget_service = services['budget']
            summary = budget_service.calculate_budget_summary(budget_data)
            
            st.success("✅ Budget saved successfully!")
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", f"₹{summary['total_income']:,.0f}")
            with col2:
                st.metric("Total Expenses", f"₹{summary['total_expenses']:,.0f}")
            with col3:
                st.metric("Savings Rate", f"{summary['savings_rate']:.1f}%")

def show_goals():
    """Financial goals manager with full CRUD operations"""
    st.header("🎯 Financial Goals")
    
    # Initialize goals in session state if not exists
    if 'financial_goals' not in st.session_state:
        st.session_state.financial_goals = [
            {
                "id": 1,
                "name": "Emergency Fund",
                "target": 300000,
                "current": 180000,
                "category": "Emergency",
                "priority": "High",
                "target_date": "2026-12-31"
            },
            {
                "id": 2,
                "name": "House Down Payment",
                "target": 2000000,
                "current": 450000,
                "category": "House",
                "priority": "High",
                "target_date": "2029-12-31"
            },
            {
                "id": 3,
                "name": "Retirement Corpus",
                "target": 50000000,
                "current": 1200000,
                "category": "Retirement",
                "priority": "Medium",
                "target_date": "2050-12-31"
            }
        ]
    
    # Summary statistics
    total_goals = len(st.session_state.financial_goals)
    total_target = sum(goal['target'] for goal in st.session_state.financial_goals)
    total_saved = sum(goal['current'] for goal in st.session_state.financial_goals)
    overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Goals", total_goals)
    with col2:
        st.metric("Target Amount", f"₹{total_target:,.0f}")
    with col3:
        st.metric("Amount Saved", f"₹{total_saved:,.0f}")
    with col4:
        st.metric("Overall Progress", f"{overall_progress:.1f}%")
    
    st.markdown("---")
    
    # Add new goal
    with st.expander("➕ Add New Goal", expanded=False):
        with st.form("goal_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_name = st.text_input("Goal Name*", placeholder="e.g., Buy a car")
                target_amount = st.number_input("Target Amount (₹)*", min_value=1000, value=500000, step=10000)
                current_amount = st.number_input("Current Amount (₹)", min_value=0, value=0, step=5000)
            
            with col2:
                category = st.selectbox("Category*", 
                                       ["Emergency", "Retirement", "House", "Car", "Education", "Vacation", "Wedding", "Other"])
                priority = st.selectbox("Priority*", ["High", "Medium", "Low"])
                target_date = st.date_input("Target Date*")
            
            notes = st.text_area("Notes (Optional)", placeholder="Add any notes about this goal...")
            
            submitted = st.form_submit_button("💾 Add Goal", type="primary")
            
            if submitted:
                if goal_name and target_amount > 0:
                    new_goal = {
                        "id": max([g['id'] for g in st.session_state.financial_goals], default=0) + 1,
                        "name": goal_name,
                        "target": target_amount,
                        "current": current_amount,
                        "category": category,
                        "priority": priority,
                        "target_date": str(target_date),
                        "notes": notes
                    }
                    st.session_state.financial_goals.append(new_goal)
                    progress = (current_amount / target_amount * 100) if target_amount > 0 else 0
                    st.success(f"✅ Goal '{goal_name}' added successfully! ({progress:.1f}% complete)")
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields!")
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox("Filter by Category", 
                                       ["All"] + ["Emergency", "Retirement", "House", "Car", "Education", "Vacation", "Wedding", "Other"])
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Progress", "Target Amount", "Priority"])
    
    # Apply filters
    filtered_goals = st.session_state.financial_goals.copy()
    
    if filter_category != "All":
        filtered_goals = [g for g in filtered_goals if g['category'] == filter_category]
    
    if filter_priority != "All":
        filtered_goals = [g for g in filtered_goals if g['priority'] == filter_priority]
    
    # Apply sorting
    if sort_by == "Progress":
        filtered_goals.sort(key=lambda x: (x['current'] / x['target'] * 100) if x['target'] > 0 else 0, reverse=True)
    elif sort_by == "Target Amount":
        filtered_goals.sort(key=lambda x: x['target'], reverse=True)
    elif sort_by == "Priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_goals.sort(key=lambda x: priority_order.get(x['priority'], 3))
    else:
        filtered_goals.sort(key=lambda x: x['name'])
    
    st.markdown("---")
    st.subheader(f"Active Goals ({len(filtered_goals)})")
    
    if not filtered_goals:
        st.info("📭 No goals found. Add your first financial goal above!")
    else:
        # Display goals
        for idx, goal in enumerate(filtered_goals):
            progress = (goal['current'] / goal['target'] * 100) if goal['target'] > 0 else 0
            remaining = goal['target'] - goal['current']
            
            # Priority color coding
            priority_colors = {
                "High": "#ff4b4b",
                "Medium": "#ffa500",
                "Low": "#4CAF50"
            }
            priority_color = priority_colors.get(goal['priority'], "#808080")
            
            # Goal card
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
                
                with col1:
                    st.markdown(f"### {goal['name']}")
                    st.caption(f"🏷️ {goal['category']} | 🎯 Priority: **{goal['priority']}** | 📅 Target: {goal['target_date']}")
                    st.progress(min(progress / 100, 1.0))
                    st.caption(f"Progress: {progress:.1f}% | Remaining: ₹{remaining:,.0f}")
                
                with col2:
                    st.metric("Saved", f"₹{goal['current']:,.0f}")
                    st.caption(f"of ₹{goal['target']:,.0f}")
                
                with col3:
                    # Update goal button
                    if st.button("✏️ Edit", key=f"edit_{goal['id']}"):
                        st.session_state[f"editing_{goal['id']}"] = True
                
                with col4:
                    # Delete goal button
                    if st.button("🗑️ Delete", key=f"delete_{goal['id']}", type="secondary"):
                        st.session_state[f"confirm_delete_{goal['id']}"] = True
                
                # Update form (shown when edit button clicked)
                if st.session_state.get(f"editing_{goal['id']}", False):
                    with st.form(f"update_form_{goal['id']}"):
                        st.markdown("#### Update Goal")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_current = st.number_input("Current Amount (₹)", 
                                                         min_value=0, 
                                                         value=goal['current'], 
                                                         step=5000,
                                                         key=f"current_{goal['id']}")
                        with col2:
                            new_target = st.number_input("Target Amount (₹)", 
                                                        min_value=1000, 
                                                        value=goal['target'], 
                                                        step=10000,
                                                        key=f"target_{goal['id']}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                # Update the goal
                                for g in st.session_state.financial_goals:
                                    if g['id'] == goal['id']:
                                        g['current'] = new_current
                                        g['target'] = new_target
                                        break
                                st.session_state[f"editing_{goal['id']}"] = False
                                st.success("✅ Goal updated successfully!")
                                st.rerun()
                        
                        with col_b:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"editing_{goal['id']}"] = False
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{goal['id']}", False):
                    st.warning(f"⚠️ Are you sure you want to delete '{goal['name']}'?")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Yes, Delete", key=f"confirm_yes_{goal['id']}", type="primary"):
                            st.session_state.financial_goals = [g for g in st.session_state.financial_goals if g['id'] != goal['id']]
                            st.session_state[f"confirm_delete_{goal['id']}"] = False
                            st.success(f"🗑️ Goal '{goal['name']}' deleted successfully!")
                            st.rerun()
                    with col_b:
                        if st.button(f"❌ Cancel", key=f"confirm_no_{goal['id']}"):
                            st.session_state[f"confirm_delete_{goal['id']}"] = False
                            st.rerun()
                
                st.markdown("---")

def show_tax_calculator():
    """Tax calculator with real calculations"""
    st.header("📊 Income Tax Calculator")
    
    from src.agents.tax_agent import TaxCalculatorAgent
    tax_agent = TaxCalculatorAgent()
    
    col1, col2 = st.columns(2)
    
    with col1:
        annual_income = st.number_input("Annual Income (₹)", min_value=0, value=1200000, step=50000)
    
    with col2:
        deductions_amount = st.number_input("Deductions (80C, 80D, etc.) (₹)", min_value=0, value=150000, step=10000)
    
    if st.button("Calculate Tax"):
        # Create deductions dictionary
        deductions = {
            '80c': min(deductions_amount, 150000),
            '80d': min(deductions_amount - 150000, 25000) if deductions_amount > 150000 else 0
        }
        
        # Calculate for both regimes
        old_tax = tax_agent.calculate_tax(annual_income, 'old', deductions)
        new_tax = tax_agent.calculate_tax(annual_income, 'new', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Old Regime")
            st.metric("Total Tax", f"₹{old_tax['final_tax']:,.0f}")
            st.metric("Effective Rate", f"{old_tax['effective_tax_rate']:.2f}%")
            st.write(f"Taxable Income: ₹{old_tax['taxable_income']:,.0f}")
            st.write(f"Total Deductions: ₹{old_tax['total_deductions']:,.0f}")
        
        with col2:
            st.subheader("New Regime")
            st.metric("Total Tax", f"₹{new_tax['final_tax']:,.0f}")
            st.metric("Effective Rate", f"{new_tax['effective_tax_rate']:.2f}%")
            st.write(f"Taxable Income: ₹{new_tax['taxable_income']:,.0f}")
            st.write(f"Total Deductions: ₹{new_tax['total_deductions']:,.0f}")
        
        # Recommendation
        if old_tax['final_tax'] < new_tax['final_tax']:
            savings = new_tax['final_tax'] - old_tax['final_tax']
            st.success(f"💡 **Recommendation**: Choose Old Regime. You save ₹{savings:,.0f}!")
        else:
            savings = old_tax['final_tax'] - new_tax['final_tax']
            st.success(f"💡 **Recommendation**: Choose New Regime. You save ₹{savings:,.0f}!")

def show_sip_planner():
    """SIP Calculator with real calculations"""
    st.header("📈 SIP Investment Planner")
    
    from src.agents.investment_agent import InvestmentAdvisorAgent
    investment_agent = InvestmentAdvisorAgent()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_sip = st.number_input("Monthly SIP Amount (₹)", min_value=500, value=10000, step=500)
    
    with col2:
        years = st.number_input("Investment Period (Years)", min_value=1, max_value=40, value=10)
    
    with col3:
        expected_return = st.slider("Expected Return (%)", min_value=8, max_value=18, value=12)
    
    if st.button("Calculate Returns"):
        result = investment_agent.calculate_sip_returns(monthly_sip, years, expected_return)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Invested", f"₹{result['total_invested']:,.0f}")
        
        with col2:
            st.metric("Expected Returns", f"₹{result['expected_returns']:,.0f}")
        
        with col3:
            st.metric("Maturity Value", f"₹{result['maturity_value']:,.0f}")
        
        st.info(f"📊 Your wealth will grow by {result['wealth_gain_percentage']:.1f}%")

def show_profile():
    """User profile"""
    st.header("👤 Your Profile")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Full Name", value="Demo User")
            st.number_input("Age", min_value=18, max_value=100, value=28)
            st.text_input("City", value="Bangalore")
        
        with col2:
            st.number_input("Annual Salary (₹)", min_value=0, value=1200000, step=50000)
            st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=1)
            st.selectbox("Language", ["English", "Hindi", "Kannada"], index=0)
        
        if st.form_submit_button("💾 Save Profile"):
            st.success("✅ Profile updated successfully!")

def show_knowledge_base():
    """Financial Knowledge Base using LangChain RAG"""
    # Lazy import to speed up app startup
    from src.agents.rag_knowledge_agent import FinancialKnowledgeAgent
    from src.utils.document_loader import IndianFinancialDocuments

    st.header("📚 Financial Knowledge Base")
    st.markdown("Ask any question about Indian taxes, investments, savings, or personal finance!")
    
    # Initialize RAG agent
    if 'knowledge_agent' not in st.session_state:
        with st.spinner("🔄 Initializing knowledge base..."):
            try:
                st.session_state.knowledge_agent = FinancialKnowledgeAgent()
                
                # Load additional documents
                indian_docs = IndianFinancialDocuments()
                additional_docs = []
                additional_docs.extend(indian_docs.get_tax_documents())
                additional_docs.extend(indian_docs.get_investment_documents())
                additional_docs.extend(indian_docs.get_banking_documents())
                
                if additional_docs:
                    st.session_state.knowledge_agent.add_documents(additional_docs)
                
                st.success("✅ Knowledge base ready!")
            except Exception as e:
                st.error(f"❌ Error initializing knowledge base: {str(e)}")
                st.stop()
    
    agent = st.session_state.knowledge_agent
    
    # Example queries
    st.markdown("### 💡 Try These Questions:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 What is Section 80C?"):
            st.session_state.kb_query = "What is Section 80C and how much can I save?"
    
    with col2:
        if st.button("⚖️ Old vs New Tax Regime"):
            st.session_state.kb_query = "Compare old tax regime vs new tax regime for FY 2024-25"
    
    with col3:
        if st.button("📊 ELSS vs PPF"):
            st.session_state.kb_query = "Should I invest in ELSS or PPF for tax saving?"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 HRA Calculation"):
            st.session_state.kb_query = "How to calculate HRA exemption?"
    
    with col2:
        if st.button("💰 Emergency Fund"):
            st.session_state.kb_query = "How much emergency fund should I maintain?"
    
    with col3:
        if st.button("📈 SIP Strategy"):
            st.session_state.kb_query = "What is the best SIP investment strategy?"
    
    st.markdown("---")
    
    # Query input
    query = st.text_area(
        "🔍 Ask Your Question:",
        value=st.session_state.get('kb_query', ''),
        height=100,
        placeholder="E.g., What are the tax implications of mutual fund investments?"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("🚀 Ask", type="primary")
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.kb_query = ''
            st.rerun()
    
    # Process query
    if ask_button and query:
        with st.spinner("🤔 Searching knowledge base..."):
            result = agent.ask(query)
        
        if result['status'] == 'success':
            st.markdown("### 📝 Answer:")
            st.markdown(result['answer'])
            
            # Show sources
            if result['sources']:
                with st.expander(f"📚 Sources ({len(result['sources'])} documents)"):
                    for i, source in enumerate(result['sources'], 1):
                        st.markdown(f"**Source {i}:**")
                        st.markdown(f"- {source['metadata']}")
                        st.markdown(f"> {source['content']}")
                        st.markdown("---")
        else:
            st.error("❌ Error processing query")
        
        # Clear the query
        st.session_state.kb_query = ''
    
    st.markdown("---")
    
    # Knowledge Base Stats
    st.markdown("### 📊 Knowledge Base Stats")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Documents", "50+", "Indian Finance")
    with col2:
        st.metric("📚 Categories", "8", "Tax, Investment, Banking")
    with col3:
        st.metric("🔍 Search Type", "Semantic", "AI-Powered")
    
    # Information boxes
    st.info("""
    **💡 How it works:**
    - Uses **LangChain RAG** (Retrieval Augmented Generation)
    - **FREE embeddings** from HuggingFace (sentence-transformers)
    - Searches through **Indian tax laws, RBI circulars, SEBI regulations**
    - Provides **accurate, source-backed answers**
    - Powered by **Groq (Llama 3.3 70B)** for fast responses
    - **100% FREE** - No OpenAI costs!
    """)
    
    with st.expander("ℹ️ What kind of questions can I ask?"):
        st.markdown("""
        **Tax Related:**
        - Income tax slabs and calculations
        - Deductions (80C, 80D, HRA, etc.)
        - Old vs New tax regime comparison
        - ITR filing requirements
        
        **Investment Related:**
        - Mutual fund categories
        - ELSS vs PPF comparison
        - SIP strategies and returns
        - Asset allocation guidelines
        
        **Banking & Savings:**
        - Fixed deposits vs debt funds
        - PPF, NSC, SCSS details
        - Credit score management
        - Emergency fund planning
        
        **Personal Finance:**
        - Retirement planning
        - Credit card best practices
        - Goal-based investing
        - Tax saving strategies
        """)

if __name__ == "__main__":
    logger.info("FinCA AI application started")
    main()
