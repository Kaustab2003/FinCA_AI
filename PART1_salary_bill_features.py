"""
Real-Life Features Implementation with Database Integration
Add these functions to app_integrated.py before def main():
"""

def show_salary_breakup():
    """💰 Salary Breakup - Understand CTC vs In-Hand with Database Storage"""
    import plotly.graph_objects as go
    from datetime import datetime
    
    st.header("💰 Salary Breakup Calculator")
    st.markdown("**Understand your CTC vs In-Hand salary - Where does your money go?**")
    
    # Get database client
    from src.config.database import DatabaseClient
    db = DatabaseClient.get_client()
    user_id = st.session_state.user_context.get('email', 'demo_user_123')
    
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
    
    # Historical data
    if existing_data:
        st.markdown("---")
        with st.expander("📊 View Previous Calculations"):
            try:
                history = db.table('salary_breakup').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
                if history.data:
                    history_df = pd.DataFrame(history.data)
                    history_df['calculated_at'] = pd.to_datetime(history_df['calculated_at']).dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(history_df[['calculated_at', 'ctc', 'in_hand_salary', 'income_tax']], use_container_width=True)
            except Exception as e:
                st.error(f"Could not load history: {e}")


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
    user_id = st.session_state.user_context.get('email', 'demo_user_123')
    
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
                bcol1, bcol2, bcol3, bcol4 = st.columns([3, 2, 2, 1])
                bcol1.write(f"**{bill['bill_name']}** ({bill['category']})")
                bcol2.write(f"₹{bill['amount']:,.0f}")
                bcol3.write(f"❌ {days_overdue} days overdue")
                if bcol4.button("Mark Paid", key=f"pay_overdue_{bill['id']}"):
                    try:
                        db.table('bill_reminders').update({
                            'last_paid_date': today.isoformat(),
                            'last_paid_amount': bill['amount']
                        }).eq('id', bill['id']).execute()
                        st.success("✅ Marked as paid!")
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
                bcol1, bcol2, bcol3, bcol4 = st.columns([3, 2, 2, 1])
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
                elif bcol4.button("Pay Now", key=f"pay_{bill['id']}"):
                    try:
                        db.table('bill_reminders').update({
                            'last_paid_date': today.isoformat(),
                            'last_paid_amount': bill['amount']
                        }).eq('id', bill['id']).execute()
                        st.success("✅ Marked as paid!")
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


# Continue with remaining 3 features in next part...
