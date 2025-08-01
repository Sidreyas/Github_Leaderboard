"""
Advanced Analytics and AI-Powered Insights for GitHub Leaderboard
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class GitHubAnalytics:
    def __init__(self):
        self.colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    def create_advanced_user_dashboard(self, username, scores_data, historical_data=None):
        """Create comprehensive user analytics dashboard"""
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Contribution Distribution', 'Performance Radar', 
                          'Growth Trend', 'Activity Heatmap'),
            specs=[[{"type": "pie"}, {"type": "scatterpolar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. Contribution Distribution (Pie Chart)
        contributions = [
            scores_data.get('pull_requests_opened', 0) + scores_data.get('pull_requests_merged', 0),
            scores_data.get('issues_created', 0) + scores_data.get('issues_closed', 0),
            scores_data.get('commit_changes', 0),
            scores_data.get('repos_contributed_to', 0),
            scores_data.get('starred_repositories', 0)
        ]
        
        labels = ['Pull Requests', 'Issues', 'Commits', 'Repositories', 'Stars']
        
        fig.add_trace(
            go.Pie(values=contributions, labels=labels, hole=0.3,
                   marker=dict(colors=self.colors)),
            row=1, col=1
        )
        
        # 2. Performance Radar Chart
        categories = ['PRs', 'Issues', 'Commits', 'Repos', 'Stars', 'Activity']
        max_values = [100, 50, 2000, 50, 200, 100]  # Scaling factors
        user_values = [
            min(contributions[0], max_values[0]),
            min(contributions[1], max_values[1]),
            min(contributions[2]/20, max_values[2]/20),  # Scale down commits
            min(contributions[3], max_values[3]),
            min(contributions[4]/2, max_values[4]/2),   # Scale down stars
            min(sum(contributions)/100, max_values[5])   # Overall activity
        ]
        
        fig.add_trace(
            go.Scatterpolar(
                r=user_values,
                theta=categories,
                fill='toself',
                name=username,
                line=dict(color='#667eea')
            ),
            row=1, col=2
        )
        
        # 3. Growth Trend (Mock data - can be replaced with real historical data)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        growth_data = np.cumsum(np.random.normal(10, 5, len(dates)))
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=growth_data,
                mode='lines+markers',
                name='Score Growth',
                line=dict(color='#764ba2', width=3)
            ),
            row=2, col=1
        )
        
        # 4. Activity Heatmap (Days of week vs Hour)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        activity_intensity = np.random.randint(0, 10, 7)
        
        fig.add_trace(
            go.Bar(
                x=days,
                y=activity_intensity,
                marker=dict(color='#f093fb'),
                name='Weekly Activity'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=700,
            showlegend=False,
            title_text=f"📊 {username}'s Advanced Analytics Dashboard",
            title_x=0.5,
            font=dict(family="Inter, sans-serif")
        )
        
        return fig
    
    def create_community_insights(self, leaderboard_data):
        """Create community-wide insights and analytics"""
        if not leaderboard_data:
            return None
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(leaderboard_data, columns=['username', 'score', 'github_url'])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Score Distribution', 'Top Contributors Network', 
                          'Growth Velocity', 'Community Segments'),
            specs=[[{"type": "histogram"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # 1. Score Distribution Histogram
        fig.add_trace(
            go.Histogram(
                x=df['score'],
                nbinsx=20,
                marker=dict(color='#667eea', opacity=0.7),
                name='Score Distribution'
            ),
            row=1, col=1
        )
        
        # 2. Top Contributors Network (Bubble Chart)
        top_10 = df.head(10)
        fig.add_trace(
            go.Scatter(
                x=range(len(top_10)),
                y=top_10['score'],
                mode='markers',
                marker=dict(
                    size=top_10['score']/100,
                    color=self.colors[0],
                    line=dict(width=2, color='white')
                ),
                text=top_10['username'],
                textposition="top center",
                name='Top Contributors'
            ),
            row=1, col=2
        )
        
        # 3. Growth Velocity (Mock calculation)
        velocity_data = np.random.normal(15, 5, len(top_10))
        fig.add_trace(
            go.Bar(
                x=top_10['username'],
                y=velocity_data,
                marker=dict(color='#f5576c'),
                name='Weekly Growth Rate'
            ),
            row=2, col=1
        )
        
        # 4. Community Segments (Performance Tiers)
        high_performers = len(df[df['score'] > df['score'].quantile(0.8)])
        mid_performers = len(df[(df['score'] > df['score'].quantile(0.4)) & 
                               (df['score'] <= df['score'].quantile(0.8))])
        new_contributors = len(df[df['score'] <= df['score'].quantile(0.4)])
        
        fig.add_trace(
            go.Pie(
                values=[high_performers, mid_performers, new_contributors],
                labels=['High Performers', 'Regular Contributors', 'New Contributors'],
                hole=0.3,
                marker=dict(colors=['#4facfe', '#f093fb', '#f5576c'])
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=700,
            showlegend=False,
            title_text="🌍 Community Analytics & Insights",
            title_x=0.5,
            font=dict(family="Inter, sans-serif")
        )
        
        return fig
    
    def perform_user_clustering(self, all_users_data):
        """Perform ML clustering to segment users"""
        if len(all_users_data) < 3:
            return None
        
        # Prepare features for clustering
        features = []
        usernames = []
        
        for user_data in all_users_data:
            features.append([
                user_data.get('pull_requests_opened', 0),
                user_data.get('pull_requests_merged', 0),
                user_data.get('issues_created', 0),
                user_data.get('issues_closed', 0),
                user_data.get('repos_contributed_to', 0),
                user_data.get('starred_repositories', 0),
                user_data.get('commit_changes', 0)
            ])
            usernames.append(user_data.get('username', 'Unknown'))
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform clustering
        n_clusters = min(4, len(all_users_data))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Create visualization
        fig = go.Figure()
        
        cluster_names = ['🚀 Elite Contributors', '💪 Active Developers', 
                        '🌱 Growing Contributors', '👶 New Members']
        
        for i in range(n_clusters):
            cluster_users = [usernames[j] for j in range(len(usernames)) if clusters[j] == i]
            cluster_scores = [sum(features[j]) for j in range(len(features)) if clusters[j] == i]
            
            fig.add_trace(go.Scatter(
                x=range(len(cluster_users)),
                y=cluster_scores,
                mode='markers',
                marker=dict(
                    size=15,
                    color=self.colors[i % len(self.colors)],
                    line=dict(width=2, color='white')
                ),
                text=cluster_users,
                name=cluster_names[i % len(cluster_names)],
                hovertemplate='%{text}<br>Score: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title="🤖 AI-Powered User Segmentation",
            xaxis_title="User Index",
            yaxis_title="Total Score",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        
        return fig, clusters, cluster_names
    
    def generate_insights_report(self, username, scores_data, rank=None):
        """Generate AI-powered insights and recommendations"""
        total_score = sum([
            scores_data.get('pull_requests_opened', 0),
            scores_data.get('pull_requests_merged', 0),
            scores_data.get('issues_created', 0),
            scores_data.get('issues_closed', 0),
            scores_data.get('repos_contributed_to', 0),
            scores_data.get('starred_repositories', 0),
            scores_data.get('commit_changes', 0)
        ])
        
        insights = []
        recommendations = []
        
        # Analyze contribution patterns
        pr_ratio = scores_data.get('pull_requests_merged', 0) / max(scores_data.get('pull_requests_opened', 1), 1)
        issue_ratio = scores_data.get('issues_closed', 0) / max(scores_data.get('issues_created', 1), 1)
        
        if pr_ratio > 0.8:
            insights.append("🎯 Excellent PR success rate! Your contributions are highly valued.")
        elif pr_ratio < 0.3:
            recommendations.append("💡 Focus on improving PR quality to increase merge rate.")
        
        if issue_ratio > 1:
            insights.append("🛠️ Great problem solver! You close more issues than you create.")
        
        if scores_data.get('commit_changes', 0) > 1000:
            insights.append("💻 Highly active coder with significant commit contributions!")
        
        if scores_data.get('repos_contributed_to', 0) > 20:
            insights.append("🌟 Open source champion! Contributing to many projects.")
        elif scores_data.get('repos_contributed_to', 0) < 5:
            recommendations.append("🚀 Consider contributing to more diverse projects to expand your impact.")
        
        # Rank-based insights
        if rank:
            if rank <= 3:
                insights.append(f"🏆 You're in the top 3! Rank #{rank} - Amazing performance!")
            elif rank <= 10:
                insights.append(f"⭐ Top 10 performer! Rank #{rank} - Keep up the great work!")
            elif rank <= 50:
                insights.append(f"📈 Solid contributor! Rank #{rank} - You're making good progress!")
        
        return {
            'total_score': total_score,
            'insights': insights,
            'recommendations': recommendations,
            'performance_level': self._get_performance_level(total_score),
            'next_milestone': self._get_next_milestone(total_score)
        }
    
    def _get_performance_level(self, score):
        """Determine performance level based on score"""
        if score >= 1000:
            return "🚀 Elite Contributor"
        elif score >= 500:
            return "💪 Senior Developer"
        elif score >= 200:
            return "🌟 Active Contributor"
        elif score >= 50:
            return "🌱 Growing Developer"
        else:
            return "👶 New Contributor"
    
    def _get_next_milestone(self, score):
        """Get next milestone target"""
        milestones = [50, 200, 500, 1000, 2000, 5000]
        for milestone in milestones:
            if score < milestone:
                return f"{milestone} points ({milestone - score} to go!)"
        return "🎯 You've reached the highest milestone!"
    
    def create_comparison_chart(self, user1_data, user2_data, user1_name, user2_name):
        """Create comparison chart between two users"""
        categories = ['PRs Opened', 'PRs Merged', 'Issues Created', 'Issues Closed', 
                     'Repositories', 'Stars', 'Commits']
        
        user1_values = [
            user1_data.get('pull_requests_opened', 0),
            user1_data.get('pull_requests_merged', 0),
            user1_data.get('issues_created', 0),
            user1_data.get('issues_closed', 0),
            user1_data.get('repos_contributed_to', 0),
            user1_data.get('starred_repositories', 0),
            min(user1_data.get('commit_changes', 0), 1000)  # Cap for visualization
        ]
        
        user2_values = [
            user2_data.get('pull_requests_opened', 0),
            user2_data.get('pull_requests_merged', 0),
            user2_data.get('issues_created', 0),
            user2_data.get('issues_closed', 0),
            user2_data.get('repos_contributed_to', 0),
            user2_data.get('starred_repositories', 0),
            min(user2_data.get('commit_changes', 0), 1000)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=user1_values,
            theta=categories,
            fill='toself',
            name=user1_name,
            line=dict(color='#667eea')
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=user2_values,
            theta=categories,
            fill='toself',
            name=user2_name,
            line=dict(color='#f5576c')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(user1_values), max(user2_values)) * 1.1]
                )),
            showlegend=True,
            title=f"⚡ {user1_name} vs {user2_name} Comparison",
            font=dict(family="Inter, sans-serif")
        )
        
        return fig
