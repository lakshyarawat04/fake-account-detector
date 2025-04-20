import streamlit as st
from detector import InstagramAudit

audit = InstagramAudit()

st.title("🕵️‍♂️ Fake Instagram Account Detector")

username = st.text_input("Enter Instagram Username")

if username:
    st.markdown("### 📄 Manual Info")
    account_age_days = st.number_input("Account Age (days)", min_value=0, step=1)
    avg_likes = st.number_input("Average Likes per Post", min_value=0.0)
    avg_comments = st.number_input("Average Comments per Post", min_value=0.0)
    stolen_content = st.selectbox("Is content stolen?", ['No', 'Yes'])

    if st.button("🔍 Analyze"):
        scraped_data = audit.scrape_profile(username) or {'username': username}
        manual_data = {
            'account_age_days': account_age_days,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'stolen_content': stolen_content == 'Yes'
        }
        combined = {**scraped_data, **manual_data}
        result = audit.analyze_account(combined)

        st.subheader("📝 Analysis Report")
        st.write(f"**Username:** @{combined['username']}")
        st.write(f"**Followers:** {combined.get('followers', 'N/A')} | **Following:** {combined.get('following', 'N/A')}")
        st.write(f"**Total Posts:** {combined.get('total_posts', 'N/A')}")
        st.write(f"**Risk Score:** {result['risk_score']}/10")
        st.write(f"**Confidence:** {result['confidence']}%")
        st.markdown(
            f"**Verdict:** {'🚨 Likely Fake Account' if result['is_fake'] else '✅ Genuine Account'}"
        )
        if result['reasons']:
            st.warning("Red Flags: " + ", ".join(result['reasons']))
