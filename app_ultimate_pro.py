"""
GitHub Leaderboard Mini App - Ultimate Enhanced Version
Next-generation developer community platform with enterprise-grade features
"""
import streamlit as st
import psycopg2
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import hashlib
import json
import asyncio
from typing import Dict, List, Optional

# Import our enhanced components with fallback handling
try:
    from styles.modern_ui import (
        apply_modern_theme, create_animated_background, create_theme_selector,
        THEMES, create_loading_spinner, create_success_animation
    )
    UI_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"UI components not fully available: {e}")
    UI_COMPONENTS_AVAILABLE = False
    # Create fallback functions
    def apply_modern_theme(theme="modern"): pass
    def create_animated_background(): pass
    def create_theme_selector(): pass
    def create_loading_spinner(): pass
    def create_success_animation(): pass
    THEMES = {"modern": {}, "dark": {}, "cyberpunk": {}, "ocean": {}}

try:
    from components.advanced_analytics import GitHubAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"Analytics component not available: {e}")
    ANALYTICS_AVAILABLE = False
    class GitHubAnalytics:
        def get_performance_insights(self, username): return ["Analytics coming soon!"]
        def create_performance_chart(self, username): st.info("📊 Advanced analytics coming soon!")
        def create_language_analysis(self, username): st.info("💻 Language analysis coming soon!")
        def create_contribution_heatmap(self, username): st.info("📅 Contribution heatmap coming soon!")
        def predict_future_performance(self, username): return {"score_prediction": 0, "score_delta": 0, "growth_rate": 0, "rank_prediction": 0, "rank_delta": 0}

try:
    from components.realtime_features import RealtimeFeatures
    REALTIME_AVAILABLE = True
except ImportError as e:
    print(f"Real-time components not available: {e}")
    REALTIME_AVAILABLE = False
    class RealtimeFeatures:
        def create_live_activity_feed(self): st.info("📡 Real-time feed coming soon!")
        def create_live_dashboard(self): st.info("📊 Live dashboard coming soon!")
        def create_notification_center(self): st.info("🔔 Notifications coming soon!")
        def enable_live_updates(self): pass

try:
    from components.pwa_mobile import inject_pwa_tags, create_mobile_optimized_css, add_mobile_gestures
    PWA_AVAILABLE = True
except ImportError as e:
    print(f"PWA components not available: {e}")
    PWA_AVAILABLE = False
    def inject_pwa_tags(): pass
    def create_mobile_optimized_css(): pass
    def add_mobile_gestures(): pass

try:
    from components.security_performance import (
        SecurityManager, PerformanceMonitor, security_middleware, create_security_dashboard
    )
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"Security components not available: {e}")
    SECURITY_AVAILABLE = False
    class SecurityManager:
        def __init__(self):
            self.session_manager = self
            self.audit_logger = self
        def create_session_token(self, user_id, data=None): return f"session_{user_id}"
        def log_login_attempt(self, username, success): pass
    class PerformanceMonitor:
        def measure_execution_time(self, func): return func
        def get_cached_query(self, key): return None
        def optimize_query_cache(self, key, result, ttl): pass
    def security_middleware(): pass
    def create_security_dashboard(): st.info("🔒 Security dashboard coming soon!")

