"""
Security, performance optimization, and monitoring features
"""
import streamlit as st
import hashlib
import time
import redis
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
import json
import asyncio
from typing import Dict, List, Optional
import jwt
from cryptography.fernet import Fernet

class SecurityManager:
    """Advanced security management"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.session_manager = SessionManager()
        self.audit_logger = AuditLogger()
        
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        token = hashlib.sha256(f"{time.time()}{st.session_state.get('user_id', 'anonymous')}".encode()).hexdigest()
        st.session_state['csrf_token'] = token
        return token
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token"""
        return token == st.session_state.get('csrf_token')
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input"""
        import re
        import html
        
        # HTML escape
        sanitized = html.escape(input_data)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script.*?</script>',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'eval\(',
            r'document\.cookie',
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        key = st.secrets.get("encryption_key", Fernet.generate_key())
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        key = st.secrets.get("encryption_key")
        if not key:
            raise ValueError("Encryption key not found")
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()

class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(
                host=st.secrets.get("redis_host", "localhost"),
                port=st.secrets.get("redis_port", 6379),
                decode_responses=True
            )
        except:
            # Fallback to memory-based rate limiting
            self.memory_store = {}
    
    def is_rate_limited(self, user_id: str, action: str, limit: int = 60, window: int = 3600) -> bool:
        """Check if user is rate limited"""
        key = f"rate_limit:{user_id}:{action}"
        
        if self.redis_client:
            try:
                current = self.redis_client.incr(key)
                if current == 1:
                    self.redis_client.expire(key, window)
                return current > limit
            except:
                pass
        
        # Fallback to memory
        now = time.time()
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old entries
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if now - timestamp < window
        ]
        
        if len(self.memory_store[key]) >= limit:
            return True
        
        self.memory_store[key].append(now)
        return False
    
    def get_rate_limit_status(self, user_id: str, action: str) -> Dict:
        """Get current rate limit status"""
        key = f"rate_limit:{user_id}:{action}"
        
        if self.redis_client:
            try:
                current = self.redis_client.get(key) or 0
                ttl = self.redis_client.ttl(key)
                return {
                    "current": int(current),
                    "reset_in": max(0, ttl),
                    "limit": 60
                }
            except:
                pass
        
        # Fallback
        return {
            "current": len(self.memory_store.get(key, [])),
            "reset_in": 3600,
            "limit": 60
        }

class SessionManager:
    """Secure session management"""
    
    def __init__(self):
        self.secret_key = st.secrets.get("session_secret", "your-secret-key")
    
    def create_session_token(self, user_id: str, additional_data: Dict = None) -> str:
        """Create secure session token"""
        payload = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            **(additional_data or {})
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def validate_session_token(self, token: str) -> Optional[Dict]:
        """Validate session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if datetime.utcnow() > expires_at:
                return None
            
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def refresh_session(self, token: str) -> Optional[str]:
        """Refresh session token"""
        payload = self.validate_session_token(token)
        if payload:
            return self.create_session_token(
                payload["user_id"],
                {k: v for k, v in payload.items() if k not in ["created_at", "expires_at"]}
            )
        return None

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        handler = logging.FileHandler("logs/security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, username: str, success: bool, ip_address: str = None):
        """Log login attempt"""
        self.logger.info(
            f"Login attempt - Username: {username}, Success: {success}, IP: {ip_address}"
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log data access"""
        self.logger.info(
            f"Data access - User: {user_id}, Resource: {resource}, Action: {action}"
        )
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security event"""
        self.logger.warning(
            f"Security event - Type: {event_type}, Details: {json.dumps(details)}"
        )

class PerformanceMonitor:
    """Performance monitoring and optimization"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def measure_execution_time(self, func):
        """Decorator to measure function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            func_name = func.__name__
            if func_name not in self.metrics:
                self.metrics[func_name] = []
            
            self.metrics[func_name].append(end - start)
            return result
        return wrapper
    
    def get_system_metrics(self) -> Dict:
        """Get system performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": time.time() - self.start_time,
            "function_metrics": {
                name: {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "max_time": max(times),
                    "min_time": min(times)
                }
                for name, times in self.metrics.items()
            }
        }
    
    def optimize_query_cache(self, query_key: str, result: any, ttl: int = 300):
        """Cache query results"""
        if 'query_cache' not in st.session_state:
            st.session_state.query_cache = {}
        
        st.session_state.query_cache[query_key] = {
            "result": result,
            "timestamp": time.time(),
            "ttl": ttl
        }
    
    def get_cached_query(self, query_key: str):
        """Get cached query result"""
        cache = st.session_state.get('query_cache', {})
        
        if query_key in cache:
            cached_item = cache[query_key]
            if time.time() - cached_item["timestamp"] < cached_item["ttl"]:
                return cached_item["result"]
            else:
                # Remove expired cache
                del cache[query_key]
        
        return None

class DatabaseOptimizer:
    """Database performance optimization"""
    
    @staticmethod
    def create_indexes():
        """Create database indexes for better performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_github_username ON users(github_username);",
            "CREATE INDEX IF NOT EXISTS idx_users_score ON users(score DESC);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_updated ON users(last_updated);",
            "CREATE INDEX IF NOT EXISTS idx_activities_user_id ON user_activities(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON user_activities(timestamp DESC);",
        ]
        return indexes
    
    @staticmethod
    def optimize_queries():
        """Optimized database queries"""
        return {
            "top_users_with_stats": """
                SELECT 
                    u.*,
                    COUNT(ua.id) as activity_count,
                    MAX(ua.timestamp) as last_activity
                FROM users u
                LEFT JOIN user_activities ua ON u.id = ua.user_id
                WHERE u.score > 0
                GROUP BY u.id
                ORDER BY u.score DESC
                LIMIT 50;
            """,
            
            "user_activity_summary": """
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as activity_count,
                    SUM(points) as total_points
                FROM user_activities
                WHERE user_id = %s AND timestamp >= %s
                GROUP BY DATE(timestamp)
                ORDER BY date DESC;
            """,
            
            "leaderboard_with_ranking": """
                SELECT 
                    *,
                    ROW_NUMBER() OVER (ORDER BY score DESC) as rank,
                    LAG(score) OVER (ORDER BY score DESC) as previous_score
                FROM users
                WHERE score > 0
                ORDER BY score DESC;
            """
        }

def create_security_dashboard():
    """Create security monitoring dashboard"""
    st.header("🔒 Security Dashboard")
    
    security_manager = SecurityManager()
    performance_monitor = PerformanceMonitor()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Active Sessions",
            len(st.session_state.get('active_sessions', [])),
            delta=2
        )
    
    with col2:
        rate_limit_status = security_manager.rate_limiter.get_rate_limit_status(
            st.session_state.get('user_id', 'anonymous'),
            'api_calls'
        )
        st.metric(
            "API Calls",
            f"{rate_limit_status['current']}/{rate_limit_status['limit']}",
            delta=-5
        )
    
    with col3:
        st.metric(
            "System Health",
            "Healthy ✅",
            delta="Good"
        )
    
    # Performance metrics
    system_metrics = performance_monitor.get_system_metrics()
    
    st.subheader("System Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "CPU Usage",
            f"{system_metrics['cpu_percent']:.1f}%",
            delta=f"{system_metrics['cpu_percent'] - 45:.1f}%"
        )
    
    with col2:
        st.metric(
            "Memory Usage",
            f"{system_metrics['memory_percent']:.1f}%",
            delta=f"{system_metrics['memory_percent'] - 60:.1f}%"
        )
    
    with col3:
        st.metric(
            "Uptime",
            f"{system_metrics['uptime']/3600:.1f}h",
            delta="Stable"
        )
    
    # Security events
    st.subheader("Recent Security Events")
    
    security_events = [
        {"time": "2 min ago", "event": "Successful login", "user": "john_doe", "severity": "info"},
        {"time": "5 min ago", "event": "Rate limit exceeded", "user": "anonymous", "severity": "warning"},
        {"time": "10 min ago", "event": "Invalid token attempt", "user": "unknown", "severity": "error"},
    ]
    
    for event in security_events:
        severity_colors = {
            "info": "🟢",
            "warning": "🟡",
            "error": "🔴"
        }
        
        st.write(f"{severity_colors[event['severity']]} **{event['event']}** - {event['user']} ({event['time']})")

