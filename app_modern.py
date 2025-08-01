import streamlit as st
import requests
import psycopg
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Import our custom components
from styles.modern_ui import apply_modern_theme, create_header, create_metric_card, create_leaderboard_item, create_stats_grid
from components.dashboard import (
    create_user_analytics_chart, 
    create_leaderboard_chart, 
    create_activity_timeline,
    fetch_github_profile_data,
    create_user_profile_card,
    create_achievement_badges
)

# Configure page
st.set_page_config(
    page_title="GitHub Leaderboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply modern theme
apply_modern_theme()

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Database functions (keeping your existing ones)
def connect_to_db():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

def create_accounts_table_if_not_exists(conn):
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS github_accounts (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        github_url TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

def create_scores_table_if_not_exists(conn):
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        pull_requests_opened INT DEFAULT 0,
        pull_requests_merged INT DEFAULT 0,
        issues_created INT DEFAULT 0,
        issues_closed INT DEFAULT 0,
        repos_contributed_to INT DEFAULT 0,
        starred_repositories INT DEFAULT 0,
        commit_changes INT DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

def fetch_commit_changes(username):
    headers = {"Accept": "application/vnd.github.v3+json"}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
    total_commits = 0
    try:
        repos_url = f"https://api.github.com/users/{username}/repos"
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repositories = repos_response.json()

        for repo in repositories:
            owner = repo['owner']['login']
            repo_name = repo['name']
            contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
            contributors_response = requests.get(contributors_url, headers=headers)
            contributors_response.raise_for_status()

            contributors = contributors_response.json()
            for contributor in contributors:
                if contributor['login'] == username:
                    total_commits += contributor['contributions']
                    break

        return total_commits
    except Exception as e:
        st.error(f"Error fetching commit changes: {str(e)}")
        return 0

def fetch_github_scores(username):
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}" if github_token else ""
    }
    
    if username.startswith("https://github.com/"):
        username = username.split("https://github.com/")[-1].strip("/")

    try:
        pr_opened = requests.get(
            f"https://api.github.com/search/issues?q=type:pr+author:{username}",
            headers=headers
        ).json().get("total_count", 0)

        pr_merged = requests.get(
            f"https://api.github.com/search/issues?q=type:pr+author:{username}+is:merged",
            headers=headers
        ).json().get("total_count", 0)

        issues_created = requests.get(
            f"https://api.github.com/search/issues?q=type:issue+author:{username}",
            headers=headers
        ).json().get("total_count", 0)

        issues_closed = requests.get(
            f"https://api.github.com/search/issues?q=type:issue+author:{username}+is:closed",
            headers=headers
        ).json().get("total_count", 0)

        repos_contributed_to = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers
        ).json()
        repos_contributed_to_count = len(repos_contributed_to) if isinstance(repos_contributed_to, list) else 0

        starred_repos = requests.get(
            f"https://api.github.com/users/{username}/starred",
            headers=headers
        ).json()
        starred_repos_count = len(starred_repos) if isinstance(starred_repos, list) else 0

        commit_changes = fetch_commit_changes(username)

        return {
            "pull_requests_opened": pr_opened,
            "pull_requests_merged": pr_merged,
            "issues_created": issues_created,
            "issues_closed": issues_closed,
            "repos_contributed_to": repos_contributed_to_count,
            "starred_repositories": starred_repos_count,
            "commit_changes": commit_changes
        }
    except Exception as e:
        st.error(f"Error fetching scores: {str(e)}")
        return None

