"""
Modern UI styling for GitHub Leaderboard - Mini App Edition
"""
import streamlit as st

def apply_modern_theme(theme="light"):
    """Apply modern CSS styling to the Streamlit app with theme support"""
    
    # Theme configurations
    themes = {
        "light": {
            "bg_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "card_bg": "rgba(255, 255, 255, 0.95)",
            "text_color": "#333",
            "text_secondary": "#6c757d",
            "border_color": "rgba(255, 255, 255, 0.18)",
            "shadow": "rgba(31, 38, 135, 0.37)"
        },
        "dark": {
            "bg_gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
            "card_bg": "rgba(25, 25, 25, 0.95)",
            "text_color": "#ffffff",
            "text_secondary": "#b0b0b0",
            "border_color": "rgba(255, 255, 255, 0.1)",
            "shadow": "rgba(0, 0, 0, 0.5)"
        },
        "cyberpunk": {
            "bg_gradient": "linear-gradient(135deg, #0f3460 0%, #e94560 100%)",
            "card_bg": "rgba(15, 52, 96, 0.9)",
            "text_color": "#00ff9f",
            "text_secondary": "#ff6b6b",
            "border_color": "rgba(0, 255, 159, 0.3)",
            "shadow": "rgba(233, 69, 96, 0.4)"
        },
        "ocean": {
            "bg_gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "card_bg": "rgba(255, 255, 255, 0.9)",
            "text_color": "#2d3436",
            "text_secondary": "#636e72",
            "border_color": "rgba(116, 185, 255, 0.3)",
            "shadow": "rgba(9, 132, 227, 0.3)"
        }
    }
    
    current_theme = themes.get(theme, themes["light"])
    
    st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* CSS Variables for theming */
    :root {{
        --bg-gradient: {current_theme["bg_gradient"]};
        --card-bg: {current_theme["card_bg"]};
        --text-color: {current_theme["text_color"]};
        --text-secondary: {current_theme["text_secondary"]};
        --border-color: {current_theme["border_color"]};
        --shadow-color: {current_theme["shadow"]};
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #00d4aa;
        --warning-color: #ff9f43;
        --error-color: #ff6b6b;
    }}
    
    /* Global Styling */
    .stApp {{
        background: var(--bg-gradient);
        font-family: 'Inter', sans-serif;
        color: var(--text-color);
    }}
    
    /* Hide Streamlit branding and menu */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* Custom Animations */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    @keyframes glow {{
        0% {{ box-shadow: 0 0 5px var(--primary-color); }}
        50% {{ box-shadow: 0 0 20px var(--primary-color), 0 0 30px var(--primary-color); }}
        100% {{ box-shadow: 0 0 5px var(--primary-color); }}
    }}
    
    /* Main container */
    .main-container {{
        background: var(--card-bg);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 32px 0 var(--shadow-color);
        border: 1px solid var(--border-color);
        animation: fadeInUp 0.6s ease-out;
    }}
    
    /* Header styling */
    .header-container {{
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
    }}
    
    .app-title {{
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    .app-subtitle {{
        font-size: 1.3rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin-bottom: 1rem;
    }}
    
    /* Theme Toggle */
    .theme-toggle {{
        position: absolute;
        top: 0;
        right: 0;
        background: var(--card-bg);
        border: 2px solid var(--primary-color);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    .theme-toggle:hover {{
        background: var(--primary-color);
        color: white;
        transform: scale(1.1);
    }}
    
    /* Enhanced Card styling */
    .metric-card {{
        background: var(--card-bg);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 35px 0 rgba(0, 0, 0, 0.2);
    }}
    
    .metric-card:hover::before {{
        left: 100%;
    }}
    
    /* Advanced Leaderboard styling */
    .leaderboard-item {{
        background: var(--card-bg);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        border-left: 5px solid var(--primary-color);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .leaderboard-item:hover {{
        transform: translateX(10px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        border-left-width: 8px;
    }}
    
    .rank-badge {{
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        animation: pulse 2s infinite;
    }}
    
    .user-info {{
        flex-grow: 1;
        margin-left: 1.5rem;
    }}
    
    .username {{
        font-weight: 600;
        font-size: 1.2rem;
        color: var(--text-color);
        transition: color 0.3s ease;
    }}
    
    .username:hover {{
        color: var(--primary-color);
    }}
    
    .score {{
        font-weight: 800;
        font-size: 1.5rem;
        color: var(--primary-color);
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* Enhanced Button styling */
    .stButton > button {{
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 30px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
    }}
    
    .stButton > button:hover::before {{
        left: 100%;
    }}
    
    .stButton > button:active {{
        transform: translateY(-1px);
    }}
    
    /* Enhanced Input styling */
    .stTextInput > div > div > input {{
        border-radius: 15px;
        border: 2px solid var(--border-color);
        padding: 1rem;
        transition: all 0.3s ease;
        background: var(--card-bg);
        color: var(--text-color);
        font-size: 1rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 0.3rem rgba(102, 126, 234, 0.25);
        outline: none;
    }}
    
    /* Enhanced Success/Error messages */
    .stSuccess {{
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid var(--success-color);
        border-radius: 15px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    .stError {{
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid var(--error-color);
        border-radius: 15px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    .stWarning {{
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid var(--warning-color);
        border-radius: 15px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    /* Enhanced Stats grid */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }}
    
    .stat-item {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .stat-item::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transition: all 0.3s ease;
        transform: scale(0);
    }}
    
    .stat-item:hover {{
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }}
    
    .stat-item:hover::before {{
        transform: scale(1);
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 800;
        display: block;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.5rem;
    }}
    
    .stat-label {{
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Sidebar styling */
    .stSidebar {{
        background: var(--card-bg);
        border-right: 1px solid var(--border-color);
    }}
    
    .stSidebar > div {{
        background: transparent;
    }}
    
    /* Charts and visualizations */
    .stPlotlyChart {{
        background: var(--card-bg);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }}
    
    /* Progress bars */
    .stProgress > div > div > div > div {{
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: var(--card-bg);
        border-radius: 15px;
        padding: 0.8rem 1.5rem;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-color: var(--primary-color);
    }}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {{
        .app-title {{
            font-size: 2.5rem;
        }}
        
        .main-container {{
            margin: 0.5rem;
            padding: 1.5rem;
        }}
        
        .stats-grid {{
            grid-template-columns: 1fr;
        }}
        
        .leaderboard-item {{
            flex-direction: column;
            text-align: center;
            gap: 1rem;
        }}
        
        .user-info {{
            margin-left: 0;
        }}
    }}
    
    /* Dark mode specific adjustments */
    @media (prefers-color-scheme: dark) {{
        .metric-card, .leaderboard-item, .stat-item {{
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, icon="📊"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: #333; font-size: 1.1rem;">{title}</h3>
                <p style="margin: 0; font-size: 2rem; font-weight: 700; color: #667eea;">{value}</p>
            </div>
            <div style="font-size: 2rem;">{icon}</div>
        </div>
    </div>
    """

def create_leaderboard_item(rank, username, score, github_url=None):
    """Create a styled leaderboard item"""
    github_link = f'<a href="{github_url}" target="_blank" style="text-decoration: none; color: #667eea;">@{username}</a>' if github_url else f"@{username}"
    
    # Determine rank badge color
    badge_color = "#FFD700" if rank == 1 else "#C0C0C0" if rank == 2 else "#CD7F32" if rank == 3 else "#667eea"
    
    return f"""
    <div class="leaderboard-item">
        <div class="rank-badge" style="background: {badge_color};">
            {rank}
        </div>
        <div class="user-info">
            <div class="username">{github_link}</div>
        </div>
        <div class="score">{score:,}</div>
    </div>
    """

def create_header(title, subtitle):
    """Create a styled header"""
    return f"""
    <div class="header-container">
        <h1 class="app-title">{title}</h1>
        <p class="app-subtitle">{subtitle}</p>
    </div>
    """

def create_stats_grid(stats):
    """Create a stats grid layout"""
    stats_html = ""
    for stat in stats:
        stats_html += f"""
        <div class="stat-item">
            <span class="stat-number">{stat['value']}</span>
            <span class="stat-label">{stat['label']}</span>
        </div>
        """
    
    return f'<div class="stats-grid">{stats_html}</div>'

def create_theme_selector():
    """Create theme selector component"""
    return """
    <div class="theme-selector">
        <button onclick="changeTheme('light')" class="theme-btn" title="Light Theme">☀️</button>
        <button onclick="changeTheme('dark')" class="theme-btn" title="Dark Theme">🌙</button>
        <button onclick="changeTheme('cyberpunk')" class="theme-btn" title="Cyberpunk Theme">🚀</button>
        <button onclick="changeTheme('ocean')" class="theme-btn" title="Ocean Theme">🌊</button>
    </div>
    
    <script>
    function changeTheme(theme) {
        localStorage.setItem('theme', theme);
        location.reload();
    }
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
    """

def create_notification_toast(message, type="info"):
    """Create notification toast"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    return f"""
    <div class="toast toast-{type}">
        <span class="toast-icon">{icons.get(type, "ℹ️")}</span>
        <span class="toast-message">{message}</span>
    </div>
    
    <style>
    .toast {{
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--card-bg);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border-left: 4px solid var(--primary-color);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }}
    
    .toast-success {{ border-left-color: var(--success-color); }}
    .toast-error {{ border-left-color: var(--error-color); }}
    .toast-warning {{ border-left-color: var(--warning-color); }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); }}
        to {{ transform: translateX(0); }}
    }}
    </style>
    """

def create_loading_spinner():
    """Create loading spinner component"""
    return """
    <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading amazing data...</p>
    </div>
    
    <style>
    .loading-spinner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid var(--border-color);
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """

def create_progress_ring(percentage, label):
    """Create circular progress ring"""
    circumference = 2 * 22/7 * 45  # radius = 45
    stroke_dasharray = circumference
    stroke_dashoffset = circumference - (percentage / 100) * circumference
    
    return f"""
    <div class="progress-ring-container">
        <svg class="progress-ring" width="120" height="120">
            <circle cx="60" cy="60" r="45" fill="transparent" stroke="var(--border-color)" stroke-width="8"/>
            <circle cx="60" cy="60" r="45" fill="transparent" stroke="var(--primary-color)" 
                    stroke-width="8" stroke-dasharray="{stroke_dasharray}" 
                    stroke-dashoffset="{stroke_dashoffset}" stroke-linecap="round"
                    style="transition: stroke-dashoffset 0.5s ease-in-out;"/>
        </svg>
        <div class="progress-text">
            <span class="progress-percentage">{percentage}%</span>
            <span class="progress-label">{label}</span>
        </div>
    </div>
    
    <style>
    .progress-ring-container {{
        position: relative;
        display: inline-block;
        margin: 1rem;
    }}
    
    .progress-ring {{
        transform: rotate(-90deg);
    }}
    
    .progress-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }}
    
    .progress-percentage {{
        display: block;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }}
    
    .progress-label {{
        display: block;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }}
    </style>
    """