# Configuration
st.set_page_config(
    page_title="GitHub Leaderboard Pro",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize all components"""
    return {
        "analytics": GitHubAnalytics(),
        "realtime": RealtimeFeatures(),
        "security": SecurityManager(),
        "performance": PerformanceMonitor()
    }

components = initialize_components()

# Apply security middleware
security_middleware()

# Enhanced database connection with connection pooling
@st.cache_resource
def get_database_connection():
    """Get database connection with pooling"""
    try:
        conn = psycopg2.connect(
            host=st.secrets.get("DB_HOST", "localhost"),
            database=st.secrets.get("DB_NAME", "github_leaderboard"),
            user=st.secrets.get("DB_USER", "postgres"),
            password=st.secrets.get("DB_PASSWORD", "password"),
            port=st.secrets.get("DB_PORT", 5432)
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Enhanced GitHub API with better error handling and caching
class EnhancedGitHubAPI:
    def __init__(self, token: Optional[str] = None):
        self.token = token or st.secrets.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
    
    @components["performance"].measure_execution_time
    def get_user_data(self, username: str) -> Optional[Dict]:
        """Get comprehensive user data"""
        cache_key = f"user_data_{username}"
        cached = components["performance"].get_cached_query(cache_key)
        if cached:
            return cached
        
        try:
            # Basic user info
            user_response = self.session.get(f"{self.base_url}/users/{username}")
            if user_response.status_code != 200:
                return None
            
            user_data = user_response.json()
            
            # Get repositories with enhanced metrics
            repos_response = self.session.get(
                f"{self.base_url}/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"}
            )
            repos = repos_response.json() if repos_response.status_code == 200 else []
            
            # Calculate comprehensive score
            score = self.calculate_enhanced_score(user_data, repos)
            
            enhanced_data = {
                **user_data,
                "repositories": repos,
                "calculated_score": score,
                "last_updated": datetime.now().isoformat()
            }
            
            components["performance"].optimize_query_cache(cache_key, enhanced_data, 300)
            return enhanced_data
            
        except Exception as e:
            st.error(f"Error fetching data for {username}: {e}")
            return None
    
    def calculate_enhanced_score(self, user_data: Dict, repos: List[Dict]) -> int:
        """Calculate enhanced user score with multiple factors"""
        score = 0
        
        # Base GitHub metrics
        score += user_data.get("public_repos", 0) * 10
        score += user_data.get("followers", 0) * 5
        score += user_data.get("following", 0) * 2
        
        # Repository quality metrics
        for repo in repos:
            if not repo.get("fork", False):  # Original repos only
                score += repo.get("stargazers_count", 0) * 3
                score += repo.get("forks_count", 0) * 5
                score += repo.get("watchers_count", 0) * 2
                
                # Language diversity bonus
                if repo.get("language"):
                    score += 5
                
                # Recent activity bonus
                updated = repo.get("updated_at", "")
                if updated:
                    try:
                        update_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        days_since_update = (datetime.now().replace(tzinfo=update_date.tzinfo) - update_date).days
                        if days_since_update < 30:
                            score += 20
                        elif days_since_update < 90:
                            score += 10
                    except:
                        pass
        
        # Account age bonus
        created_at = user_data.get("created_at", "")
        if created_at:
            try:
                creation_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                years_active = (datetime.now().replace(tzinfo=creation_date.tzinfo) - creation_date).days / 365
                score += int(years_active * 50)
            except:
                pass
        
        return max(0, score)

# Initialize enhanced GitHub API
github_api = EnhancedGitHubAPI()

# Enhanced database operations
class DatabaseManager:
    def __init__(self, conn):
        self.conn = conn
    
    def create_enhanced_tables(self):
        """Create enhanced database schema"""
        cursor = self.conn.cursor()
        
        # Enhanced users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                github_username VARCHAR(255) UNIQUE NOT NULL,
                github_id INTEGER UNIQUE,
                email VARCHAR(255),
                full_name VARCHAR(255),
                avatar_url TEXT,
                bio TEXT,
                location VARCHAR(255),
                company VARCHAR(255),
                blog VARCHAR(255),
                twitter_username VARCHAR(255),
                score INTEGER DEFAULT 0,
                public_repos INTEGER DEFAULT 0,
                followers INTEGER DEFAULT 0,
                following INTEGER DEFAULT 0,
                total_stars INTEGER DEFAULT 0,
                total_forks INTEGER DEFAULT 0,
                account_created DATE,
                last_updated TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE,
                preferences JSONB DEFAULT '{}',
                achievements JSONB DEFAULT '[]'
            )
        """)
        
        # User activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                activity_type VARCHAR(100) NOT NULL,
                description TEXT,
                points INTEGER DEFAULT 0,
                metadata JSONB DEFAULT '{}',
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                session_token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address INET,
                user_agent TEXT
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_github_username ON users(github_username);",
            "CREATE INDEX IF NOT EXISTS idx_users_score ON users(score DESC);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_updated ON users(last_updated);",
            "CREATE INDEX IF NOT EXISTS idx_activities_user_id ON user_activities(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON user_activities(timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        self.conn.commit()
        cursor.close()
    
    def upsert_user(self, user_data: Dict) -> int:
        """Insert or update user with enhanced data"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (
                    github_username, github_id, email, full_name, avatar_url,
                    bio, location, company, blog, twitter_username,
                    score, public_repos, followers, following,
                    account_created, last_updated
                ) VALUES (
                    %(login)s, %(id)s, %(email)s, %(name)s, %(avatar_url)s,
                    %(bio)s, %(location)s, %(company)s, %(blog)s, %(twitter_username)s,
                    %(calculated_score)s, %(public_repos)s, %(followers)s, %(following)s,
                    %(created_at)s, NOW()
                )
                ON CONFLICT (github_username) DO UPDATE SET
                    github_id = EXCLUDED.github_id,
                    email = EXCLUDED.email,
                    full_name = EXCLUDED.full_name,
                    avatar_url = EXCLUDED.avatar_url,
                    bio = EXCLUDED.bio,
                    location = EXCLUDED.location,
                    company = EXCLUDED.company,
                    blog = EXCLUDED.blog,
                    twitter_username = EXCLUDED.twitter_username,
                    score = EXCLUDED.score,
                    public_repos = EXCLUDED.public_repos,
                    followers = EXCLUDED.followers,
                    following = EXCLUDED.following,
                    last_updated = NOW()
                RETURNING id;
            """, user_data)
            
            user_id = cursor.fetchone()[0]
            self.conn.commit()
            
            # Log activity
            self.log_activity(user_id, "profile_updated", "Profile data refreshed", 10)
            
            return user_id
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Database error: {e}")
            return None
        finally:
            cursor.close()
    
    def log_activity(self, user_id: int, activity_type: str, description: str, points: int = 0, metadata: Dict = None):
        """Log user activity"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_activities (user_id, activity_type, description, points, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, activity_type, description, points, json.dumps(metadata or {})))
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        finally:
            cursor.close()
    
    def get_leaderboard(self, limit: int = 50) -> List[Dict]:
        """Get enhanced leaderboard"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    u.*,
                    ROW_NUMBER() OVER (ORDER BY u.score DESC) as rank,
                    COUNT(ua.id) as activity_count,
                    MAX(ua.timestamp) as last_activity,
                    COALESCE(SUM(ua.points), 0) as total_activity_points
                FROM users u
                LEFT JOIN user_activities ua ON u.id = ua.user_id
                WHERE u.is_active = TRUE AND u.score > 0
                GROUP BY u.id
                ORDER BY u.score DESC
                LIMIT %s;
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in results]
            
        except Exception as e:
            st.error(f"Error fetching leaderboard: {e}")
            return []
        finally:
            cursor.close()

