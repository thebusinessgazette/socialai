import streamlit as st
import streamlit_authenticator as stauth
import json
import os
from datetime import datetime, timedelta

# === Replace these imports with your actual agent implementations ===
# Here are dummy placeholders for demonstration — replace with your real agent code.
class ProfileAnalyzerAgent:
    def run(self, url):
        # Dummy example returning a dict with some interests
        return {"profile_url": url, "top_interests": ["AI", "Tech", "Innovation"]}

class TopicResearcherAgent:
    def run(self, interests):
        # Dummy example returning some topics based on interests
        return {"topics": [f"Latest trends in {i}" for i in interests]}

class ContentCreatorAgent:
    def run(self, profile_data, topics):
        # Dummy example returning generated post text
        return f"Check out my thoughts on {', '.join(topics['topics'])}!"

class ContentReviewAgent:
    def run(self, post_text):
        # Dummy review returning approval recommendation
        return json.dumps({"recommendation": "approve", "suggestion": ""})

def schedule_post(post_text, platform, username, post_time):
    # Dummy scheduler stub — replace with actual scheduler logic or API calls
    # For demo: just print/log or pretend it schedules successfully
    print(f"Scheduled post on {platform} at {post_time} by {username}:\n{post_text}")

# =====================================================================

# --- Authentication Setup ---
users = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": stauth.Hasher(['yourpassword']).generate()[0]  # Change password here!
        }
    }
}

authenticator = stauth.Authenticate(users, "cookie_name", "signature_key", cookie_expiry_days=1)
name, authentication_status, username = authenticator.login("Login", "main")

if not authentication_status:
    st.warning("Please enter your username and password")
    st.stop()
else:
    st.success(f"Welcome {name}")

# --- Constants and Helpers ---
HISTORY_FILE = "post_history.json"

def load_post_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_post_history(entry):
    history = load_post_history()
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def update_post_history(index, new_entry):
    history = load_post_history()
    if 0 <= index < len(history):
        history[index] = new_entry
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

# --- Streamlit UI ---

st.title("🔮 AI Social Media Agent Dashboard")

# --- Session State Defaults ---
if 'profile_data' not in st.session_state:
    st.session_state['profile_data'] = None
if 'topics' not in st.session_state:
    st.session_state['topics'] = None
if 'post' not in st.session_state:
    st.session_state['post'] = ''
if 'review' not in st.session_state:
    st.session_state['review'] = None
if 'platform' not in st.session_state:
    st.session_state['platform'] = 'twitter'
if 'post_time' not in st.session_state:
    st.session_state['post_time'] = datetime.now() + timedelta(minutes=1)

# --- Layout Columns ---
col1, col2 = st.columns([3, 2])

with col1:
    st.header("1. Analyze Profile")
    profile_url = st.text_input("Enter LinkedIn/X/Bluesky Profile URL:", value=st.session_state.get('profile_url', ''))
    if st.button("Analyze Profile"):
        try:
            analyzer = ProfileAnalyzerAgent()
            profile_data = analyzer.run(profile_url)
            st.session_state['profile_data'] = profile_data
            st.session_state['profile_url'] = profile_url
            st.json(profile_data)
            st.success("Profile analyzed successfully!")
        except Exception as e:
            st.error(f"Failed to analyze profile: {e}")
            st.session_state['profile_data'] = None

with col2:
    st.header("2. Select Platform & Schedule Time")
    platform = st.selectbox("Select Platform", options=["twitter", "bluesky"], index=["twitter", "bluesky"].index(st.session_state['platform']))
    st.session_state['platform'] = platform

    post_time = st.datetime_input("Schedule Post Time", value=st.session_state['post_time'])
    st.session_state['post_time'] = post_time

# --- Research Topics ---
st.header("3. Research & Generate Post")

if st.session_state['profile_data']:
    if st.button("Research Topics"):
        try:
            topics_agent = TopicResearcherAgent()
            topics = topics_agent.run(st.session_state['profile_data'].get("top_interests", []))
            st.session_state['topics'] = topics
            st.json(topics)
            st.success("Topics researched successfully!")
        except Exception as e:
            st.error(f"Failed to research topics: {e}")
            st.session_state['topics'] = None
else:
    st.info("Analyze a profile first to start.")

# --- Generate Post ---
if st.session_state['topics']:
    if st.button("Generate Post"):
        try:
            creator = ContentCreatorAgent()
            post_generated = creator.run(st.session_state['profile_data'], st.session_state['topics'])
            st.session_state['post'] = post_generated
            st.success("Post generated successfully!")
        except Exception as e:
            st.error(f"Failed to generate post: {e}")
            st.session_state['post'] = ''

# --- Edit Post ---
if st.session_state['post']:
    post = st.text_area("Edit Generated Post", value=st.session_state['post'], height=150)
    st.session_state['post'] = post

    # Review post button
    if st.button("Review Post"):
        try:
            reviewer = ContentReviewAgent()
            review = reviewer.run(post)
            st.session_state['review'] = review
            st.text_area("Review Result", value=review, height=200)
            st.success("Post reviewed!")
        except Exception as e:
            st.error(f"Failed to review post: {e}")
            st.session_state['review'] = None

# --- Schedule Post ---
if st.session_state['post'] and st.session_state['review']:
    try:
        review_json = json.loads(st.session_state['review'])
    except Exception:
        review_json = {"recommendation": "reject", "suggestion": "Review parse error"}

    if review_json.get("recommendation") == "approve":
        if st.button("Schedule Post"):
            try:
                schedule_post(st.session_state['post'], platform=st.session_state['platform'], username=username, post_time=st.session_state['post_time'])
                save_post_history({
                    "time": st.session_state['post_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    "text": st.session_state['post'],
                    "platform": st.session_state['platform'],
                    "status": "Scheduled"
                })
                st.success("Post scheduled successfully!")
            except Exception as e:
                st.error(f"Failed to schedule post: {e}")
    else:
        st.warning(f"Post flagged by reviewer: {review_json.get('suggestion', 'No suggestion')}")

# --- Post History & Logs ---

st.header("📜 Post History & Logs")

history = load_post_history()

search_text = st.text_input("Search posts by keyword or platform")

# Filter posts by search text (case insensitive)
filtered_history = [
    (i, p) for i, p in enumerate(history)
    if search_text.lower() in p['text'].lower() or search_text.lower() in p['platform'].lower()
]

if filtered_history:
    for idx, post_entry in filtered_history[::-1]:
        with st.expander(f"{post_entry['platform'].upper()} | {post_entry['time']}"):
            st.write(post_entry['text'])
            st.write(f"Status: {post_entry['status']}")

            col_edit, col_reschedule = st.columns(2)
            with col_edit:
                if st.button(f"Edit Post #{idx}"):
                    st.session_state['post'] = post_entry['text']
                    st.session_state['platform'] = post_entry['platform']
                    try:
                        st.session_state['post_time'] = datetime.strptime(post_entry['time'], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        st.session_state['post_time'] = datetime.now() + timedelta(minutes=1)
                    st.info("Loaded post into editor. Make changes and re-schedule.")

            with col_reschedule:
                if st.button(f"Reschedule Post #{idx}"):
                    try:
                        schedule_post(post_entry['text'], platform=post_entry['platform'], username=username,
                                      post_time=datetime.strptime(post_entry['time'], "%Y-%m-%d %H:%M:%S"))
                        st.success("Post re-scheduled successfully!")
                    except Exception as e:
                        st.error(f"Failed to reschedule: {e}")

else:
    st.write("No posts found matching your search.")
