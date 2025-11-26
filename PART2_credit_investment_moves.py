"""
Real-Life Features Part 2: Credit Card, Investment, Quick Moves
Add these functions to app_integrated.py before def main():
"""

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
    user_id = st.session_state.user_context.get('email', 'demo_user_123')
    
    # Load existing cards
    try:
        result = db.table('credit_cards').select('*').eq('user_id', user_id).order('is_primary', desc=True).execute()
        cards = result.data if result.data else []
    except Exception as e:
        st.error(f"Could not load credit cards: {e}")
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
                    db.table('credit_cards').insert(data).execute()
                    st.success(f"✅ Card '{card_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add card: {e}")
    
    # Card comparison
    st.markdown("---")
    st.subheader("💎 Your Cards Performance")
    
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
            with st.container():
                c_col1, c_col2, c_col3, c_col4 = st.columns([3, 2, 2, 2])
                
                is_best = perf['card'] == best_card['card']
                badge = "🏆 " if is_best else ""
                
                c_col1.markdown(f"**{badge}{perf['card']}**  \n<small>{perf['type']}</small>", unsafe_allow_html=True)
                c_col2.metric("Monthly Spend", f"₹{perf['monthly_spend']:,.0f}")
                c_col3.metric("Cashback", f"₹{perf['monthly_cashback']:,.0f}/mo", f"₹{perf['monthly_cashback']*12:,.0f}/yr")
                c_col4.metric("Net Benefit", f"₹{perf['annual_net_benefit']:,.0f}/yr", 
                             delta_color="normal" if perf['annual_net_benefit'] > 0 else "inverse")
                
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
    user_id = st.session_state.user_context.get('email', 'demo_user_123')
    
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
            data = {
                'user_id': user_id,
                'investment_type': 'FD vs Debt Fund',
                'principal_amount': float(principal),
                'time_period': time_period,
                'investment_horizon': 'Long-term' if time_period >= 36 else 'Short-term' if time_period <= 12 else 'Medium-term',
                'fd_rate': float(fd_rate),
                'fd_maturity': float(fd_maturity),
                'fd_tax_amount': float(fd_tax),
                'fd_post_tax_return': float(fd_post_tax),
                'debt_fund_return': float(debt_fund_return),
                'debt_fund_maturity': float(debt_maturity),
                'debt_fund_tax_amount': float(debt_tax),
                'debt_fund_post_tax_return': float(debt_post_tax),
                'recommended_option': winner,
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
                history_df['calculation_date'] = pd.to_datetime(history_df['calculation_date']).dt.strftime('%Y-%m-%d')
                display_cols = ['calculation_date', 'principal_amount', 'time_period', 'recommended_option', 'fd_post_tax_return', 'debt_fund_post_tax_return']
                st.dataframe(history_df[display_cols], use_container_width=True, hide_index=True)
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
    user_id = st.session_state.user_context.get('email', 'demo_user_123')
    
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
                    db.table('quick_money_moves').insert(data).execute()
                    st.success(f"✅ Money move '{action_item}' added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to add move: {e}")
    
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
                                
                                acol1, acol2 = st.columns(2)
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
        else:
            st.info("No pending moves. Add new ones above!")
    
    with tab2:
        if completed_moves:
            completed_df = pd.DataFrame(completed_moves)
            completed_df['completed_date'] = pd.to_datetime(completed_df['completed_date']).dt.strftime('%Y-%m-%d')
            display_cols = ['action_item', 'move_type', 'estimated_impact', 'actual_impact', 'completed_date']
            st.dataframe(completed_df[display_cols], use_container_width=True, hide_index=True)
            
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


# DONE! Now add these to navigation and routes in main()