def update_scores_in_db(username, scores):
    try:
        conn = connect_to_db()
        create_scores_table_if_not_exists(conn)
        cursor = conn.cursor()

        query = """
            INSERT INTO scores (
                username, pull_requests_opened, pull_requests_merged,
                issues_created, issues_closed, repos_contributed_to,
                starred_repositories, commit_changes, last_updated
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                pull_requests_opened = EXCLUDED.pull_requests_opened,
                pull_requests_merged = EXCLUDED.pull_requests_merged,
                issues_created = EXCLUDED.issues_created,
                issues_closed = EXCLUDED.issues_closed,
                repos_contributed_to = EXCLUDED.repos_contributed_to,
                starred_repositories = EXCLUDED.starred_repositories,
                commit_changes = EXCLUDED.commit_changes,
                last_updated = EXCLUDED.last_updated;
        """
        cursor.execute(query, (
            username,
            scores["pull_requests_opened"],
            scores["pull_requests_merged"],
            scores["issues_created"],
            scores["issues_closed"],
            scores["repos_contributed_to"],
            scores["starred_repositories"],
            scores["commit_changes"],
            datetime.now()
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Scores updated successfully!"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def fetch_leaderboard():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.username, (
                COALESCE(s.pull_requests_opened, 0) +
                COALESCE(s.pull_requests_merged, 0) +
                COALESCE(s.issues_created, 0) +
                COALESCE(s.issues_closed, 0) +
                COALESCE(s.repos_contributed_to, 0) +
                COALESCE(s.starred_repositories, 0) +
                COALESCE(s.commit_changes, 0)
            ) AS total_score, g.github_url
            FROM scores s
            LEFT JOIN github_accounts g ON s.username = g.username
            ORDER BY total_score DESC;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error fetching leaderboard: {str(e)}")
        return []

def validate_login(username, password):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM github_accounts WHERE username = %s", (username,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()

        if record and check_password_hash(record[0], password):
            return True, "Login successful!"
        return False, "Invalid username or password."
    except Exception as e:
        return False, f"Database error: {str(e)}"

def sign_up(github_url, password):
    try:
        username = github_url.split("https://github.com/")[-1].strip("/")
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code != 200:
            return False, "GitHub account does not exist."

        conn = connect_to_db()
        create_accounts_table_if_not_exists(conn)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_accounts WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "User already exists. Please log in."

        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO github_accounts (username, password_hash, github_url)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, password_hash, github_url))
        conn.commit()
        cursor.close()
        conn.close()

        return True, "User signed up successfully!"
    except Exception as e:
        return False, f"Error during sign-up: {str(e)}"

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Sidebar navigation
with st.sidebar:
    st.markdown(create_header("🏆 Navigation", ""), unsafe_allow_html=True)
    
    if st.session_state.page == "Dashboard" and st.session_state.current_user:
        st.success(f"Welcome, {st.session_state.current_user}!")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
        
        if st.button("📊 My Profile", use_container_width=True):
            st.session_state.page = "Profile"
        
        if st.button("🔄 Refresh Scores", use_container_width=True):
            # Refresh current user's scores
            scores = fetch_github_scores(st.session_state.current_user)
            if scores:
                success, msg = update_scores_in_db(st.session_state.current_user, scores)
                if success:
                    st.success("Scores updated!")
                else:
                    st.error(msg)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.page = "Login"
            st.session_state.current_user = None
            st.rerun()