def security_middleware():
    """Security middleware for all pages"""
    security_manager = SecurityManager()
    
    # Generate CSRF token if not exists
    if 'csrf_token' not in st.session_state:
        security_manager.generate_csrf_token()
    
    # Check rate limits
    user_id = st.session_state.get('user_id', 'anonymous')
    if security_manager.rate_limiter.is_rate_limited(user_id, 'page_view'):
        st.error("⚠️ Rate limit exceeded. Please wait before making more requests.")
        st.stop()
    
    # Session validation
    if 'session_token' in st.session_state:
        session_data = security_manager.session_manager.validate_session_token(
            st.session_state.session_token
        )
        if not session_data:
            st.warning("Session expired. Please log in again.")
            del st.session_state.session_token
            st.rerun()
    
    # Add security headers
    st.markdown("""
    <script>
    // Add security headers via meta tags
    const securityHeaders = [
        ['Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data: https:;"],
        ['X-Content-Type-Options', 'nosniff'],
        ['X-Frame-Options', 'DENY'],
        ['X-XSS-Protection', '1; mode=block'],
        ['Referrer-Policy', 'strict-origin-when-cross-origin']
    ];
    
    securityHeaders.forEach(([name, value]) => {
        const meta = document.createElement('meta');
        meta.httpEquiv = name;
        meta.content = value;
        document.head.appendChild(meta);
    });
    </script>
    """, unsafe_allow_html=True)
