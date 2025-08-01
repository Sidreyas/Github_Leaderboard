"""
Configuration settings for GitHub Leaderboard
"""

# App Configuration
APP_CONFIG = {
    "title": "🏆 GitHub Leaderboard",
    "subtitle": "Track and compare GitHub contributions",
    "page_icon": "🏆",
    "layout": "wide",
    "theme": {
        "primary_color": "#667eea",
        "secondary_color": "#764ba2",
        "background_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "card_background": "rgba(255, 255, 255, 0.95)",
        "text_color": "#333",
        "accent_color": "#6c757d"
    }
}

# Scoring Configuration
SCORING_CONFIG = {
    "weights": {
        "pull_requests_opened": 2,
        "pull_requests_merged": 5,
        "issues_created": 1,
        "issues_closed": 3,
        "repos_contributed_to": 2,
        "starred_repositories": 0.5,
        "commit_changes": 0.1
    },
    "achievement_thresholds": {
        "pr_master": 50,           # Merged PRs
        "bug_hunter": 25,          # Closed issues
        "code_warrior": 1000,      # Commits
        "star_gazer": 100,         # Starred repos
        "open_source_hero": 20     # Contributed repos
    }
}

# API Configuration
API_CONFIG = {
    "github_api_base": "https://api.github.com",
    "rate_limit_delay": 2,  # seconds between requests
    "max_retries": 3,
    "timeout": 30
}

# Database Configuration
DB_CONFIG = {
    "connection_pool_size": 10,
    "connection_timeout": 30,
    "auto_create_tables": True
}

# Background Tasks Configuration
BACKGROUND_CONFIG = {
    "update_interval_hours": 6,
    "batch_size": 5,  # Process users in batches
    "enable_notifications": True
}

# UI Configuration
UI_CONFIG = {
    "items_per_page": 20,
    "max_leaderboard_display": 100,
    "chart_height": 400,
    "enable_animations": True,
    "show_user_avatars": True,
    "enable_dark_mode": False
}

# Feature Flags
FEATURES = {
    "enable_achievements": True,
    "enable_analytics": True,
    "enable_real_time_updates": True,
    "enable_notifications": False,  # Not implemented yet
    "enable_team_features": False,  # Future feature
    "enable_export": False          # Future feature
}