# Main content based on current page
if st.session_state.page == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(create_header("🏆 GitHub Leaderboard", "Track and compare GitHub contributions"), unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            with tab1:
                st.subheader("Welcome Back!")
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("Login", use_container_width=True):
                    if username and password:
                        success, message = validate_login(username, password)
                        if success:
                            st.success(message)
                            st.session_state.page = "Dashboard"
                            st.session_state.current_user = username
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please fill in all fields.")
            
            with tab2:
                st.subheader("Join the Community!")
                github_url = st.text_input("GitHub Profile URL", placeholder="https://github.com/yourusername")
                password = st.text_input("Password", type="password", key="signup_password")
                
                if st.button("Sign Up", use_container_width=True):
                    if github_url and password:
                        if github_url.startswith("https://github.com/"):
                            success, message = sign_up(github_url, password)
                            if success:
                                st.success(message)
                                st.balloons()
                            else:
                                st.error(message)
                        else:
                            st.error("Please enter a valid GitHub URL (https://github.com/username)")
                    else:
                        st.warning("Please fill in all fields.")
            
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Dashboard":
    st.markdown(create_header("🏆 GitHub Leaderboard", "Community Rankings & Statistics"), unsafe_allow_html=True)
    
    # Fetch and update all users' scores
    with st.spinner("Updating leaderboard data..."):
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM github_accounts;")
            all_users = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Update scores for all users (you might want to do this less frequently in production)
            for user in all_users[:5]:  # Limit to first 5 users to avoid API rate limits
                username = user[0]
                scores = fetch_github_scores(username)
                if scores:
                    update_scores_in_db(username, scores)
        except Exception as e:
            st.error(f"Error updating scores: {str(e)}")

    # Fetch leaderboard data
    leaderboard = fetch_leaderboard()
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Top Contributors")
        
        if leaderboard:
            # Display top 10 in a styled format
            for i, (username, score, github_url) in enumerate(leaderboard[:10], 1):
                st.markdown(create_leaderboard_item(i, username, score, github_url), unsafe_allow_html=True)
            
            # Create leaderboard chart
            if len(leaderboard) > 1:
                chart = create_leaderboard_chart(leaderboard)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No users found in the leaderboard yet.")
    
    with col2:
        st.subheader("📊 Statistics")
        
        if leaderboard:
            total_users = len(leaderboard)
            total_score = sum([user[1] for user in leaderboard])
            avg_score = total_score / total_users if total_users > 0 else 0
            top_score = leaderboard[0][1] if leaderboard else 0
            
            stats = [
                {"value": total_users, "label": "Total Users"},
                {"value": f"{total_score:,}", "label": "Total Score"},
                {"value": f"{avg_score:.0f}", "label": "Average Score"},
                {"value": f"{top_score:,}", "label": "Top Score"}
            ]
            
            st.markdown(create_stats_grid(stats), unsafe_allow_html=True)
        
        # Activity timeline
        st.subheader("📈 Activity Timeline")
        activity_chart = create_activity_timeline()
        st.plotly_chart(activity_chart, use_container_width=True)

elif st.session_state.page == "Profile":
    if st.session_state.current_user:
        username = st.session_state.current_user
        st.markdown(create_header(f"👤 {username}'s Profile", "Personal Statistics & Achievements"), unsafe_allow_html=True)
        
        # Fetch user data
        with st.spinner("Loading profile data..."):
            scores = fetch_github_scores(username)
            profile_data = fetch_github_profile_data(username)
        
        if scores and profile_data:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Profile card
                st.markdown(create_user_profile_card(username, profile_data, scores), unsafe_allow_html=True)
                
                # Achievements
                achievements_html = create_achievement_badges(scores)
                if achievements_html:
                    st.markdown(achievements_html, unsafe_allow_html=True)
            
            with col2:
                # Analytics chart
                chart = create_user_analytics_chart(username, scores)
                st.plotly_chart(chart, use_container_width=True)
                
                # Detailed metrics
                st.subheader("📊 Detailed Metrics")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.markdown(create_metric_card("Pull Requests Opened", scores.get('pull_requests_opened', 0), "🔀"), unsafe_allow_html=True)
                    st.markdown(create_metric_card("Issues Created", scores.get('issues_created', 0), "🐛"), unsafe_allow_html=True)
                    st.markdown(create_metric_card("Repositories", scores.get('repos_contributed_to', 0), "📁"), unsafe_allow_html=True)
                
                with metrics_col2:
                    st.markdown(create_metric_card("Pull Requests Merged", scores.get('pull_requests_merged', 0), "✅"), unsafe_allow_html=True)
                    st.markdown(create_metric_card("Issues Closed", scores.get('issues_closed', 0), "✅"), unsafe_allow_html=True)
                    st.markdown(create_metric_card("Stars Given", scores.get('starred_repositories', 0), "⭐"), unsafe_allow_html=True)
        else:
            st.error("Failed to load profile data. Please try again later.")
    else:
        st.error("Please log in to view your profile.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d; font-size: 0.9rem;'>"
    "Built with ❤️ using Streamlit • Data sourced from GitHub API"
    "</div>",
    unsafe_allow_html=True
)
