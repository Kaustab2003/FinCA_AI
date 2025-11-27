"""
Admin Dashboard for FinCA AI
Manage users, view system statistics, and perform administrative tasks
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.services.admin_service import AdminService
from src.utils.session_manager import SessionManager
from src.utils.logger import logger


def show_admin_dashboard():
    """Display admin dashboard"""
    
    # Require admin access
    if not SessionManager.require_admin():
        return
    
    st.title("🛡️ Admin Dashboard")
    st.markdown("---")
    
    # Initialize admin service
    if 'admin_service' not in st.session_state:
        try:
            st.session_state.admin_service = AdminService()
        except Exception as e:
            st.error("⚠️ Failed to initialize Admin Service.")
            st.info("This usually happens if the `SUPABASE_SERVICE_KEY` is missing or invalid in your `.env` file.")
            st.code("SUPABASE_SERVICE_KEY=your_service_role_key_here", language="bash")
            logger.error(f"Admin service init failed: {str(e)}")
            return
    
    admin_service = st.session_state.admin_service
    
    # Tabs for different admin sections
    tab1, tab2, tab3 = st.tabs(["📊 System Stats", "👥 User Management", "📜 Activity Logs"])
    
    with tab1:
        show_system_stats(admin_service)
    
    with tab2:
        show_user_management(admin_service)
    
    with tab3:
        show_activity_logs(admin_service)


def show_system_stats(admin_service: AdminService):
    """Display system-wide statistics"""
    
    st.subheader("System Overview")
    
    # Get system stats
    stats = admin_service.get_system_stats()
    
    if not stats:
        st.error("Failed to load system statistics")
        return
    
    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats.get('total_users', 0))
        st.metric("Active Users", stats.get('active_users', 0))
    
    with col2:
        st.metric("Inactive Users", stats.get('inactive_users', 0))
        st.metric("Recently Active (7d)", stats.get('recently_active', 0))
    
    with col3:
        st.metric("Total Budgets", stats.get('total_budgets', 0))
        st.metric("Avg Budgets/User", stats.get('avg_budgets_per_user', 0))
    
    with col4:
        st.metric("Total Goals", stats.get('total_goals', 0))
        st.metric("Avg Goals/User", stats.get('avg_goals_per_user', 0))
    
    st.markdown("---")
    
    # Transaction stats
    st.subheader("Transaction Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Transactions", stats.get('total_transactions', 0))


def show_user_management(admin_service: AdminService):
    """Display user management interface"""
    
    st.subheader("User Management")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search by email, name, or user ID", key="user_search")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear", key="clear_search"):
            st.session_state.user_search = ""
            st.rerun()
    
    # Get users
    if search_term:
        users = admin_service.search_users(search_term)
    else:
        users = admin_service.get_all_users(limit=50)
    
    if not users:
        st.info("No users found")
        return
    
    # Display users table
    st.write(f"**Showing {len(users)} users**")
    
    # Convert to DataFrame for better display
    df_users = pd.DataFrame(users)
    
    # Select columns to display
    display_columns = ['full_name', 'email', 'role', 'is_active', 'city', 'created_at']
    display_df = df_users[display_columns] if all(col in df_users.columns for col in display_columns) else df_users
    
    # Format created_at
    if 'created_at' in display_df.columns:
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    
    # User actions section
    st.subheader("User Actions")
    
    # Select user
    user_options = {f"{user['email']} ({user['full_name']})": user['user_id'] for user in users}
    selected_user_display = st.selectbox("Select User", list(user_options.keys()), key="selected_user")
    
    if selected_user_display:
        selected_user_id = user_options[selected_user_display]
        
        # Get user details
        user_details = admin_service.get_user_details(selected_user_id)
        
        if user_details:
            # Display user info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**User Information**")
                st.write(f"**Email:** {user_details.get('email', 'N/A')}")
                st.write(f"**Name:** {user_details.get('full_name', 'N/A')}")
                st.write(f"**Role:** {user_details.get('role', 'user')}")
                st.write(f"**Status:** {'Active' if user_details.get('is_active') else 'Blocked'}")
                st.write(f"**City:** {user_details.get('city', 'N/A')}")
                st.write(f"**Age:** {user_details.get('age', 'N/A')}")
            
            with col2:
                st.write("**User Statistics**")
                stats = user_details.get('stats', {})
                st.write(f"**Budgets:** {stats.get('budgets', 0)}")
                st.write(f"**Goals:** {stats.get('goals', 0)}")
                st.write(f"**Transactions:** {stats.get('transactions', 0)}")
            
            st.markdown("---")
            
            # Action buttons
            st.write("**Actions**")
            col1, col2, col3, col4 = st.columns(4)
            
            admin_id = SessionManager.get_user_id()
            current_role = user_details.get('role', 'user')
            is_active = user_details.get('is_active', True)
            
            with col1:
                if is_active:
                    if st.button("🚫 Block User", key="block_user"):
                        success, message = admin_service.block_user(selected_user_id, admin_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    if st.button("✅ Unblock User", key="unblock_user"):
                        success, message = admin_service.unblock_user(selected_user_id, admin_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            with col2:
                new_role = 'admin' if current_role == 'user' else 'user'
                button_label = f"👑 Make Admin" if new_role == 'admin' else "👤 Make User"
                
                if st.button(button_label, key="change_role"):
                    success, message = admin_service.change_user_role(selected_user_id, new_role, admin_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            with col3:
                if st.button("🔄 Refresh", key="refresh_user"):
                    st.rerun()
            
            with col4:
                # Delete with confirmation
                if 'confirm_delete' not in st.session_state:
                    st.session_state.confirm_delete = False
                
                if not st.session_state.confirm_delete:
                    if st.button("🗑️ Delete User", key="delete_user_btn"):
                        st.session_state.confirm_delete = True
                        st.rerun()
                else:
                    st.warning("⚠️ Confirm deletion?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes", key="confirm_yes"):
                            success, message = admin_service.delete_user(selected_user_id, admin_id)
                            if success:
                                st.success(message)
                                st.session_state.confirm_delete = False
                                st.rerun()
                            else:
                                st.error(message)
                    with col_no:
                        if st.button("No", key="confirm_no"):
                            st.session_state.confirm_delete = False
                            st.rerun()


def show_activity_logs(admin_service: AdminService):
    """Display activity logs"""
    
    st.subheader("User Activity Logs")
    
    # Get all users for selection
    users = admin_service.get_all_users(limit=100)
    
    if not users:
        st.info("No users found")
        return
    
    # Select user
    user_options = {f"{user['email']} ({user['full_name']})": user['user_id'] for user in users}
    selected_user_display = st.selectbox("Select User for Activity Log", list(user_options.keys()), key="activity_user")
    
    if selected_user_display:
        selected_user_id = user_options[selected_user_display]
        
        # Get activity log
        activities = admin_service.get_user_activity_log(selected_user_id, limit=50)
        
        if not activities:
            st.info("No activity found for this user")
            return
        
        # Display activity
        st.write(f"**Recent activity for {selected_user_display}**")
        
        for activity in activities:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{activity.get('type')}**")
                
                with col2:
                    st.write(activity.get('description', 'N/A'))
                
                with col3:
                    st.write(f"₹{activity.get('amount', 0):,.2f}")
                
                st.caption(activity.get('date', 'N/A'))
                st.markdown("---")


# Add custom styling
def apply_admin_styles():
    """Apply custom styles to admin dashboard"""
    st.markdown("""
        <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton button {
            border-radius: 5px;
            font-weight: 500;
        }
        
        .stDataFrame {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    apply_admin_styles()
    show_admin_dashboard()
