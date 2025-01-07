# import streamlit as st
# import requests
# import psycopg2
# import os
# from datetime import datetime
# from dotenv import load_dotenv
# from werkzeug.security import generate_password_hash, check_password_hash

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

# def create_accounts_table_if_not_exists(conn):
#     cursor = conn.cursor()
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS github_accounts (
#         id SERIAL PRIMARY KEY,
#         username VARCHAR(255) UNIQUE NOT NULL,
#         password_hash TEXT NOT NULL,
#         github_url TEXT NOT NULL
#     );
#     """
#     cursor.execute(create_table_query)
#     conn.commit()

# # Function to sign up a new user
# def sign_up(username, password, github_url):
#     try:
#         conn = connect_to_db()
#         create_accounts_table_if_not_exists(conn)  # Ensure the 'github_accounts' table exists
#         cursor = conn.cursor()

#         # Check if username already exists
#         cursor.execute("SELECT * FROM github_accounts WHERE username = %s", (username,))
#         if cursor.fetchone():
#             return False, "Username already exists. Please choose a different username."

#         # Insert new user into the table
#         password_hash = generate_password_hash(password)
#         query = "INSERT INTO github_accounts (username, password_hash, github_url) VALUES (%s, %s, %s);"
#         cursor.execute(query, (username, password_hash, github_url))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return True, "User signed up successfully!"
#     except Exception as e:
#         return False, f"Database error: {str(e)}"

# # Streamlit App layout
# st.title("GitHub Leaderboard - Sign Up")

# # Sign-Up Form
# st.subheader("Sign Up")
# username = st.text_input("Username")
# password = st.text_input("Password", type="password")
# github_url = st.text_input("GitHub Profile URL")

# if st.button("Sign Up"):
#     if username and password and github_url:
#         if github_url.startswith("https://github.com/"):
#             success, message = sign_up(username, password, github_url)
#             if success:
#                 st.success(message)
#             else:
#                 st.error(message)
#         else:
#             st.error("Invalid GitHub URL. Please ensure it starts with 'https://github.com/'.")
#     else:
#         st.warning("Please fill in all fields.")
