# import requests
# import os
# import psycopg2

# GITHUB_API_URL = "https://api.github.com"
# TOKEN = os.getenv("GITHUB_TOKEN")

# headers = {"Authorization": f"token {TOKEN}"}

# def fetch_github_data(endpoint):
#     response = requests.get(f"{GITHUB_API_URL}/{endpoint}", headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     response.raise_for_status()

# def calculate_scores(github_id):
#     # Define scoring criteria
#     scores = {
#         "commits": 1,
#         "pull_requests": 5,
#         "issues": 3,
#         "stars": 2
#     }

#     # Fetch data
#     commits = fetch_github_data(f"users/{github_id}/events")
#     pull_requests = fetch_github_data(f"search/issues?q=author:{github_id}+type:pr")
#     issues = fetch_github_data(f"search/issues?q=author:{github_id}+type:issue")
#     stars = fetch_github_data(f"users/{github_id}/starred")

#     # Calculate scores
#     total_score = 0
#     total_score += len([event for event in commits if event['type'] == 'PushEvent']) * scores["commits"]
#     total_score += pull_requests['total_count'] * scores["pull_requests"]
#     total_score += issues['total_count'] * scores["issues"]
#     total_score += len(stars) * scores["stars"]

#     return total_score

# def update_github_account_score(github_id):
#     score = calculate_scores(github_id)
#     try:
#         conn = psycopg2.connect(
#             dbname="leaderboard",
#             user="postgres",
#             password="sudharsan25",
#             host="localhost",
#             port="5432"
#         )
#         cursor = conn.cursor()

#         # Update the score in the database
#         update_query = """
#             INSERT INTO github_accounts (username, url, score)
#             VALUES (%s, %s, %s)
#             ON CONFLICT (username) DO UPDATE SET score = EXCLUDED.score;
#         """
#         cursor.execute(update_query, (github_id, f"https://github.com/{github_id}", score))

#         # Commit and close the connection
#         conn.commit()
#     except psycopg2.Error as e:
#         raise Exception(f"Database error: {e}")
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

#     return score

# from datetime import datetime, timedelta
# from fastapi import FastAPI, HTTPException
# from .services import calculate_scores

# app = FastAPI()

# @app.post("/track-user/")
# async def track_user(github_id: str):
#     try:
#         # Calculate scores
#         score = update_github_account_score(github_id)
#     except psycopg2.Error as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {e}")

#     return {"github_id": github_id, "score": score}