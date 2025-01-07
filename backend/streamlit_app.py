# import streamlit as st
# import requests
# import psycopg2
# import os
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()  # So we can read .env DB credentials, if available

# # Function to connect to the database using existing credentials
# def connect_to_db():
#     return psycopg2.connect(
#         dbname=os.getenv("DB_NAME", "leaderboard"),
#         user=os.getenv("DB_USER", "postgres"),
#         password=os.getenv("DB_PASSWORD", "sudharsan25"),
#         host=os.getenv("DB_HOST", "localhost"),
#         port=os.getenv("DB_PORT", "5432")
#     )

# def create_scores_table_if_not_exists(conn):
#     cursor = conn.cursor()
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS scores (
#         id SERIAL PRIMARY KEY,
#         username VARCHAR(255) UNIQUE NOT NULL,
#         pull_requests_opened INT DEFAULT 0,
#         pull_requests_merged INT DEFAULT 0,
#         issues_created INT DEFAULT 0,
#         issues_closed INT DEFAULT 0,
#         repos_contributed_to INT DEFAULT 0,
#         starred_repositories INT DEFAULT 0,
#         commit_changes INT DEFAULT 0,
#         last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     );
#     """
#     cursor.execute(create_table_query)
#     conn.commit()

# # Function to fetch commit changes using GitHub API
# def fetch_commit_changes(username):
#     headers = {"Accept": "application/vnd.github.v3+json"}
#     total_commits = 0

#     try:
#         # Step 1: Get user's repositories
#         repos_url = f"https://api.github.com/users/{username}/repos"
#         repos_response = requests.get(repos_url, headers=headers)
#         repos_response.raise_for_status()
#         repositories = repos_response.json()

#         # Step 2: Loop through each repository and fetch commit count
#         for repo in repositories:
#             owner = repo['owner']['login']
#             repo_name = repo['name']
#             contributors_url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
#             contributors_response = requests.get(contributors_url, headers=headers)
#             contributors_response.raise_for_status()

#             # Find the user's contribution in this repository
#             contributors = contributors_response.json()
#             for contributor in contributors:
#                 if contributor['login'] == username:
#                     total_commits += contributor['contributions']
#                     break

#         return total_commits
#     except Exception as e:
#         st.error(f"Error fetching commit changes: {str(e)}")
#         return 0

# # Function to fetch scores using GitHub API
# def fetch_github_scores(username):
    
#     if username.startswith("https://github.com/"):
#         username = username.split("https://github.com/")[-1].strip("/")
    
#     headers = {"Accept": "application/vnd.github.v3+json"}

#     try:
#         # Pull Requests Opened
#         pr_opened = requests.get(
#             f"https://api.github.com/search/issues?q=type:pr+author:{username}",
#             headers=headers
#         ).json().get("total_count", 0)

#         # Pull Requests Merged
#         pr_merged = requests.get(
#             f"https://api.github.com/search/issues?q=type:pr+author:{username}+is:merged",
#             headers=headers
#         ).json().get("total_count", 0)

#         # Issues Created
#         issues_created = requests.get(
#             f"https://api.github.com/search/issues?q=type:issue+author:{username}",
#             headers=headers
#         ).json().get("total_count", 0)

#         # Issues Closed
#         issues_closed = requests.get(
#             f"https://api.github.com/search/issues?q=type:issue+author:{username}+is:closed",
#             headers=headers
#         ).json().get("total_count", 0)

#         # Repositories Contributed To
#         repos_contributed_to = requests.get(
#             f"https://api.github.com/users/{username}/repos",
#             headers=headers
#         ).json()
#         repos_contributed_to_count = len(repos_contributed_to) if isinstance(repos_contributed_to, list) else 0

#         # Starred Repositories
#         starred_repos = requests.get(
#             f"https://api.github.com/users/{username}/starred",
#             headers=headers
#         ).json()
#         starred_repos_count = len(starred_repos) if isinstance(starred_repos, list) else 0

#         # Commit Changes
#         commit_changes = fetch_commit_changes(username)

#         return {
#             "pull_requests_opened": pr_opened,
#             "pull_requests_merged": pr_merged,
#             "issues_created": issues_created,
#             "issues_closed": issues_closed,
#             "repos_contributed_to": repos_contributed_to_count,
#             "starred_repositories": starred_repos_count,
#             "commit_changes": commit_changes
#         }
#     except Exception as e:
#         st.error(f"Error fetching scores: {str(e)}")
#         return None

# # Function to insert or update scores in the database
# def update_scores_in_db(username, scores):
#     try:
#         conn = connect_to_db()
#         create_scores_table_if_not_exists(conn)  # Ensure the 'scores' table exists
#         cursor = conn.cursor()

#         query = """
#             INSERT INTO scores (
#                 username, pull_requests_opened, pull_requests_merged,
#                 issues_created, issues_closed, repos_contributed_to,
#                 starred_repositories, commit_changes, last_updated
#             )
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (username) DO UPDATE SET
#                 pull_requests_opened = EXCLUDED.pull_requests_opened,
#                 pull_requests_merged = EXCLUDED.pull_requests_merged,
#                 issues_created = EXCLUDED.issues_created,
#                 issues_closed = EXCLUDED.issues_closed,
#                 repos_contributed_to = EXCLUDED.repos_contributed_to,
#                 starred_repositories = EXCLUDED.starred_repositories,
#                 commit_changes = EXCLUDED.commit_changes,
#                 last_updated = EXCLUDED.last_updated;
#         """
#         cursor.execute(query, (
#             username,
#             scores["pull_requests_opened"],
#             scores["pull_requests_merged"],
#             scores["issues_created"],
#             scores["issues_closed"],
#             scores["repos_contributed_to"],
#             scores["starred_repositories"],
#             scores["commit_changes"],
#             datetime.now()
#         ))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return True, "Scores updated successfully in the 'scores' table."
#     except Exception as e:
#         return False, f"Database error: {str(e)}"

# # Streamlit App layout
# st.title("GitHub Leaderboard")
# st.write("Fetch GitHub scores and update them in the leaderboard database.")

# # Input field for GitHub username
# github_username = st.text_input("GitHub Username", "")

# if st.button("Fetch and Update Scores"):
#     if github_username:
#         scores = fetch_github_scores(github_username)
#         if scores:
#             db_status, db_message = update_scores_in_db(github_username, scores)
#             if db_status:
#                 st.success(db_message)
#             else:
#                 st.error(db_message)
#     else:
#         st.warning("Please enter a GitHub username.")
