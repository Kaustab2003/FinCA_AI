import streamlit as st
from src.services.features_service import FeaturesService
from src.utils.session_manager import SessionManager
# from src.services.auth_service import AuthService  # Moved inside function

def show_gamification_hub():
    st.header("🏆 Rewards & Insights Hub")
    user_email = SessionManager.get_user_email()
    
    from src.services.auth_service import AuthService
    auth_service = AuthService()
    user_profile = auth_service.get_user_profile(user_email)
    
    if not user_profile:
        st.error("User profile not found.")
        return

    user_id = user_profile['user_id']
    service = FeaturesService()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📰 Market News")
        news = service.get_latest_news()
        if news:
            for item in news:
                with st.expander(f"📢 {item.get('title')}"):
                    st.write(item.get('summary'))
                    st.caption(f"Sentiment: {item.get('sentiment')} | {item.get('published_at')}")
        else:
            st.info("No recent news fetched.")

    with col2:
        st.subheader("🥇 Leaderboard")
        leaders = service.get_leaderboard()
        if leaders:
            for i, leader in enumerate(leaders):
                st.write(f"{i+1}. {leader.get('anonymous_name', 'User')} - {leader.get('score')} pts")
        else:
            st.write("Be the first to join the leaderboard!")

        st.divider()
        st.subheader("🎯 My Challenges")
        challenges = service.get_active_challenges(user_id)
        if challenges:
            for c in challenges:
                st.progress(float(c.get('current_progress', 0)) / float(c.get('target_value', 100)))
                st.caption(f"{c.get('challenge_type')} ({c.get('status')})")
        else:
            st.info("No active challenges.")
