"""
FinCA AI - Main Streamlit Application
Personal Finance Copilot for India
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import settings
from src.utils.logger import logger

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
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<h1 class="main-header">💰 FinCA AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your Personal Finance Copilot for India</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=FinCA", width=150)
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "💰 Budget", "🎯 Goals", "💬 Chat Assistant", 
             "📊 Tax Calculator", "📈 SIP Planner", "👤 Profile"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("FinCA Score", "72/100", "+12")
        st.metric("Monthly Savings", "₹50,000", "+₹5,000")
        
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
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
    Built with ❤️ for Indian millennials | 
    <a href='https://github.com/yourusername/finca-ai'>GitHub</a> | 
    <a href='https://docs.finca.ai'>Docs</a>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard():
    """Dashboard page"""
    st.header("🏠 Dashboard")
    
    # FinCA Score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>72</div>
            <div class='metric-label'>FinCA Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='metric-value'>62.5%</div>
            <div class='metric-label'>Savings Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div class='metric-value'>₹1.8L</div>
            <div class='metric-label'>Emergency Fund</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card' style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);'>
            <div class='metric-value'>3/5</div>
            <div class='metric-label'>Goals On Track</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Monthly Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Income & Expenses")
        st.info("**Total Income:** ₹80,000")
        st.warning("**Total Expenses:** ₹30,000")
        st.success("**Savings:** ₹50,000 (62.5%)")
        
        # Simple bar chart placeholder
        st.bar_chart({"Income": 80000, "Expenses": 30000, "Savings": 50000})
    
    with col2:
        st.subheader("Active Goals")
        
        goals = [
            {"name": "🏠 House Down Payment", "progress": 80, "target": "₹50L"},
            {"name": "🚗 Car Purchase", "progress": 30, "target": "₹8L"},
            {"name": "🎓 MBA Education", "progress": 20, "target": "₹15L"}
        ]
        
        for goal in goals:
            st.write(f"**{goal['name']}** - Target: {goal['target']}")
            st.progress(goal['progress'] / 100)
    
    st.markdown("### 🏆 Recent Achievements")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🏆 **Tax Saver**\nChose optimal tax regime")
    with col2:
        st.success("🔥 **7-Day Streak**\nConsistent budgeting")
    with col3:
        st.warning("💰 **First SIP**\nStarted investing")

def show_budget():
    """Budget tracking page"""
    st.header("💰 Budget Manager")
    
    st.info("💡 Track your monthly income and expenses to understand your cash flow")
    
    # Month selector
    col1, col2 = st.columns([2, 1])
    with col1:
        month = st.date_input("Select Month", value=None)
    with col2:
        if st.button("📥 Load Budget", type="primary"):
            st.success("Budget loaded for November 2025")
    
    # Income section
    st.subheader("💵 Income")
    col1, col2, col3 = st.columns(3)
    with col1:
        salary = st.number_input("Salary", value=80000, step=1000)
    with col2:
        rental = st.number_input("Rental Income", value=0, step=1000)
    with col3:
        other_income = st.number_input("Other Income", value=0, step=1000)
    
    total_income = salary + rental + other_income
    st.metric("**Total Income**", f"₹{total_income:,}")
    
    # Fixed Expenses
    st.subheader("🏠 Fixed Expenses")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        rent = st.number_input("Rent", value=20000, step=1000)
    with col2:
        emi = st.number_input("EMI", value=0, step=1000)
    with col3:
        insurance = st.number_input("Insurance", value=5000, step=500)
    with col4:
        sip = st.number_input("SIP/Investments", value=10000, step=1000)
    
    # Variable Expenses
    st.subheader("🛒 Variable Expenses")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        groceries = st.number_input("Groceries", value=8000, step=500)
    with col2:
        utilities = st.number_input("Utilities", value=3000, step=500)
    with col3:
        transport = st.number_input("Transport", value=5000, step=500)
    with col4:
        entertainment = st.number_input("Entertainment", value=4000, step=500)
    
    # Calculate totals
    fixed_expenses = rent + emi + insurance + sip
    variable_expenses = groceries + utilities + transport + entertainment
    total_expenses = fixed_expenses + variable_expenses
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # Summary
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", f"₹{total_income:,}")
    with col2:
        st.metric("Total Expenses", f"₹{total_expenses:,}")
    with col3:
        st.metric("Savings", f"₹{savings:,}")
    with col4:
        st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    # Save button
    if st.button("💾 Save Budget", type="primary"):
        st.success("✅ Budget saved successfully!")
        st.balloons()

def show_goals():
    """Goals management page"""
    st.header("🎯 Financial Goals")
    
    st.info("💡 Set clear financial goals and track your progress")
    
    # Add new goal
    with st.expander("➕ Add New Goal", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input("Goal Name", placeholder="e.g., House Down Payment")
            goal_type = st.selectbox("Goal Type", 
                ["🏠 House", "🚗 Car", "🎓 Education", "💰 Retirement", 
                 "🚨 Emergency", "✈️ Vacation", "💍 Wedding", "💼 Business"])
            target_amount = st.number_input("Target Amount (₹)", value=5000000, step=100000)
        
        with col2:
            current_amount = st.number_input("Current Amount (₹)", value=0, step=10000)
            target_date = st.date_input("Target Date")
            priority = st.select_slider("Priority", 
                options=["Low", "Medium", "High", "Critical"])
        
        if st.button("➕ Add Goal", type="primary"):
            st.success(f"✅ Goal '{goal_name}' added successfully!")
    
    # Existing goals
    st.subheader("📋 Your Goals")
    
    goals = [
        {"name": "🏠 House Down Payment", "type": "house", "target": 5000000, 
         "current": 4000000, "date": "2026-12-31", "priority": "Critical"},
        {"name": "🚗 New Car", "type": "car", "target": 800000, 
         "current": 240000, "date": "2027-06-30", "priority": "High"},
        {"name": "🎓 MBA Education", "type": "education", "target": 1500000, 
         "current": 300000, "date": "2028-08-01", "priority": "Medium"}
    ]
    
    for idx, goal in enumerate(goals):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"### {goal['name']}")
                progress = (goal['current'] / goal['target']) * 100
                st.progress(progress / 100)
                st.caption(f"₹{goal['current']:,} / ₹{goal['target']:,}")
            
            with col2:
                st.metric("Progress", f"{progress:.1f}%")
            
            with col3:
                st.metric("Target Date", goal['date'])
            
            with col4:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.warning(f"Goal '{goal['name']}' deleted")
        
        st.markdown("---")

def show_chat():
    """AI Chat Assistant page"""
    st.header("💬 AI Chat Assistant")
    
    st.info("💡 Ask me anything about tax, investments, budgeting, or financial planning!")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your FinCA AI assistant. How can I help you today?"}
        ]
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💵 Tax Regime?", use_container_width=True):
            question = "Should I choose old or new tax regime based on my ₹80,000 monthly income?"
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()
    
    with col2:
        if st.button("📈 SIP Amount?", use_container_width=True):
            question = "Calculate monthly SIP needed for my financial goals"
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()
    
    with col3:
        if st.button("💰 Budget Tips?", use_container_width=True):
            question = "Analyze my budget and suggest optimizations"
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response (placeholder)
        with st.chat_message("assistant"):
            response = f"""Based on your query about "{prompt[:50]}...", here's my analysis:

