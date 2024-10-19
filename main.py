# main.py

import threading
import time
import pandas as pd
import os
import subprocess
from scrape_contacts import scrape_emails
from get_desc import get_description

def get_google_search(software_desc, company_desc, possible_users):
    # Generate a Google search query based on user inputs
    query = f"{software_desc} {company_desc} {possible_users}"
    return query

def generate_email(software_description, company_description):
    # Generate an email content based on descriptions
    email_content = (
        f"Hello,\n\nWe'd like to introduce our {software_description} tailored for "
        f"{company_description}.\nBest regards."
    )
    return email_content

def run_get_list():
    # Run get_list.py as a subprocess
    subprocess.run(['python', 'get_list.py'])

def scrape_emails_thread(google_q):
    # Run scrape_emails in a separate thread
    scrape_emails(google_q, 20, 'en', 'results.csv')

def main():
    # Take inputs from the user
    software_desc = input("Enter Software description: ")
    company_desc = input("Enter Company description: ")
    possible_users = input("Enter Possible users: ")

    # Generate Google search query
    google_q = get_google_search(software_desc, company_desc, possible_users)

    # Start scrape_emails in a separate thread
    scrape_thread = threading.Thread(target=scrape_emails_thread, args=(google_q,))
    scrape_thread.start()

    k = 0
    finished = False

    while not finished:
        # Run get_list.py to update results_filtered.csv
        run_get_list()

        # Check if results_filtered.csv exists
        if os.path.exists('results_filtered.csv'):
            df_filtered = pd.read_csv('results_filtered.csv')

            if k < len(df_filtered):
                # Process the k-th line
                row = df_filtered.iloc[k]
                domain = row['domain']

                # Generate description for this domain
                description = get_description(domain)

                # Add description to the dataframe
                df_filtered.at[k, 'description'] = description

                # Generate email for this line and description
                email_content = generate_email(software_desc, description)
                print(f"Generated email for {domain}:\n{email_content}\n")

                # Save updated dataframe back to CSV
                df_filtered.to_csv('results_filtered.csv', index=False)

                # Increment k
                k += 1
            else:
                # No new lines to process
                if not scrape_thread.is_alive():
                    finished = True
                else:
                    # Wait for new data to be scraped
                    time.sleep(5)
        else:
            # Wait for results_filtered.csv to be created
            time.sleep(5)

    print("Processing completed.")

if __name__ == '__main__':
    main()
