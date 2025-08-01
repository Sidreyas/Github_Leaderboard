import streamlit as st
import requests
import psycopg
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import time
import json

# Import our enhanced components
from styles.modern_ui import (
    apply_modern_theme, create_header, create_metric_card, 
    create_leaderboard_item, create_stats_grid, create_theme_selector,
    create_notification_toast, create_loading_spinner, create_progress_ring
)
from components.dashboard import (
    create_user_analytics_chart, create_leaderboard_chart, create_activity_timeline,
    fetch_github_profile_data, create_user_profile_card, create_achievement_badges
)
from components.advanced_analytics import GitHubAnalytics
from components.realtime_features import (
    live_activity_feed, live_stats, notification_system, simulate_live_activity
)

# Configure page
st.set_page_config(
    page_title="🏆 GitHub Leaderboard Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme from session state or default
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Apply theme
apply_modern_theme(st.session_state.theme)

# Initialize analytics
analytics = GitHubAnalytics()

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Database functions (enhanced with error handling and connection pooling)
@st.cache_resource
def get_db_connection():
    """Get database connection with connection pooling"""
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

def connect_to_db():
    """Connect to database with error handling"""
    try:
        return get_db_connection()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def create_accounts_table_if_not_exists(conn):
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS github_accounts (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        github_url TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        profile_data JSONB,
        preferences JSONB DEFAULT '{}'
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
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        historical_data JSONB DEFAULT '[]'
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

def create_activity_log_table(conn):
    """Create activity log table for real-time features"""
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS activity_log (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        action VARCHAR(100) NOT NULL,
        details TEXT,
        score_change INT DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_commit_changes(username):
    """Fetch commit changes with caching"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
    total_commits = 0
    try:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        repos_response = requests.get(repos_url, headers=headers, timeout=10)
        repos_response.raise_for_status()
        repositories = repos_response.json()

        for repo in repositories[:20]:  # Limit to first 20 repos for performance
            owner = repo['owner']['login']
            repo_name = repo['name']
            contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
            try:
                contributors_response = requests.get(contributors_url, headers=headers, timeout=5)
                contributors_response.raise_for_status()
                contributors = contributors_response.json()
                
                for contributor in contributors:
                    if contributor['login'] == username:
                        total_commits += contributor['contributions']
                        break
            except:
                continue  # Skip repos that error out

        return total_commits
    except Exception as e:
        st.warning(f"Error fetching commit data for {username}: {str(e)}")
        return 0

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_github_scores(username):
    """Enhanced GitHub score fetching with better error handling"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}" if github_token else ""
    }
    
    if username.startswith("https://github.com/"):
        username = username.split("https://github.com/")[-1].strip("/")

    try:
        # Use search API with rate limiting consideration
        pr_opened = requests.get(
            f"https://api.github.com/search/issues?q=type:pr+author:{username}&per_page=1",
            headers=headers, timeout=10
        ).json().get("total_count", 0)

        pr_merged = requests.get(
            f"https://api.github.com/search/issues?q=type:pr+author:{username}+is:merged&per_page=1",
            headers=headers, timeout=10
        ).json().get("total_count", 0)

        issues_created = requests.get(
            f"https://api.github.com/search/issues?q=type:issue+author:{username}&per_page=1",
            headers=headers, timeout=10
        ).json().get("total_count", 0)

        issues_closed = requests.get(
            f"https://api.github.com/search/issues?q=type:issue+author:{username}+is:closed&per_page=1",
            headers=headers, timeout=10
        ).json().get("total_count", 0)

        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100",
            headers=headers, timeout=10
        )
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        repos_contributed_to_count = len(repos_data) if isinstance(repos_data, list) else 0

        starred_response = requests.get(
            f"https://api.github.com/users/{username}/starred?per_page=100",
            headers=headers, timeout=10
        )
        starred_data = starred_response.json() if starred_response.status_code == 200 else []
        starred_repos_count = len(starred_data) if isinstance(starred_data, list) else 0

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
        st.error(f"Error fetching GitHub data for {username}: {str(e)}")
        return None

def update_scores_in_db(username, scores):
    """Enhanced score updating with activity logging"""
    try:
        conn = connect_to_db()
        if not conn:
            return False, "Database connection failed"
            
        create_scores_table_if_not_exists(conn)
        create_activity_log_table(conn)
        cursor = conn.cursor()

        # Get previous score for comparison
        cursor.execute("SELECT * FROM scores WHERE username = %s", (username,))
        previous_data = cursor.fetchone()
        
        total_score = sum([
            scores["pull_requests_opened"],
            scores["pull_requests_merged"] * 2,  # Weight merged PRs higher
            scores["issues_created"],
            scores["issues_closed"] * 2,  # Weight closed issues higher
            scores["repos_contributed_to"],
            scores["starred_repositories"],
            int(scores["commit_changes"] * 0.1)  # Scale down commits
        ])

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

        # Log activity if score changed
        if previous_data:
            previous_total = sum([
                previous_data[2] or 0,  # pull_requests_opened
                (previous_data[3] or 0) * 2,  # pull_requests_merged
                previous_data[4] or 0,  # issues_created
                (previous_data[5] or 0) * 2,  # issues_closed
                previous_data[6] or 0,  # repos_contributed_to
                previous_data[7] or 0,  # starred_repositories
                int((previous_data[8] or 0) * 0.1)  # commit_changes
            ])
            score_change = total_score - previous_total
            
            if score_change != 0:
                cursor.execute("""
                    INSERT INTO activity_log (username, action, details, score_change)
                    VALUES (%s, %s, %s, %s)
                """, (username, 'scored', f'Score updated to {total_score}', score_change))
                
                # Add to live feed
                simulate_live_activity(username, 'scored', f'Gained {score_change} points', score_change)

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Scores updated successfully!"
    except Exception as e:
        return False, f"Database error: {str(e)}"

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_leaderboard():
    """Enhanced leaderboard fetching with caching"""
    try:
        conn = connect_to_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.username, (
                COALESCE(s.pull_requests_opened, 0) +
                COALESCE(s.pull_requests_merged, 0) * 2 +
                COALESCE(s.issues_created, 0) +
                COALESCE(s.issues_closed, 0) * 2 +
                COALESCE(s.repos_contributed_to, 0) +
                COALESCE(s.starred_repositories, 0) +
                COALESCE(s.commit_changes, 0) * 0.1
            ) AS total_score, g.github_url, s.last_updated
            FROM scores s
            LEFT JOIN github_accounts g ON s.username = g.username
            ORDER BY total_score DESC
            LIMIT 100;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error fetching leaderboard: {str(e)}")
        return []

def validate_login(username, password):
    """Enhanced login with last login tracking"""
    try:
        conn = connect_to_db()
        if not conn:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM github_accounts WHERE username = %s", (username,))
        record = cursor.fetchone()
        
        if record and check_password_hash(record[0], password):
            # Update last login
            cursor.execute(
                "UPDATE github_accounts SET last_login = %s WHERE username = %s",
                (datetime.now(), username)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Login successful!"
        
        cursor.close()
        conn.close()
        return False, "Invalid username or password."
    except Exception as e:
        return False, f"Database error: {str(e)}"

def sign_up(github_url, password):
    """Enhanced signup with profile data fetching"""
    try:
        username = github_url.split("https://github.com/")[-1].strip("/")
        
        # Validate GitHub account and fetch profile data
        profile_response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
        if profile_response.status_code != 200:
            return False, "GitHub account does not exist."
        
        profile_data = profile_response.json()

        conn = connect_to_db()
        if not conn:
            return False, "Database connection failed"
            
        create_accounts_table_if_not_exists(conn)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM github_accounts WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "User already exists. Please log in."

        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO github_accounts (username, password_hash, github_url, profile_data)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, password_hash, github_url, json.dumps(profile_data)))
        
        # Log activity
        cursor.execute("""
            INSERT INTO activity_log (username, action, details)
            VALUES (%s, %s, %s)
        """, (username, 'joined', 'New user joined the leaderboard'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Add to live feed
        simulate_live_activity(username, 'joined', 'Welcome to the community!')
        
        return True, f"Welcome {profile_data.get('name', username)}! Account created successfully!"
    except Exception as e:
        return False, f"Error during sign-up: {str(e)}"

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Enhanced Sidebar with theme selection
with st.sidebar:
    st.markdown(create_header("🏆 GitHub Leaderboard Pro", ""), unsafe_allow_html=True)
    
    # Theme selector
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("☀️", help="Light Theme", key="light"):
            st.session_state.theme = 'light'
            st.rerun()
    with col2:
        if st.button("🌙", help="Dark Theme", key="dark"):
            st.session_state.theme = 'dark'
            st.rerun()
    with col3:
        if st.button("🚀", help="Cyberpunk Theme", key="cyberpunk"):
            st.session_state.theme = 'cyberpunk'
            st.rerun()
    with col4:
        if st.button("🌊", help="Ocean Theme", key="ocean"):
            st.session_state.theme = 'ocean'
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.page == "Dashboard" and st.session_state.current_user:
        st.success(f"Welcome, {st.session_state.current_user}!")
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", "Dashboard"),
            ("👤 My Profile", "Profile"),
            ("📊 Analytics", "Analytics"),
            ("🔄 Live Feed", "LiveFeed"),
            ("⚡ Compare", "Compare"),
            ("🏆 Achievements", "Achievements")
        ]
        
        for label, page in nav_buttons:
            if st.button(label, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        if st.button("🔄 Refresh My Scores", use_container_width=True):
            with st.spinner("Updating your scores..."):
                scores = fetch_github_scores(st.session_state.current_user)
                if scores:
                    success, msg = update_scores_in_db(st.session_state.current_user, scores)
                    if success:
                        st.success("Scores updated!")
                        st.cache_data.clear()  # Clear cache to show updated data
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Failed to fetch GitHub data")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.page = "Login"
            st.session_state.current_user = None
            st.session_state.user_data = None
            st.cache_data.clear()
            st.rerun()
    
    # Live stats in sidebar
    if st.session_state.page in ["Dashboard", "Profile", "Analytics", "LiveFeed"]:
        st.markdown("### 📡 Live Stats")
        live_stats.stats['online_users'] = np.random.randint(45, 85)  # Simulate online users
        st.markdown(live_stats.create_live_stats_html(), unsafe_allow_html=True)

# Main content based on current page
if st.session_state.page == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(create_header("🚀 GitHub Leaderboard Pro", "Next-Gen Developer Community Platform"), unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            with tab1:
                st.subheader("Welcome Back!")
                st.markdown("*Access your personalized developer dashboard*")
                
                username = st.text_input("Username", key="login_username", placeholder="Enter your GitHub username")
                password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                
                col_login1, col_login2 = st.columns(2)
                with col_login1:
                    remember_me = st.checkbox("Remember me")
                with col_login2:
                    forgot_password = st.button("Forgot Password?", type="secondary")
                
                if st.button("🚀 Login", use_container_width=True, type="primary"):
                    if username and password:
                        with st.spinner("Authenticating..."):
                            success, message = validate_login(username, password)
                            if success:
                                st.success(message)
                                st.balloons()
                                st.session_state.page = "Dashboard"
                                st.session_state.current_user = username
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Please fill in all fields.")
            
            with tab2:
                st.subheader("Join the Elite!")
                st.markdown("*Connect your GitHub and start competing*")
                
                github_url = st.text_input(
                    "GitHub Profile URL", 
                    key="signup_url",
                    placeholder="https://github.com/yourusername",
                    help="We'll validate your GitHub profile and fetch your contribution data"
                )
                password = st.text_input(
                    "Create Password", 
                    type="password", 
                    key="signup_password",
                    placeholder="Choose a secure password"
                )
                confirm_password = st.text_input(
                    "Confirm Password", 
                    type="password", 
                    key="confirm_password",
                    placeholder="Confirm your password"
                )
                
                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                if st.button("🎯 Join the Leaderboard", use_container_width=True, type="primary"):
                    if github_url and password and confirm_password:
                        if password != confirm_password:
                            st.error("Passwords don't match!")
                        elif not terms:
                            st.warning("Please accept the terms and conditions.")
                        elif not github_url.startswith("https://github.com/"):
                            st.error("Please enter a valid GitHub URL (https://github.com/username)")
                        else:
                            with st.spinner("Creating your account..."):
                                success, message = sign_up(github_url, password)
                                if success:
                                    st.success(message)
                                    st.balloons()
                                    time.sleep(2)
                                    st.session_state.page = "Login"
                                    st.rerun()
                                else:
                                    st.error(message)
                    else:
                        st.warning("Please fill in all fields.")
            
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Dashboard":
    st.markdown(create_header("🏆 GitHub Leaderboard Pro", "Elite Developer Community Dashboard"), unsafe_allow_html=True)
    
    # Auto-refresh mechanism
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # Refresh every 5 minutes
    if time.time() - st.session_state.last_refresh > 300:
        st.cache_data.clear()
        st.session_state.last_refresh = time.time()
    
    # Fetch and update leaderboard data
    with st.spinner("Loading leaderboard data..."):
        leaderboard = fetch_leaderboard()
    
    # Main dashboard layout
    col1, col2 = st.columns([2.5, 1.5])
    
    with col1:
        st.subheader("🏆 Elite Contributors Hall of Fame")
        
        if leaderboard:
            # Enhanced leaderboard display with animations
            for i, (username, score, github_url, last_updated) in enumerate(leaderboard[:15], 1):
                time_since_update = ""
                if last_updated:
                    time_diff = datetime.now() - last_updated
                    if time_diff.days > 0:
                        time_since_update = f" • Updated {time_diff.days}d ago"
                    elif time_diff.seconds > 3600:
                        time_since_update = f" • Updated {time_diff.seconds//3600}h ago"
                    else:
                        time_since_update = f" • Updated {time_diff.seconds//60}m ago"
                
                enhanced_item = create_leaderboard_item(i, username, int(score), github_url)
                # Add update time info
                enhanced_item = enhanced_item.replace(
                    f'<div class="username">', 
                    f'<div class="username">'
                ).replace(
                    '</div>        </div>',
                    f'{time_since_update}</div>        </div>'
                )
                st.markdown(enhanced_item, unsafe_allow_html=True)
            
            # Create enhanced leaderboard chart
            if len(leaderboard) > 1:
                chart = analytics.create_leaderboard_chart(leaderboard)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("🚀 Be the first to join our elite leaderboard!")
    
    with col2:
        st.subheader("📊 Live Community Stats")
        
        if leaderboard:
            total_users = len(leaderboard)
            total_score = sum([user[1] for user in leaderboard])
            avg_score = total_score / total_users if total_users > 0 else 0
            top_score = leaderboard[0][1] if leaderboard else 0
            active_today = len([user for user in leaderboard if user[3] and (datetime.now() - user[3]).days == 0])
            
            # Enhanced stats with progress rings
            stats_data = [
                {"value": total_users, "label": "Total Developers"},
                {"value": f"{int(total_score):,}", "label": "Combined Score"},
                {"value": f"{int(avg_score)}", "label": "Average Score"},
                {"value": f"{int(top_score):,}", "label": "Top Score"},
                {"value": active_today, "label": "Active Today"}
            ]
            
            # Create grid of stats with progress indicators
            for i, stat in enumerate(stats_data):
                if i < 3:  # Show progress rings for first 3 stats
                    percentage = min(100, (int(stat["value"].replace(',', '')) / 1000) * 100) if stat["value"].replace(',', '').isdigit() else 75
                    st.markdown(create_progress_ring(percentage, stat["label"]), unsafe_allow_html=True)
                else:
                    st.markdown(create_metric_card(stat["label"], stat["value"], "📊"), unsafe_allow_html=True)
        
        # Community insights
        if leaderboard and len(leaderboard) > 5:
            st.subheader("🌍 Community Insights")
            community_chart = analytics.create_community_insights(leaderboard)
            if community_chart:
                st.plotly_chart(community_chart, use_container_width=True, height=400)

elif st.session_state.page == "Profile":
    if st.session_state.current_user:
        username = st.session_state.current_user
        st.markdown(create_header(f"👤 {username}'s Elite Profile", "Personal Analytics & Performance Dashboard"), unsafe_allow_html=True)
        
        # Fetch comprehensive user data
        with st.spinner("Loading your elite profile..."):
            scores = fetch_github_scores(username)
            profile_data = fetch_github_profile_data(username)
            
            # Get user rank
            leaderboard = fetch_leaderboard()
            user_rank = None
            for i, (user, score, _, _) in enumerate(leaderboard, 1):
                if user == username:
                    user_rank = i
                    break
        
        if scores and profile_data:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Enhanced profile card
                st.markdown(create_user_profile_card(username, profile_data, scores), unsafe_allow_html=True)
                
                # AI-powered insights
                insights_report = analytics.generate_insights_report(username, scores, user_rank)
                
                # Insights card
                insights_html = f"""
                <div class="metric-card">
                    <h3 style="margin-bottom: 1rem; color: #333;">🤖 AI Insights</h3>
                    <div style="margin-bottom: 1rem;">
                        <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.9rem;">
                            {insights_report['performance_level']}
                        </span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Next Milestone:</strong><br>
                        <span style="color: #667eea;">{insights_report['next_milestone']}</span>
                    </div>
                """
                
                for insight in insights_report['insights']:
                    insights_html += f'<div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; font-size: 0.9rem;">{insight}</div>'
                
                for rec in insights_report['recommendations']:
                    insights_html += f'<div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(255, 193, 7, 0.1); border-radius: 8px; font-size: 0.9rem;">{rec}</div>'
                
                insights_html += "</div>"
                st.markdown(insights_html, unsafe_allow_html=True)
                
                # Achievements
                achievements_html = create_achievement_badges(scores)
                if achievements_html:
                    st.markdown(achievements_html, unsafe_allow_html=True)
            
            with col2:
                # Advanced analytics dashboard
                advanced_chart = analytics.create_advanced_user_dashboard(username, scores)
                st.plotly_chart(advanced_chart, use_container_width=True)
                
                # Detailed metrics with enhanced styling
                st.subheader("📊 Detailed Performance Metrics")
                
                metrics_col1, metrics_col2 = st.columns(2)
                
                metrics_data = [
                    ("Pull Requests Opened", scores.get('pull_requests_opened', 0), "🔀"),
                    ("Pull Requests Merged", scores.get('pull_requests_merged', 0), "✅"),
                    ("Issues Created", scores.get('issues_created', 0), "🐛"),
                    ("Issues Closed", scores.get('issues_closed', 0), "✅"),
                    ("Repositories", scores.get('repos_contributed_to', 0), "📁"),
                    ("Stars Given", scores.get('starred_repositories', 0), "⭐"),
                    ("Total Commits", scores.get('commit_changes', 0), "💻"),
                    ("Total Score", insights_report['total_score'], "🏆")
                ]
                
                for i, (title, value, icon) in enumerate(metrics_data):
                    col = metrics_col1 if i % 2 == 0 else metrics_col2
                    with col:
                        st.markdown(create_metric_card(title, f"{value:,}", icon), unsafe_allow_html=True)
        else:
            st.error("Failed to load profile data. Please try refreshing your scores.")
    else:
        st.error("Please log in to view your profile.")

elif st.session_state.page == "Analytics":
    st.markdown(create_header("📊 Advanced Analytics Hub", "Deep Insights & Data Intelligence"), unsafe_allow_html=True)
    
    # Fetch all user data for ML analysis
    leaderboard = fetch_leaderboard()
    
    if len(leaderboard) >= 3:
        # Prepare data for ML clustering
        all_users_data = []
        for username, _, _, _ in leaderboard:
            user_scores = fetch_github_scores(username)
            if user_scores:
                user_scores['username'] = username
                all_users_data.append(user_scores)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 AI-Powered User Segmentation")
            if len(all_users_data) >= 3:
                clustering_result = analytics.perform_user_clustering(all_users_data)
                if clustering_result:
                    cluster_chart, clusters, cluster_names = clustering_result
                    st.plotly_chart(cluster_chart, use_container_width=True)
                    
                    # Show cluster distribution
                    cluster_counts = {}
                    for i, cluster in enumerate(clusters):
                        cluster_name = cluster_names[cluster % len(cluster_names)]
                        cluster_counts[cluster_name] = cluster_counts.get(cluster_name, 0) + 1
                    
                    st.subheader("🎯 Segment Distribution")
                    for name, count in cluster_counts.items():
                        st.markdown(create_metric_card(name, count, "👥"), unsafe_allow_html=True)
        
        with col2:
            st.subheader("🌍 Community Insights")
            community_chart = analytics.create_community_insights(leaderboard)
            if community_chart:
                st.plotly_chart(community_chart, use_container_width=True)
        
        # Activity timeline
        st.subheader("📈 Community Activity Timeline")
        timeline_chart = create_activity_timeline()
        st.plotly_chart(timeline_chart, use_container_width=True)
        
    else:
        st.info("🚀 More users needed for advanced analytics. Invite your friends!")

elif st.session_state.page == "LiveFeed":
    st.markdown(create_header("📡 Live Activity Feed", "Real-time Community Updates"), unsafe_allow_html=True)
    
    # Simulate some live activities for demo
    if st.button("🔄 Refresh Live Data", type="primary"):
        # Simulate new activities
        users = ["alice", "bob", "charlie", "diana", "eve"]
        actions = ["scored", "pull_request", "issue", "commit", "achievement"]
        
        for _ in range(3):
            user = np.random.choice(users)
            action = np.random.choice(actions)
            score_change = np.random.randint(5, 50) if action == "scored" else 0
            details = f"Made awesome contributions!" if action == "scored" else f"Created new {action}"
            simulate_live_activity(user, action, details, score_change)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Live activity feed
        recent_activities = live_activity_feed.get_activities(20)
        activity_html = live_activity_feed.create_activity_stream_html(recent_activities)
        st.markdown(activity_html, unsafe_allow_html=True)
    
    with col2:
        # Live statistics
        st.markdown(live_stats.create_live_stats_html(), unsafe_allow_html=True)
        
        # Real-time notifications
        if notification_system.notifications:
            st.subheader("🔔 Recent Notifications")
            for notification in notification_system.notifications[-3:]:
                notification_html = notification_system.create_notification_html(notification)
                st.markdown(notification_html, unsafe_allow_html=True)

elif st.session_state.page == "Compare":
    st.markdown(create_header("⚡ User Comparison Arena", "Head-to-Head Performance Analysis"), unsafe_allow_html=True)
    
    leaderboard = fetch_leaderboard()
    usernames = [user[0] for user in leaderboard]
    
    if len(usernames) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            user1 = st.selectbox("Select First User", usernames, key="compare_user1")
        with col2:
            user2 = st.selectbox("Select Second User", usernames, key="compare_user2")
        
        if user1 and user2 and user1 != user2:
            if st.button("🔥 Start Comparison", type="primary", use_container_width=True):
                with st.spinner("Analyzing performance..."):
                    user1_scores = fetch_github_scores(user1)
                    user2_scores = fetch_github_scores(user2)
                    
                    if user1_scores and user2_scores:
                        # Comparison chart
                        comparison_chart = analytics.create_comparison_chart(
                            user1_scores, user2_scores, user1, user2
                        )
                        st.plotly_chart(comparison_chart, use_container_width=True)
                        
                        # Side-by-side comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader(f"👤 {user1}")
                            user1_total = sum([
                                user1_scores.get('pull_requests_opened', 0),
                                user1_scores.get('pull_requests_merged', 0) * 2,
                                user1_scores.get('issues_created', 0),
                                user1_scores.get('issues_closed', 0) * 2,
                                user1_scores.get('repos_contributed_to', 0),
                                user1_scores.get('starred_repositories', 0),
                                int(user1_scores.get('commit_changes', 0) * 0.1)
                            ])
                            st.markdown(create_metric_card("Total Score", f"{user1_total:,}", "🏆"), unsafe_allow_html=True)
                        
                        with col2:
                            st.subheader(f"👤 {user2}")
                            user2_total = sum([
                                user2_scores.get('pull_requests_opened', 0),
                                user2_scores.get('pull_requests_merged', 0) * 2,
                                user2_scores.get('issues_created', 0),
                                user2_scores.get('issues_closed', 0) * 2,
                                user2_scores.get('repos_contributed_to', 0),
                                user2_scores.get('starred_repositories', 0),
                                int(user2_scores.get('commit_changes', 0) * 0.1)
                            ])
                            st.markdown(create_metric_card("Total Score", f"{user2_total:,}", "🏆"), unsafe_allow_html=True)
                        
                        # Winner announcement
                        if user1_total > user2_total:
                            st.success(f"🏆 {user1} wins with {user1_total - user2_total:,} more points!")
                        elif user2_total > user1_total:
                            st.success(f"🏆 {user2} wins with {user2_total - user1_total:,} more points!")
                        else:
                            st.info("🤝 It's a tie! Both users have the same score.")
    else:
        st.info("Need at least 2 users for comparison. Invite more developers!")

elif st.session_state.page == "Achievements":
    st.markdown(create_header("🏆 Achievement Gallery", "Unlock Your Developer Potential"), unsafe_allow_html=True)
    
    if st.session_state.current_user:
        scores = fetch_github_scores(st.session_state.current_user)
        if scores:
            # All possible achievements
            all_achievements = [
                {"name": "PR Master", "icon": "🔀", "threshold": 50, "current": scores.get('pull_requests_merged', 0), "type": "pull_requests_merged"},
                {"name": "Bug Hunter", "icon": "🐛", "threshold": 25, "current": scores.get('issues_closed', 0), "type": "issues_closed"},
                {"name": "Code Warrior", "icon": "⚔️", "threshold": 1000, "current": scores.get('commit_changes', 0), "type": "commit_changes"},
                {"name": "Star Gazer", "icon": "⭐", "threshold": 100, "current": scores.get('starred_repositories', 0), "type": "starred_repositories"},
                {"name": "Open Source Hero", "icon": "🚀", "threshold": 20, "current": scores.get('repos_contributed_to', 0), "type": "repos_contributed_to"},
                {"name": "Issue Creator", "icon": "📝", "threshold": 50, "current": scores.get('issues_created', 0), "type": "issues_created"},
                {"name": "PR Opener", "icon": "📤", "threshold": 100, "current": scores.get('pull_requests_opened', 0), "type": "pull_requests_opened"},
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Unlocked Achievements")
                unlocked_count = 0
                for achievement in all_achievements:
                    if achievement["current"] >= achievement["threshold"]:
                        unlocked_count += 1
                        progress_percentage = 100
                        st.markdown(f"""
                        <div class="achievement-card unlocked">
                            <div class="achievement-icon">{achievement["icon"]}</div>
                            <div class="achievement-info">
                                <h4>{achievement["name"]}</h4>
                                <p>✅ Unlocked! ({achievement["current"]:,}/{achievement["threshold"]:,})</p>
                                <div class="progress-bar"><div class="progress-fill" style="width: 100%;"></div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if unlocked_count == 0:
                    st.info("🎯 Start contributing to unlock your first achievement!")
            
            with col2:
                st.subheader("🔓 Locked Achievements")
                for achievement in all_achievements:
                    if achievement["current"] < achievement["threshold"]:
                        progress_percentage = (achievement["current"] / achievement["threshold"]) * 100
                        remaining = achievement["threshold"] - achievement["current"]
                        st.markdown(f"""
                        <div class="achievement-card locked">
                            <div class="achievement-icon-locked">{achievement["icon"]}</div>
                            <div class="achievement-info">
                                <h4>{achievement["name"]}</h4>
                                <p>{remaining:,} more to unlock ({achievement["current"]:,}/{achievement["threshold"]:,})</p>
                                <div class="progress-bar"><div class="progress-fill" style="width: {progress_percentage}%;"></div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Achievement progress styles
            st.markdown("""
            <style>
            .achievement-card {
                background: var(--card-bg);
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                display: flex;
                align-items: center;
                border: 2px solid transparent;
                transition: all 0.3s ease;
            }
            
            .achievement-card.unlocked {
                border-color: var(--success-color);
                background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 184, 148, 0.1));
            }
            
            .achievement-card.locked {
                border-color: var(--border-color);
                opacity: 0.7;
            }
            
            .achievement-icon, .achievement-icon-locked {
                font-size: 3rem;
                margin-right: 1.5rem;
            }
            
            .achievement-icon-locked {
                filter: grayscale(100%);
            }
            
            .achievement-info h4 {
                margin: 0 0 0.5rem 0;
                color: var(--text-color);
            }
            
            .achievement-info p {
                margin: 0 0 0.5rem 0;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: var(--border-color);
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
                transition: width 0.3s ease;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.error("Please log in to view achievements.")

# Footer with additional info
st.markdown("---")
footer_html = f"""
<div style='text-align: center; padding: 2rem; color: var(--text-secondary); font-size: 0.9rem;'>
    <div style='margin-bottom: 1rem;'>
        <strong>🚀 GitHub Leaderboard Pro</strong> - Next-Generation Developer Community Platform
    </div>
    <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
        <span>💻 Built with Streamlit & AI</span>
        <span>📊 Real-time Analytics</span>
        <span>🤖 ML-Powered Insights</span>
        <span>🎯 Achievement System</span>
        <span>⚡ Live Updates</span>
    </div>
    <div style='margin-top: 1rem; font-size: 0.8rem;'>
        Current Theme: <strong>{st.session_state.theme.title()}</strong> | 
        Last Updated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
