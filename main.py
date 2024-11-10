import os
import sqlite3
from nbformat.v2.rwbase import rejoin_lines
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime
from web_scraper import web_scraper
import concurrent.futures

def create_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        software_description TEXT NOT NULL,
        company_description TEXT NOT NULL,
        request TEXT NOT NULL,
        target_clients TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    user_info_folder = "users"
    if not os.path.exists("db/" + user_info_folder):
        os.makedirs("db/" + user_info_folder)
        print(f"Folder '{user_info_folder}' created for user info.")


def insert_user(software_description, company_description, request, target_clients):
    db_file = "db/users.sql"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Insert the new user
    cursor.execute('''
    INSERT INTO users (software_description, company_description, request, target_clients) 
    VALUES (?, ?, ?, ?)
    ''', (software_description, company_description, request, target_clients))

    # Get the ID of the newly inserted user
    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Create a folder for the user
    user_folder = f'db/users/user_{user_id}'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        print(f"Folder '{user_folder}' created for user ID {user_id}.")

    return user_id


def get_user_by_id(user_id):
    db_file = "db/users.sql"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch user details by id
    cursor.execute('''
    SELECT * FROM users WHERE id = ?
    ''', (user_id,))

    user = cursor.fetchone()  # Fetch the first (and only) result
    conn.close()

    return user


def generate_google_initial_request(user_id):
    load_dotenv()
    db_file = "db/users.sql"
    api_key = os.getenv("NEBIUS_API_KEY")
    client = OpenAI(
        base_url="https://api.studio.nebius.ai/v1/",
        api_key=api_key
    )
    id, software_description, company_description, request, target_clients = get_user_by_id(user_id)
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
            {
                "role": "system",
                "content": "You are a search term generator. User has a company -" + company_description + " with the following product description" + software_description + " He wants to find clients for his product" + "His target clients are " + target_clients
            },
            {
                "role": "user",
                "content": "Generate one combined search term for me. Don't categorize them. Simply print the search prompt - nothing else"
            }
        ], temperature=0.7
    )

    data = json.loads(completion.to_json())
    searchTerm = data['choices'][0]['message']['content']
    return searchTerm


def web_scraper_wrapper(file_path, user_id, timestamp, number):
    with open(file_path, 'r') as file:
        google_search = file.read()
    web_scraper(google_search, 20, "en", f'db/users/user_{user_id}/request_{timestamp}/{number}.csv')


def new_request(user_id):
    db_file = "db/users.sql"
    user = get_user_by_id(user_id)
    if not user:
        print(f"No user found with ID {user_id}")
        return

    id, software_description, company_description, request, target_clients = user


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the request folder
    request_folder = f'db/users/user_{user_id}/request_{timestamp}'
    if not os.path.exists(request_folder):
        os.makedirs(request_folder)
        print(f"Folder '{request_folder}' created for the new request.")
    log_file_path = os.path.join(request_folder, 'log.txt')
    with open(log_file_path, 'w') as log_file:
        log_file.write(f"Request Log for User {user_id}\n")
        log_file.write(f"Timestamp: {timestamp}\n")
        log_file.write(f"Software Description: {software_description}\n")
        log_file.write(f"Company Description: {company_description}\n")
        log_file.write(f"Request: {request}\n")
        log_file.write(f"Target Clients: {target_clients}\n")
        log_file.write("Initiated google search\n")
    for i in range(1, 4):
        request_folder = f'db/users/user_{user_id}/request_{timestamp}'
        log_file_path = os.path.join(request_folder, f'google_search_{i}.txt')
        with open(log_file_path, 'w') as log_file:
            if i == 3:
                searchTerm = ("custom")
            else:
                searchTerm = generate_google_initial_request(user_id)
            log_file.write(searchTerm)


    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(1, 4):
            file_path = os.path.join(f'db/users/user_{user_id}/request_{timestamp}', f'google_search_{i}.txt')
            futures.append(executor.submit(web_scraper_wrapper, file_path, user_id, timestamp, i))

        # Optionally, wait for all threads to complete (this is implicit in 'with' block)
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # Retrieve result, if any
            except Exception as exc:
                print(f'An error occurred: {exc}')



def main():
    db_file = "db/users.sql"
    user_id = 1
    def check_if_user_exists(db_file):
        if not os.path.exists(db_file):
            # Create the database if it doesn't exist
            print("Database not found. Creating users.sql...")
            create_db(db_file)
            print("Database created successfully.")

            # Ask for user details
            software_description = input("Enter your software description: ")
            company_description = input("Enter your company description: ")
            request = input("Enter your request for e-mails: ")
            target_clients = input("Enter your supposed target clients: ")

            # Insert the user details into the database
            insert_user(software_description, company_description, request, target_clients)
            print("Successfully inserted user.")
        else:
            print(f"The database {db_file} already exists.")
    check_if_user_exists(db_file)
    new_request(1)





if __name__ == '__main__':
    main()

