"""
Real-time features and live updates for GitHub Leaderboard
"""
import asyncio
import json
import time
from datetime import datetime
import streamlit as st
import websockets
import threading
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LiveUpdate:
    user: str
    action: str
    score_change: int
    timestamp: datetime
    details: Dict

class RealTimeManager:
    def __init__(self):
        self.update_queue = queue.Queue()
        self.active_connections = set()
        self.live_stats = {
            'active_users': 0,
            'total_updates': 0,
            'last_update': None
        }
    
    def add_live_update(self, update: LiveUpdate):
        """Add a live update to the queue"""
        self.update_queue.put(update)
        self.live_stats['total_updates'] += 1
        self.live_stats['last_update'] = datetime.now()
    
    def get_recent_updates(self, limit=10):
        """Get recent updates from the queue"""
        updates = []
        count = 0
        temp_queue = queue.Queue()
        
        while not self.update_queue.empty() and count < limit:
            update = self.update_queue.get()
            updates.append(update)
            temp_queue.put(update)
            count += 1
        
        # Put items back in queue
        while not temp_queue.empty():
            self.update_queue.put(temp_queue.get())
        
        return updates

class LiveActivityFeed:
    def __init__(self):
        self.recent_activities = []
        self.max_activities = 50
    
    def add_activity(self, username, action, details, score_change=0):
        """Add new activity to the feed"""
        activity = {
            'username': username,
            'action': action,
            'details': details,
            'score_change': score_change,
            'timestamp': datetime.now(),
            'id': f"{username}_{int(time.time())}"
        }
        
        self.recent_activities.insert(0, activity)
        
        # Keep only recent activities
        if len(self.recent_activities) > self.max_activities:
            self.recent_activities = self.recent_activities[:self.max_activities]
    
    def get_activities(self, limit=10):
        """Get recent activities"""
        return self.recent_activities[:limit]
    
    def create_activity_stream_html(self, activities):
        """Create HTML for activity stream"""
        if not activities:
            return """
            <div class="activity-stream">
                <h3>📡 Live Activity Feed</h3>
                <p>No recent activities</p>
            </div>
            """
        
        activities_html = ""
        for activity in activities:
            time_ago = self._time_ago(activity['timestamp'])
            icon = self._get_activity_icon(activity['action'])
            
            activities_html += f"""
            <div class="activity-item" data-activity-id="{activity['id']}">
                <div class="activity-icon">{icon}</div>
                <div class="activity-content">
                    <div class="activity-header">
                        <strong>{activity['username']}</strong> {activity['action']}
                        {f'<span class="score-change">+{activity["score_change"]}</span>' if activity['score_change'] > 0 else ''}
                    </div>
                    <div class="activity-details">{activity['details']}</div>
                    <div class="activity-time">{time_ago}</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="activity-stream">
            <h3>📡 Live Activity Feed</h3>
            <div class="activity-list">
                {activities_html}
            </div>
        </div>
        
        <style>
        .activity-stream {{
            background: var(--card-bg);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .activity-item {{
            display: flex;
            align-items: flex-start;
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            transition: background 0.3s ease;
            animation: fadeInSlide 0.5s ease-out;
        }}
        
        .activity-item:hover {{
            background: rgba(102, 126, 234, 0.05);
        }}
        
        .activity-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
            width: 40px;
            text-align: center;
        }}
        
        .activity-content {{
            flex-grow: 1;
        }}
        
        .activity-header {{
            font-weight: 600;
            margin-bottom: 0.3rem;
            color: var(--text-color);
        }}
        
        .activity-details {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
        }}
        
        .activity-time {{
            color: var(--text-secondary);
            font-size: 0.8rem;
        }}
        
        .score-change {{
            background: linear-gradient(45deg, var(--success-color), #00b894);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        @keyframes fadeInSlide {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        </style>
        """
    
    def _time_ago(self, timestamp):
        """Calculate time ago string"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        elif diff.seconds < 86400:
            return f"{diff.seconds // 3600}h ago"
        else:
            return f"{diff.days}d ago"
    
    def _get_activity_icon(self, action):
        """Get icon for activity type"""
        icons = {
            'joined': '👋',
            'scored': '⭐',
            'pull_request': '🔀',
            'issue': '🐛',
            'commit': '💻',
            'repository': '📁',
            'star': '⭐',
            'achievement': '🏆',
            'milestone': '🎯'
        }
        return icons.get(action, '📈')

class LiveStats:
    def __init__(self):
        self.stats = {
            'online_users': 0,
            'total_score_today': 0,
            'new_registrations': 0,
            'active_contributors': 0,
            'top_gainer': {'username': '', 'score_increase': 0}
        }
    
    def update_stats(self, new_stats):
        """Update live statistics"""
        self.stats.update(new_stats)
    
    def create_live_stats_html(self):
        """Create HTML for live statistics display"""
        return f"""
        <div class="live-stats-container">
            <h3>📊 Live Statistics</h3>
            <div class="stats-grid-live">
                <div class="stat-card-live">
                    <div class="stat-icon">👥</div>
                    <div class="stat-content">
                        <div class="stat-number">{self.stats['online_users']}</div>
                        <div class="stat-label">Online Users</div>
                    </div>
                </div>
                
                <div class="stat-card-live">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-number">{self.stats['total_score_today']:,}</div>
                        <div class="stat-label">Score Today</div>
                    </div>
                </div>
                
                <div class="stat-card-live">
                    <div class="stat-icon">🆕</div>
                    <div class="stat-content">
                        <div class="stat-number">{self.stats['new_registrations']}</div>
                        <div class="stat-label">New Members</div>
                    </div>
                </div>
                
                <div class="stat-card-live">
                    <div class="stat-icon">🚀</div>
                    <div class="stat-content">
                        <div class="stat-number">{self.stats['active_contributors']}</div>
                        <div class="stat-label">Active Today</div>
                    </div>
                </div>
            </div>
            
            {f'''
            <div class="top-gainer">
                <h4>🏆 Today's Top Gainer</h4>
                <div class="gainer-info">
                    <span class="gainer-name">{self.stats['top_gainer']['username']}</span>
                    <span class="gainer-score">+{self.stats['top_gainer']['score_increase']}</span>
                </div>
            </div>
            ''' if self.stats['top_gainer']['username'] else ''}
        </div>
        
        <style>
        .live-stats-container {{
            background: var(--card-bg);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        
        .stats-grid-live {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        
        .stat-card-live {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 10px;
            padding: 1rem;
            display: flex;
            align-items: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card-live:hover {{
            transform: scale(1.05);
        }}
        
        .stat-icon {{
            font-size: 2rem;
            margin-right: 1rem;
        }}
        
        .stat-content {{
            flex-grow: 1;
        }}
        
        .stat-number {{
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            opacity: 0.9;
        }}
        
        .top-gainer {{
            background: rgba(102, 126, 234, 0.1);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
        }}
        
        .gainer-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
        }}
        
        .gainer-name {{
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        .gainer-score {{
            background: var(--success-color);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: 600;
        }}
        </style>
        """

class NotificationSystem:
    def __init__(self):
        self.notifications = []
    
    def add_notification(self, title, message, type="info", duration=5000):
        """Add a new notification"""
        notification = {
            'id': f"notif_{int(time.time())}",
            'title': title,
            'message': message,
            'type': type,
            'duration': duration,
            'timestamp': datetime.now()
        }
        self.notifications.append(notification)
    
    def create_notification_html(self, notification):
        """Create HTML for a notification"""
        icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'achievement': '🏆'
        }
        
        return f"""
        <div class="notification notification-{notification['type']}" 
             data-notification-id="{notification['id']}">
            <div class="notification-icon">{icons.get(notification['type'], 'ℹ️')}</div>
            <div class="notification-content">
                <div class="notification-title">{notification['title']}</div>
                <div class="notification-message">{notification['message']}</div>
            </div>
            <div class="notification-close" onclick="closeNotification('{notification['id']}')">×</div>
        </div>
        
        <style>
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            border-left: 4px solid var(--primary-color);
            z-index: 1000;
            max-width: 350px;
            animation: slideInRight 0.3s ease-out;
            display: flex;
            align-items: flex-start;
        }}
        
        .notification-success {{ border-left-color: var(--success-color); }}
        .notification-error {{ border-left-color: var(--error-color); }}
        .notification-warning {{ border-left-color: var(--warning-color); }}
        .notification-achievement {{ 
            border-left-color: #ffd700;
            background: linear-gradient(135deg, #fff9c4, #ffeaa7);
        }}
        
        .notification-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
        }}
        
        .notification-content {{
            flex-grow: 1;
        }}
        
        .notification-title {{
            font-weight: 600;
            margin-bottom: 0.3rem;
            color: var(--text-color);
        }}
        
        .notification-message {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .notification-close {{
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--text-secondary);
            margin-left: 1rem;
        }}
        
        .notification-close:hover {{
            color: var(--text-color);
        }}
        
        @keyframes slideInRight {{
            from {{ 
                transform: translateX(100%); 
                opacity: 0;
            }}
            to {{ 
                transform: translateX(0); 
                opacity: 1;
            }}
        }}
        </style>
        
        <script>
        function closeNotification(id) {{
            const notification = document.querySelector(`[data-notification-id="${{id}}"]`);
            if (notification) {{
                notification.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }}
        }}
        
        // Auto-close notifications
        setTimeout(() => closeNotification('{notification['id']}'), {notification['duration']});
        </script>
        """

# Global instances
live_activity_feed = LiveActivityFeed()
live_stats = LiveStats()
notification_system = NotificationSystem()
real_time_manager = RealTimeManager()

def simulate_live_activity(username, action, details, score_change=0):
    """Simulate live activity (for demo purposes)"""
    live_activity_feed.add_activity(username, action, details, score_change)
    
    # Update live stats
    if action == 'joined':
        live_stats.stats['new_registrations'] += 1
    elif score_change > 0:
        live_stats.stats['total_score_today'] += score_change
        live_stats.stats['active_contributors'] += 1
        
        # Check if this is the top gainer
        if score_change > live_stats.stats['top_gainer']['score_increase']:
            live_stats.stats['top_gainer'] = {
                'username': username,
                'score_increase': score_change
            }
    
    # Add notification for significant events
    if score_change > 50:
        notification_system.add_notification(
            "🎉 Great Progress!",
            f"{username} gained {score_change} points!",
            "achievement"
        )