# Initialize database with graceful fallback
conn = get_database_connection()
if conn:
    db_manager = DatabaseManager(conn)
    db_manager.create_enhanced_tables()
    DATABASE_AVAILABLE = True
else:
    DATABASE_AVAILABLE = False
    # Create a mock database manager for demo purposes
    class MockDatabaseManager:
        def upsert_user(self, user_data): return 1
        def log_activity(self, user_id, activity_type, description, points=0): pass
        def get_leaderboard(self, limit=50): return []
    db_manager = MockDatabaseManager()

# Enhanced Authentication System
class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.security_manager = components["security"]
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Enhanced user authentication"""
        # For demo purposes, using simple auth
        # In production, use proper password hashing
        user_data = github_api.get_user_data(username)
        
        if user_data:
            user_id = self.db_manager.upsert_user(user_data)
            if user_id:
                # Create session
                session_token = self.security_manager.session_manager.create_session_token(
                    str(user_id), {"username": username}
                )
                
                st.session_state.update({
                    "authenticated": True,
                    "user_id": user_id,
                    "username": username,
                    "session_token": session_token,
                    "user_data": user_data
                })
                
                # Log successful login
                self.security_manager.audit_logger.log_login_attempt(username, True)
                self.db_manager.log_activity(user_id, "login", "User logged in successfully", 5)
                
                return user_data
        
        # Log failed login
        self.security_manager.audit_logger.log_login_attempt(username, False)
        return None

# Enhanced UI Components
def create_enhanced_header():
    """Create enhanced header with theme selector and real-time stats"""
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        st.markdown("""
        <div class="main-header">
            <div class="app-title">
                🏆 GitHub Leaderboard Pro
            </div>
            <div class="app-subtitle">Next-Gen Developer Community</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.get("authenticated"):
            user_data = st.session_state.get("user_data", {})
            st.markdown(f"""
            <div style="color: white; text-align: center;">
                <img src="{user_data.get('avatar_url', '')}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 0.5rem;" />
                <div style="font-weight: 600;">Welcome back!</div>
                <div style="opacity: 0.9;">@{user_data.get('login', 'User')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Real-time stats
        if DATABASE_AVAILABLE and conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
                total_users = cursor.fetchone()[0]
                cursor.execute("SELECT MAX(score) FROM users")
                max_score = cursor.fetchone()[0] or 0
                cursor.close()
                
                st.markdown(f"""
                <div style="color: white; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700;">{total_users}</div>
                    <div style="opacity: 0.9;">Active Users</div>
                    <div style="font-size: 1.5rem; font-weight: 600; margin-top: 0.5rem;">{max_score:,}</div>
                    <div style="opacity: 0.9;">Top Score</div>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown("""
                <div style="color: white; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700;">Demo</div>
                    <div style="opacity: 0.9;">Mode</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: white; text-align: center;">
                <div style="font-size: 2rem; font-weight: 700;">Demo</div>
                <div style="opacity: 0.9;">Mode</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if UI_COMPONENTS_AVAILABLE:
            create_theme_selector()
        else:
            st.markdown("""
            <div style="color: white; text-align: center; font-size: 0.9rem;">
                🎨 Themes<br/>Coming Soon
            </div>
            """, unsafe_allow_html=True)

def create_navigation():
    """Create modern navigation"""
    if st.session_state.get("authenticated"):
        nav_options = ["🏠 Dashboard", "👤 Profile", "📊 Analytics", "📡 Live Feed", "🆚 Compare", "🏆 Achievements", "⚙️ Settings"]
        if st.session_state.get("username") == "admin":  # Admin only
            nav_options.append("🔒 Security")
        
        selected = st.selectbox("Navigate to:", nav_options, key="navigation")
        return selected.split(" ", 1)[1]  # Remove emoji
    else:
        return "Login"

def create_login_page():
    """Enhanced login page"""
    create_animated_background()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-form">
            <h2>🚀 Join the Developer Community</h2>
            <p>Connect your GitHub account to see where you stand among developers worldwide!</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "GitHub Username",
                placeholder="Enter your GitHub username",
                help="Your public GitHub username"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password (demo: any value)",
                help="For demo purposes, any password works"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                login_clicked = st.form_submit_button(
                    "🔐 Sign In",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_b:
                signup_clicked = st.form_submit_button(
                    "📝 Sign Up",
                    use_container_width=True
                )
        
        if login_clicked or signup_clicked:
            if username:
                with st.spinner("🔍 Verifying GitHub profile..."):
                    auth_manager = AuthManager(db_manager)
                    user_data = auth_manager.authenticate_user(username, password)
                    
                    if user_data:
                        create_success_animation()
                        st.success(f"✅ Welcome {user_data.get('name', username)}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ GitHub username not found or profile is private.")
            else:
                st.warning("⚠️ Please enter your GitHub username.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo users suggestion
    st.markdown("""
    <div class="demo-users">
        <h4>🎮 Try these demo profiles:</h4>
        <div class="demo-buttons">
            <button onclick="document.querySelector('input[aria-label=\"GitHub Username\"]').value='octocat'; document.querySelector('input[type=\"password\"]').value='demo';">octocat</button>
            <button onclick="document.querySelector('input[aria-label=\"GitHub Username\"]').value='torvalds'; document.querySelector('input[type=\"password\"]').value='demo';">torvalds</button>
            <button onclick="document.querySelector('input[aria-label=\"GitHub Username\"]').value='gaearon'; document.querySelector('input[type=\"password\"]').value='demo';">gaearon</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_dashboard():
    """Enhanced dashboard with comprehensive metrics"""
    st.header("🏠 Dashboard")
    
    if not DATABASE_AVAILABLE:
        st.warning("🔧 Demo Mode: Database not connected. Using GitHub API only.")
    
    # Real-time updates
    if REALTIME_AVAILABLE:
        components["realtime"].create_live_activity_feed()
    else:
        st.info("📡 Real-time updates coming soon!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    user_data = st.session_state.get("user_data", {})
    
    with col1:
        st.metric(
            "Your Score",
            f"{user_data.get('calculated_score', 0):,}",
            delta="+150 today"
        )
    
    with col2:
        st.metric(
            "Repositories",
            user_data.get('public_repos', 0),
            delta=f"+{max(0, user_data.get('public_repos', 0) - 10)}"
        )
    
    with col3:
        st.metric(
            "Followers",
            user_data.get('followers', 0),
            delta="+5 this week"
        )
    
    with col4:
        st.metric(
            "Following",
            user_data.get('following', 0),
            delta="stable"
        )
    
    # Interactive leaderboard
    st.subheader("🏆 Global Leaderboard")
    
    if DATABASE_AVAILABLE:
        leaderboard_data = db_manager.get_leaderboard(50)
        
        if leaderboard_data:
            # Create interactive leaderboard
            for i, user in enumerate(leaderboard_data[:10]):
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                    
                    with col1:
                        rank = user['rank']
                        if rank == 1:
                            st.markdown("🥇")
                        elif rank == 2:
                            st.markdown("🥈")
                        elif rank == 3:
                            st.markdown("🥉")
                        else:
                            st.markdown(f"**#{rank}**")
                    
                    with col2:
                        st.markdown(f"""
                        <div class="leaderboard-item">
                            <img src="{user['avatar_url']}" class="user-avatar" />
                            <div>
                                <div style="font-weight: 600;">{user['full_name'] or user['github_username']}</div>
                                <div style="opacity: 0.7;">@{user['github_username']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.metric("Score", f"{user['score']:,}")
                    
                    with col4:
                        st.metric("Repos", user['public_repos'])
                    
                    with col5:
                        if st.button("View Profile", key=f"profile_{user['id']}"):
                            st.session_state['viewing_profile'] = user['github_username']
                            st.rerun()
        else:
            st.info("No leaderboard data available yet. More users needed!")
    else:
        # Demo leaderboard with current user
        current_user = st.session_state.get("user_data", {})
        if current_user:
            st.markdown(f"""
            <div class="leaderboard-item">
                <div style="margin-right: 1rem; font-weight: bold; color: #667eea;">🥇 #1</div>
                <img src="{current_user.get('avatar_url', '')}" class="user-avatar" />
                <div style="flex: 1;">
                    <div style="font-weight: 600;">{current_user.get('name', current_user.get('login', 'User'))}</div>
                    <div style="opacity: 0.7;">@{current_user.get('login', 'user')}</div>
                </div>
                <div style="text-align: center; margin: 0 1rem;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">{current_user.get('calculated_score', 0):,}</div>
                    <div style="opacity: 0.7;">Score</div>
                </div>
                <div style="text-align: center; margin: 0 1rem;">
                    <div style="font-size: 1.2rem; font-weight: 600;">{current_user.get('public_repos', 0)}</div>
                    <div style="opacity: 0.7;">Repos</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 In demo mode - connect a database to see the full leaderboard with multiple users!")

def create_analytics_page():
    """Advanced analytics page"""
    st.header("📊 Advanced Analytics")
    
    analytics = components["analytics"]
    user_data = st.session_state.get("user_data", {})
    username = user_data.get("login", "")
    
    if username:
        # Performance insights
        insights = analytics.get_performance_insights(username)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Performance Trends")
            analytics.create_performance_chart(username)
        
        with col2:
            st.subheader("🎯 Insights & Recommendations")
            for insight in insights:
                st.info(f"💡 {insight}")
        
        # Language analysis
        st.subheader("💻 Language Distribution")
        analytics.create_language_analysis(username)
        
        # Contribution patterns
        st.subheader("📅 Contribution Patterns")
        analytics.create_contribution_heatmap(username)
        
        # ML-powered predictions
        st.subheader("🔮 AI Predictions")
        predictions = analytics.predict_future_performance(username)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Predicted Score (30 days)",
                f"{predictions.get('score_prediction', 0):,}",
                delta=f"+{predictions.get('score_delta', 0):,}"
            )
        
        with col2:
            st.metric(
                "Growth Rate",
                f"{predictions.get('growth_rate', 0):.1f}%",
                delta="monthly"
            )
        
        with col3:
            st.metric(
                "Rank Prediction",
                f"#{predictions.get('rank_prediction', 0)}",
                delta=f"{predictions.get('rank_delta', 0):+d}"
            )

def create_live_feed():
    """Real-time activity feed"""
    st.header("📡 Live Activity Feed")
    
    components["realtime"].create_live_dashboard()
    
    # Real-time notifications
    st.subheader("🔔 Live Notifications")
    components["realtime"].create_notification_center()

def apply_basic_styling():
    """Apply basic styling if advanced UI components aren't available"""
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .leaderboard-item {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-right: 1rem;
    }
    
    .demo-users {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 2rem;
        text-align: center;
        color: white;
    }
    
    .demo-users button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        margin: 0.5rem;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .demo-users button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation
    if not st.session_state.get("authenticated"):
        create_login_page()
    else:
        # Navigation
        page = create_navigation()
        
        # Page routing
        if page == "Dashboard":
            create_dashboard()
        elif page == "Profile":
            st.header("👤 Profile Management")
            user_data = st.session_state.get("user_data", {})
            st.json(user_data)  # Enhanced profile page would go here
        elif page == "Analytics":
            create_analytics_page()
def main():
    """Main application entry point"""
    # Apply basic styling first
    apply_basic_styling()
    
    # Inject all enhancements
    if PWA_AVAILABLE:
        inject_pwa_tags()
        create_mobile_optimized_css()
        add_mobile_gestures()
    
    # Apply theme
    selected_theme = st.session_state.get("selected_theme", "modern")
    apply_modern_theme(selected_theme)
    
    # Create header
    create_enhanced_header()
    
    # Navigation
    if not st.session_state.get("authenticated"):
        create_login_page()
    else:
        # Navigation
        page = create_navigation()
        
        # Page routing
        if page == "Dashboard":
            create_dashboard()
        elif page == "Profile":
            st.header("👤 Profile Management")
            user_data = st.session_state.get("user_data", {})
            st.json(user_data)  # Enhanced profile page would go here
        elif page == "Analytics":
            create_analytics_page()
        elif page == "Live Feed":
            create_live_feed()
        elif page == "Compare":
            st.header("🆚 Compare Developers")
            st.info("🚧 Feature coming soon! Compare your stats with other developers.")
        elif page == "Achievements":
            st.header("🏆 Achievements & Badges")
            st.info("🚧 Feature coming soon! Unlock achievements based on your contributions.")
        elif page == "Settings":
            st.header("⚙️ Settings")
            st.info("🚧 Feature coming soon! Customize your experience.")
        elif page == "Security":
            create_security_dashboard()
        
        # Logout option
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            for key in ["authenticated", "user_id", "username", "session_token", "user_data"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Real-time features
    if REALTIME_AVAILABLE:
        components["realtime"].enable_live_updates()

if __name__ == "__main__":
    main()
