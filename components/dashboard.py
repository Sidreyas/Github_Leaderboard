"""
Enhanced dashboard components with data visualization
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import requests

def create_user_analytics_chart(username, scores_data):
    """Create analytics charts for individual user"""
    
    # Contribution distribution pie chart
    contribution_data = {
        'Type': ['Pull Requests', 'Issues', 'Commits', 'Repositories', 'Stars'],
        'Count': [
            scores_data.get('pull_requests_opened', 0) + scores_data.get('pull_requests_merged', 0),
            scores_data.get('issues_created', 0) + scores_data.get('issues_closed', 0),
            scores_data.get('commit_changes', 0),
            scores_data.get('repos_contributed_to', 0),
            scores_data.get('starred_repositories', 0)
        ]
    }
    
    fig_pie = px.pie(
        values=contribution_data['Count'],
        names=contribution_data['Type'],
        title=f"{username}'s Contribution Distribution",
        color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    )
    fig_pie.update_layout(
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig_pie

def create_leaderboard_chart(leaderboard_data):
    """Create a horizontal bar chart for top performers"""
    if not leaderboard_data:
        return None
    
    # Take top 10 users
    top_users = leaderboard_data[:10]
    usernames = [user[0] for user in top_users]
    scores = [user[1] for user in top_users]
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=usernames,
        orientation='h',
        marker=dict(
            color=scores,
            colorscale='Viridis',
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        text=scores,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="🏆 Top 10 Contributors",
        xaxis_title="Total Score",
        yaxis_title="Username",
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    
    return fig

def create_activity_timeline():
    """Create a mock activity timeline (can be enhanced with real data)"""
    # This is a placeholder - you can enhance this with real user activity data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
    activity_data = pd.DataFrame({
        'Date': dates,
        'Activity': [max(0, int(50 + 30 * (i % 4) + (i % 7) * 10)) for i in range(len(dates))]
    })
    
    fig = px.line(
        activity_data,
        x='Date',
        y='Activity',
        title="📈 Community Activity Over Time",
        line_shape='spline'
    )
    
    fig.update_traces(line_color='#667eea', line_width=3)
    fig.update_layout(
        font=dict(family="Inter, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    return fig

def fetch_github_profile_data(username):
    """Fetch additional GitHub profile data for enhanced display"""
    try:
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code == 200:
            data = response.json()
            return {
                'avatar_url': data.get('avatar_url', ''),
                'name': data.get('name', username),
                'bio': data.get('bio', ''),
                'followers': data.get('followers', 0),
                'following': data.get('following', 0),
                'public_repos': data.get('public_repos', 0),
                'created_at': data.get('created_at', ''),
                'location': data.get('location', 'Unknown')
            }
    except:
        pass
    return None

def create_user_profile_card(username, profile_data, scores_data):
    """Create an enhanced user profile card"""
    if not profile_data:
        return f"""
        <div class="metric-card">
            <h3>👤 {username}</h3>
            <p>Profile data not available</p>
        </div>
        """
    
    total_score = sum([
        scores_data.get('pull_requests_opened', 0),
        scores_data.get('pull_requests_merged', 0),
        scores_data.get('issues_created', 0),
        scores_data.get('issues_closed', 0),
        scores_data.get('repos_contributed_to', 0),
        scores_data.get('starred_repositories', 0),
        scores_data.get('commit_changes', 0)
    ])
    
    return f"""
    <div class="metric-card" style="text-align: center;">
        <img src="{profile_data['avatar_url']}" style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 1rem;" />
        <h2 style="margin: 0.5rem 0; color: #333;">{profile_data['name']}</h2>
        <p style="color: #667eea; font-weight: 600;">@{username}</p>
        <p style="color: #6c757d; margin: 1rem 0;">{profile_data['bio'] or 'No bio available'}</p>
        
        <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
            <div>
                <div style="font-weight: 700; font-size: 1.2rem; color: #667eea;">{total_score:,}</div>
                <div style="font-size: 0.9rem; color: #6c757d;">Total Score</div>
            </div>
            <div>
                <div style="font-weight: 700; font-size: 1.2rem; color: #667eea;">{profile_data['followers']:,}</div>
                <div style="font-size: 0.9rem; color: #6c757d;">Followers</div>
            </div>
            <div>
                <div style="font-weight: 700; font-size: 1.2rem; color: #667eea;">{profile_data['public_repos']:,}</div>
                <div style="font-size: 0.9rem; color: #6c757d;">Repositories</div>
            </div>
        </div>
        
        <p style="font-size: 0.9rem; color: #6c757d;">📍 {profile_data['location']}</p>
    </div>
    """

def create_achievement_badges(scores_data):
    """Create achievement badges based on user scores"""
    badges = []
    
    # Define achievement criteria
    if scores_data.get('pull_requests_merged', 0) >= 50:
        badges.append({"name": "PR Master", "icon": "🔀", "color": "#28a745"})
    
    if scores_data.get('issues_closed', 0) >= 25:
        badges.append({"name": "Bug Hunter", "icon": "🐛", "color": "#dc3545"})
    
    if scores_data.get('commit_changes', 0) >= 1000:
        badges.append({"name": "Code Warrior", "icon": "⚔️", "color": "#6f42c1"})
    
    if scores_data.get('starred_repositories', 0) >= 100:
        badges.append({"name": "Star Gazer", "icon": "⭐", "color": "#ffc107"})
    
    if scores_data.get('repos_contributed_to', 0) >= 20:
        badges.append({"name": "Open Source Hero", "icon": "🚀", "color": "#17a2b8"})
    
    if not badges:
        return ""
    
    badges_html = ""
    for badge in badges:
        badges_html += f"""
        <span style="
            background: {badge['color']};
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 0.2rem;
            display: inline-block;
            font-weight: 600;
        ">
            {badge['icon']} {badge['name']}
        </span>
        """
    
    return f"""
    <div class="metric-card">
        <h3 style="margin-bottom: 1rem; color: #333;">🏅 Achievements</h3>
        {badges_html}
    </div>
    """
