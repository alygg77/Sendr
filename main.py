# main.py

import threading
import time
import pandas as pd
import os
import subprocess
from scrape_contacts import scrape_emails
from get_desc import get_description
from get_list import process_csv


def get_google_search(software_desc, company_desc, possible_users):
    # Generate a Google search query based on user inputs
    query = f"{software_desc} {company_desc} {possible_users}"
    return str(query)


def generate_email(software_description, company_description):
    # Generate an email content based on descriptions
    email_content = (
        f"Hello,\n\nWe'd like to introduce our {software_description} tailored for "
        f"{company_description}.\nBest regards."
    )
    return email_content


def print_colored_email(domain, email_content):
    # ANSI escape codes for colors
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    reset = "\033[0m"

    # Print the colored output
    print(f"{green}Generated email for {domain}:{reset}")
    print(f"{yellow}{email_content}{reset}\n")


def run_get_list():
    # Run get_list.py as a subprocess
    subprocess.run(['python', 'get_list.py'])


def scrape_emails_with_retries(google_q, max_retries=3, wait_time=5):
    # Retry mechanism for scrape_emails
    retries = 0
    while retries < max_retries:
        try:
            # Try to scrape emails
            scrape_emails(google_q, 20, 'en', 'results.csv')
            break  # Break the loop if successful
        except Exception as e:
            # Handle exception and retry
            print(f"Error occurred in scraping: {e}. Retrying {retries + 1}/{max_retries}...")
            retries += 1
            time.sleep(wait_time)
    if retries == max_retries:
        print("Max retries reached. Exiting scrape process.")
        raise RuntimeError("Failed to scrape emails after multiple attempts.")


def scrape_emails_thread(google_q):
    # Run scrape_emails with retries in a separate thread
    scrape_emails_with_retries(google_q)


def main():
    # Take inputs from the user
    software_desc = input("Enter Software description: ")
    company_desc = input("Enter Company description: ")
    possible_users = input("Enter Possible users: ")

    # Remove results_filtered.csv if it exists
    if os.path.exists('results_filtered.csv'):
        os.remove('results_filtered.csv')

    # Generate Google search query
    google_q = get_google_search(software_desc, company_desc, possible_users)
    print("we are here: google_q")

    # Start scrape_emails in a separate thread
    scrape_thread = threading.Thread(target=scrape_emails_thread, args=(google_q,))
    scrape_thread.daemon = True  # Daemon thread will exit when the main thread exits
    scrape_thread.start()
    print("we are here: 2")
    time.sleep(10)  # Allow some time for the scraping to begin

    k = 0
    finished = False

    while not finished:
        print("we are here: 3, number: ", k)
        process_csv('results.csv') # Run the get_list.py script
        time.sleep(2)  # Small delay before checking again

        # Check if results_filtered.csv exists
        if os.path.exists('results_filtered.csv'):
            df_filtered = pd.read_csv('results_filtered.csv')

            if k < len(df_filtered):
                # Process the k-th line
                row = df_filtered.iloc[k]
                domain = row['domain']

                # Generate description for this domain
                try:
                    description = get_description(domain)
                except Exception as e:
                    print(f"Error occurred while fetching description for {domain}: {e}")
                    description = "Description not available"

                # Add description to the dataframe
                df_filtered.at[k, 'description'] = description

                # Generate email for this line and description
                email_content = generate_email(software_desc, description)
                print_colored_email(domain, email_content)

                # Save updated dataframe back to CSV
                df_filtered.to_csv('results_filtered.csv', index=False)

                # Increment k
                k += 1
            else:
                # No new lines to process, check if scraping is finished
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
