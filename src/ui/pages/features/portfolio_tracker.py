import streamlit as st
import pandas as pd
import plotly.express as px
from src.services.features_service import FeaturesService
from src.utils.session_manager import SessionManager

def show_portfolio_tracker():
    st.header("📈 Investment Portfolio")
    user_email = SessionManager.get_user_email()
    # We need user_id, but SessionManager usually stores email. 
    # Assuming we can get user_id via auth service or it's stored in session.
    # For now, let's try to get it from session state if available, or fetch via email.
    
    # Ideally SessionManager should provide user_id. 
    # Let's check how other pages get user_id. 
    # Looking at app_integrated.py, it seems user_id is often fetched from db using email.
    
    from src.services.auth_service import AuthService
    auth_service = AuthService()
    user_profile = auth_service.get_user_profile(user_email)
    
    if not user_profile:
        st.error("Please login.")
        return

    user_id = user_profile['user_id']
    service = FeaturesService()
    
    # Tabs
    tab1, tab2 = st.tabs(["My Holdings", "Add Transaction"])

    with tab1:
        holdings = service.get_portfolio(user_id)
        if holdings:
            df = pd.DataFrame(holdings)
            
            # Summary Metrics
            total_value = df['current_value'].sum() if 'current_value' in df.columns else 0
            invested_value = df['invested_value'].sum() if 'invested_value' in df.columns else 0
            pnl = total_value - invested_value
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Current Value", f"₹{total_value:,.0f}")
            c2.metric("Invested Amount", f"₹{invested_value:,.0f}")
            c3.metric("Total P&L", f"₹{pnl:,.0f}", delta_color="normal")

            # Charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Asset Allocation")
                if not df.empty:
                    fig = px.pie(df, values='quantity', names='asset_name', title='Holdings by Quantity')
                    st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df)
        else:
            st.info("No investments found. Add your first transaction!")

    with tab2:
        st.subheader("Add Buy/Sell Record")
        with st.form("portfolio_form"):
            symbol = st.text_input("Symbol / Ticker (e.g., RELIANCE)", key="symbol_input")
            qty = st.number_input("Quantity", min_value=0.01, value=1.0, key="qty_input")
            price = st.number_input("Price per Unit (₹)", min_value=0.01, value=100.0, key="price_input")
            date = st.date_input("Date", key="date_input")
            notes = st.text_input("Asset Name / Notes", key="notes_input")
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                if not symbol or not symbol.strip():
                    st.error("Please enter a valid symbol/ticker")
                elif qty <= 0:
                    st.error("Quantity must be greater than 0")
                elif price <= 0:
                    st.error("Price must be greater than 0")
                else:
                    data = {
                        "transaction_type": "buy",
                        "quantity": qty,
                        "price": price,
                        "total_amount": qty * price,
                        "transaction_date": str(date),
                        "symbol": symbol.strip().upper(),
                        "notes": notes
                    }
                    success, msg = service.add_portfolio_transaction(user_id, data)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(f"Failed to add transaction: {msg}")
