# import streamlit as st
# import requests
# import psycopg2
# from psycopg2.extras import execute_values
# from datetime import datetime

# # Function to validate GitHub account
# def validate_github_account(url):
#     try:
#         # Extract the username from the URL
#         if "github.com/" not in url:
#             return False, "Invalid URL. Ensure it includes 'github.com/'."

#         username = url.split("github.com/")[-1].strip("/")
#         if not username:
#             return False, "Invalid URL. Username missing."

#         # Use GitHub API to check if the user exists
#         api_url = f"https://api.github.com/users/{username}"
#         response = requests.get(api_url)

#         if response.status_code == 200:
#             user_data = response.json()
#             return True, user_data['login'], url
#         elif response.status_code == 404:
#             return False, "GitHub account does not exist."
#         else:
#             return False, f"Error: {response.status_code} - {response.reason}"

#     except Exception as e:
#         return False, f"An error occurred: {str(e)}"

# # Function to insert validated GitHub account into PostgreSQL
# def insert_into_db(username, url):
#     try:
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(
#             dbname="leaderboard",
#             user="postgres",  # Replace with your PostgreSQL username
#             password="sudharsan25",  # Replace with your PostgreSQL password
#             host="localhost",
#             port="5432"
#         )
#         cursor = conn.cursor()

#         # Create table if it doesn't exist
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS github_accounts (
#             id SERIAL PRIMARY KEY,
#             username VARCHAR(255) UNIQUE NOT NULL,
#             url VARCHAR(255) NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
#         cursor.execute(create_table_query)

#         # Insert data into the table
#         insert_query = """
#             INSERT INTO github_accounts (username, url)
#             VALUES (%s, %s)
#             ON CONFLICT (username) DO NOTHING;
#         """
#         cursor.execute(insert_query, (username, url))

#         # Commit and close the connection
#         conn.commit()
#     except psycopg2.Error as e:
#         print(f"Database error: {e}")
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

#     return True, "GitHub account saved to the database successfully."

# # Streamlit App
# st.title("GitHub Account Validator")
# st.write("Enter a GitHub profile URL to validate if it's a valid GitHub account.")

# # Input field for GitHub URL
# github_url = st.text_input("GitHub Profile URL", "")

# # Validate button
# if st.button("Validate"):
#     if github_url:
#         is_valid, result, *details = validate_github_account(github_url)
#         if is_valid:
#             username, url = result, details[0]
#             st.success(f"Valid GitHub account for user: {username}")

#             # Insert into database
#             db_status, db_message = insert_into_db(username, url)
#             if db_status:
#                 st.success(db_message)
#             else:
#                 st.error(db_message)
#         else:
#             st.error(result)
#     else:
#         st.warning("Please enter a GitHub profile URL.")