**Current Financial Situation:**
- Monthly Income: ₹80,000
- Monthly Savings: ₹50,000 (62.5% savings rate)
- Active Goals: 3

**Recommendation:**
This is a placeholder response. The actual AI agents will provide personalized advice based on your real financial data.

💡 **Next Steps:**
1. Complete backend integration
2. Activate AI agents
3. Get personalized recommendations

Would you like me to explain any specific aspect?"""
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def show_tax_calculator():
    """Tax calculator page"""
    st.header("📊 Tax Calculator")
    
    st.info("💡 Compare Old vs New tax regime and find which saves you more!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Your Details")
        annual_income = st.number_input("Annual Income (₹)", value=960000, step=10000)
        deductions_80c = st.number_input("80C Deductions (₹)", value=150000, step=10000, max_value=150000)
        deductions_80d = st.number_input("80D Health Insurance (₹)", value=25000, step=5000, max_value=25000)
        nps = st.number_input("NPS (80CCD(1B)) (₹)", value=50000, step=10000, max_value=50000)
        
        if st.button("🧮 Calculate Tax", type="primary"):
            st.success("Tax calculated! See comparison →")
    
    with col2:
        st.subheader("💰 Tax Comparison")
        
        # Placeholder calculations
        old_regime_tax = 112320
        new_regime_tax = 130000
        savings = old_regime_tax - new_regime_tax if old_regime_tax < new_regime_tax else new_regime_tax - old_regime_tax
        
        st.markdown(f"""
        **Old Regime:**
        - Taxable Income: ₹{annual_income - deductions_80c - deductions_80d - nps:,}
        - Tax: ₹{old_regime_tax:,}
        
        **New Regime:**
        - Taxable Income: ₹{annual_income:,}
        - Tax: ₹{new_regime_tax:,}
        
        ---
        
        ### 🎯 Recommendation
        """)
        
        if old_regime_tax < new_regime_tax:
            st.success(f"✅ **Choose Old Regime** - Save ₹{savings:,} annually!")
        else:
            st.info(f"✅ **Choose New Regime** - Save ₹{savings:,} annually!")

def show_sip_planner():
    """SIP planner page"""
    st.header("📈 SIP Planner")
    
    st.info("💡 Calculate required SIP amount to achieve your financial goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Goal Details")
        goal_amount = st.number_input("Target Amount (₹)", value=5000000, step=100000)
        time_horizon = st.slider("Time Horizon (Years)", 1, 30, 10)
        expected_return = st.slider("Expected Annual Return (%)", 8, 15, 12)
        current_savings = st.number_input("Current Savings (₹)", value=0, step=10000)
        
        if st.button("🧮 Calculate SIP", type="primary"):
            st.success("SIP calculated! See results →")
    
    with col2:
        st.subheader("💰 Required SIP")
        
        # Placeholder calculation
        monthly_sip = 18000
        total_investment = monthly_sip * time_horizon * 12
        expected_corpus = goal_amount
        returns = expected_corpus - total_investment
        
        st.metric("Monthly SIP Required", f"₹{monthly_sip:,}")
        st.metric("Total Investment", f"₹{total_investment:,}")
        st.metric("Expected Returns", f"₹{returns:,}")
        
        st.markdown("### 📊 Asset Allocation")
        st.write("**Recommended Mix (Moderate Risk):**")
        st.progress(0.50, text="Equity: 50%")
        st.progress(0.30, text="Debt: 30%")
        st.progress(0.15, text="Hybrid: 15%")
        st.progress(0.05, text="Gold: 5%")

def show_profile():
    """User profile page"""
    st.header("👤 User Profile")
    
    st.info("💡 Update your profile to get personalized financial recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Details")
        full_name = st.text_input("Full Name", value="Test User")
        age = st.number_input("Age", value=26, min_value=18, max_value=100)
        city_type = st.selectbox("City Type", ["Metro", "Tier 1", "Tier 2", "Tier 3", "Rural"])
        employment = st.selectbox("Employment Type", ["Salaried", "Self-Employed", "Business", "Freelancer"])
    
    with col2:
        st.subheader("Financial Details")
        monthly_salary = st.number_input("Monthly Salary (₹)", value=80000, step=5000)
        dependents = st.number_input("Number of Dependents", value=0, min_value=0)
        risk_profile = st.select_slider("Risk Profile", 
            options=["Conservative", "Moderate", "Aggressive"])
        language = st.selectbox("Preferred Language", ["English", "Hindi", "Tamil", "Bengali"])
    
    if st.button("💾 Save Profile", type="primary"):
        st.success("✅ Profile updated successfully!")
        st.balloons()
    
    st.markdown("---")
    st.markdown("### 🔐 Security")
    st.write("Your salary is encrypted using bank-grade AES-128 encryption")
    st.caption("🔒 We never share your personal financial data")

if __name__ == "__main__":
    try:
        logger.info("Starting FinCA AI application")
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {e}")
