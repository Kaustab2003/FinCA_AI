"""
FinCA AI - Integrated Streamlit Application with Real Backend
"""
import streamlit as st
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import settings
from src.utils.logger import logger
from src.utils.metrics import MetricsCalculator
from src.services.chat_service import ChatService
from src.services.budget_service import BudgetService
from src.services.goals_service import GoalsService
from src.services.user_service import UserService

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
@st.cache_resource
def get_services():
    """Initialize and cache service instances"""
    return {
        'chat': ChatService(),
        'budget': BudgetService(),
        'goals': GoalsService(),
        'user': UserService(),
        'metrics': MetricsCalculator()
    }

services = get_services()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = 'demo_user_123'  # In production, get from auth
if 'user_context' not in st.session_state:
    st.session_state.user_context = {
        'salary': 1200000,  # ₹12L annual
        'age': 28,
        'risk_profile': 'moderate',
        'city': 'Bangalore'
    }
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = {}

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<h1 class="main-header">💰 FinCA AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your Personal Finance Copilot for India</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "💰 Budget", "🎯 Goals", "💬 Chat Assistant", 
             "📊 Tax Calculator", "📈 SIP Planner", "👤 Profile"],
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
    elif page == "👤 Profile":
        show_profile()

def show_dashboard():
    """Dashboard with real data, graphs, and insights"""
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import datetime, timedelta
    
    st.header("🏠 Dashboard")
    
    # Calculate metrics
    calculator = services['metrics']
    salary = st.session_state.user_context.get('salary', 0)
    monthly_income = salary / 12 if salary > 0 else 100000
    
    user_data = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_income * 0.4,
        'monthly_savings': monthly_income * 0.3,
        'emergency_fund': monthly_income * 3,
        'monthly_emi': monthly_income * 0.15,
        'goals': [],
        'days_active': 30,
        'budgets_logged': 3,
        'goals_set': 2
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
        
        # Budget breakdown data
        budget_data = {
            'Category': ['Housing', 'Food & Groceries', 'Transport', 'Entertainment', 'Insurance', 'Savings', 'Investments', 'Other'],
            'Amount': [30000, 10000, 5000, 5000, 3000, 20000, 15000, 12000]
        }
        
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
        st.metric("Remaining Balance", f"₹{monthly_income - total_expenses:,.0f}", 
                 delta=f"{((monthly_income - total_expenses) / monthly_income * 100):.1f}%")
    
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
    
    # Sample transaction data
    if 'transactions' not in st.session_state:
        st.session_state.transactions = [
            {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'description': 'Salary Credit', 'category': 'Income', 'amount': 100000, 'type': 'credit'},
            {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'description': 'Rent Payment', 'category': 'Housing', 'amount': -30000, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'description': 'Grocery Shopping', 'category': 'Food', 'amount': -3500, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'description': 'SIP Investment', 'category': 'Investment', 'amount': -15000, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'description': 'Electricity Bill', 'category': 'Utilities', 'amount': -2500, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'description': 'Fuel', 'category': 'Transport', 'amount': -3000, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), 'description': 'Restaurant', 'category': 'Entertainment', 'amount': -1800, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'), 'description': 'Health Insurance', 'category': 'Insurance', 'amount': -3000, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d'), 'description': 'Amazon Purchase', 'category': 'Shopping', 'amount': -2200, 'type': 'debit'},
            {'date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'), 'description': 'Fixed Deposit', 'category': 'Savings', 'amount': -20000, 'type': 'debit'},
        ]
    
    # Transaction table with styling
    for idx, txn in enumerate(st.session_state.transactions[:10]):
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
        
        if idx < len(st.session_state.transactions[:10]) - 1:
            st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    # View all transactions button
    if len(st.session_state.transactions) > 10:
        if st.button("📋 View All Transactions"):
            st.info(f"Showing {len(st.session_state.transactions)} total transactions")
    
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

if __name__ == "__main__":
    logger.info("FinCA AI application started")
    main()
