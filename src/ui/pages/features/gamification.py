import streamlit as st
from src.services.features_service import FeaturesService
from src.utils.session_manager import SessionManager
# from src.services.auth_service import AuthService  # Moved inside function

def show_gamification_hub():
    st.header("🏆 Rewards Hub")
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
        st.subheader("🎯 Active Challenges")
        challenges = service.get_active_challenges(user_id)
        if challenges:
            for c in challenges:
                progress = float(c.get('current_progress', 0)) / float(c.get('target_value', 100))
                with st.expander(f"🎯 {c.get('challenge_type', 'Challenge')} - {c.get('status', 'Active')}"):
                    st.progress(progress)
                    st.write(f"Progress: {c.get('current_progress', 0)} / {c.get('target_value', 100)}")
                    if progress >= 1.0:
                        st.success("🎉 Challenge completed!")
        else:
            st.info("No active challenges. Complete financial tasks to unlock rewards!")

        st.divider()
        st.subheader("🏅 Recent Achievements")
        # This could be expanded to show completed challenges or badges
        st.info("Achievement system coming soon!")

    with col2:
        st.subheader("🥇 Leaderboard")
        leaders = service.get_leaderboard()
        if leaders:
            for i, leader in enumerate(leaders):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📊"
                st.write(f"{medal} {leader.get('anonymous_name', 'User')} - {leader.get('score')} pts")
        else:
            st.write("Be the first to join the leaderboard!")

        st.divider()
        st.subheader("📊 Your Stats")
        # Show user statistics
        user_stats = service.get_user_stats(user_id)
        if user_stats:
            st.metric("Total Score", user_stats.get('total_score', 0))
            st.metric("Challenges Completed", user_stats.get('completed_challenges', 0))
            st.metric("Current Rank", user_stats.get('rank', 'N/A'))
        else:
            st.write("Start using the app to build your stats!")
