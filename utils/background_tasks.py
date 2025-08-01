"""
Background tasks and real-time updates
"""
import threading
import time
import schedule
from datetime import datetime
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

def update_all_user_scores():
    """Background task to update all user scores periodically"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM github_accounts;")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"[{datetime.now()}] Starting background score update for {len(users)} users...")
        
        # Update scores for each user
        from app_modern import fetch_github_scores, update_scores_in_db
        
        for user in users:
            username = user[0]
            try:
                scores = fetch_github_scores(username)
                if scores:
                    success, message = update_scores_in_db(username, scores)
                    print(f"Updated scores for {username}: {success}")
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Error updating {username}: {e}")
        
        print(f"[{datetime.now()}] Background score update completed.")
        
    except Exception as e:
        print(f"Error in background task: {e}")

def start_background_scheduler():
    """Start the background scheduler"""
    # Schedule updates every 6 hours
    schedule.every(6).hours.do(update_all_user_scores)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Background scheduler started - scores will update every 6 hours")

def get_user_activity_summary(username):
    """Get summary of user activity for notifications"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                pull_requests_opened + pull_requests_merged as pr_total,
                issues_created + issues_closed as issue_total,
                commit_changes,
                last_updated
            FROM scores 
            WHERE username = %s
        """, (username,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                "pr_total": result[0] or 0,
                "issue_total": result[1] or 0,
                "commit_changes": result[2] or 0,
                "last_updated": result[3]
            }
    except Exception as e:
        print(f"Error getting activity summary: {e}")
    
    return None

# If running this file directly, start the scheduler
if __name__ == "__main__":
    start_background_scheduler()
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Background scheduler stopped.")
