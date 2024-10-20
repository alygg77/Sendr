# main.py

import threading
import time
import pandas as pd
import os
import subprocess
from scrape_contacts import scrape_emails
from get_desc import get_description
from get_list import process_csv
from openai import OpenAI
import json
import streamlit as st




client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key="eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNDQ1Mzc2NjE4MTgyMDQwNjYyMyIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg4NzAyNzQ4MiwidXVpZCI6Ijc5NjUxMDdjLWU1YWEtNGE2My1hZGNlLTZiM2UxMDM0YWQ0OSIsIm5hbWUiOiJVbm5hbWVkIGtleSIsImV4cGlyZXNfYXQiOiIyMDI5LTEwLTE4VDE0OjE4OjAyKzAwMDAifQ.Y-84JOUhbJmzeR-nvI5ubCEOn9Cc0CyE9IpbilRn_CI"
)


id = "email"



class frontEnd:

    # Set page layout to wide mode
    st.set_page_config(layout="wide")

    # Create a container for the layout
    with st.container():
        # Create a layout with two columns (first column smaller)
        col1, col2 = st.columns([1, 2])  # 1:2 ratio

        # Column for the form
        with col1:
            st.header("Connection Finder Form")
            # Create a form
            with st.form('mailAI'):
                # Input fields for company, product, and partners
                company = st.text_input('Information about your company:', 'I am a small startup focused on guitar tuning')
                product = st.text_input('Information about your product:', 'I have an application that listens to guitar sounds and helps users to tune the guitar')
                partners = st.text_input('What partners are you looking to find?:', 'Music shops could work, maybe online music platforms')

                # Submit button
                submit = st.form_submit_button('Find your connections')

        # Column for the progress display
        with col2:
            st.header("Progress Log")

            # Add CSS styling for scrollable text area
            st.markdown(
                """
                <style>
                    .scrollable {
                        max-height: 400px;  /* Set a maximum height */
                        overflow-y: auto;   /* Enable vertical scrolling */
                        padding: 10px;      /* Add some padding */
                        border: 1px solid #d0d0d0; /* Optional border */
                        border-radius: 5px; /* Optional rounded corners */
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

            progress_text = st.empty()  # Placeholder for progress messages

                # Logic after form submission


            if submit:
                st.success("Form submitted!")
                # Simulating email generation
                time.sleep(1)  # Simulate processing time for email generation

            else:
                progress_text.markdown('<div class="scrollable">Fill out the form to find connections.</div>', unsafe_allow_html=True)





#WRITES STRING TO FILE
def write_message_to_file(message_content, id, i):
    # Create a filename by combining id and i
    filename = f"{id}_{i + 1}.txt"
    # Open the file in write mode and write the message content
    with open(filename, 'w') as file:
        file.write(message_content)
    print(f"Message written to {filename}")


def get_google_search(software_desc, company_desc, possible_users):
    # Generate a Google search query based on user inputs
    return searchTerm(software_desc, company_desc, possible_users)


def generate_email(software_description, company_description,company_desc,k):
    # Generate an email content based on descriptions
    email_content = (
        f"Hello,\n\nWe'd like to introduce our {software_description} tailored for "
        f"{company_description}.\nBest regards."
    )
    ##REQUEST TO NEBIUS
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
        {
        "role": "system",
        "content": "You are an email generating tool. You will receive data about a company that you will be emailing to. User will inpput details about his software/application, and your job is to compile an email to offer the software/application services to the company in data. Your answer should be formated as follows: Subject: .... /n *Write the email here *. Data is here (ignore the email and link): " + company_description
        },
        {
        "role": "user",
        "content": "Hello! I own a company,"+ company_desc + " and our main product is the following:" + software_description + "Put my name as Daniil Bekirov. In your respons include the subject and email only as it will be sent directly to the people. Don't write *Here is the compiled email:* in the beginning of the response"
        }
    ], temperature= 0.6
    )

    ##LOADING DATA FROM JSON TO STRING VARIABLE

        
    data = json.loads(completion.to_json())

    # Extract the message content
    message_content = data['choices'][0]['message']['content']


    ## WRITING THE MESSAGE TO A FILE
    write_message_to_file(message_content, id, k)
    frontEnd.progress_text.markdown(f'<div class="scrollable"><br>{message_content}</div>', unsafe_allow_html=True)
    
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



def searchTerm(company, product, partners):

    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        messages=[
        {
        "role": "system",
        "content": "You are a search term generator. User has a company -" + company + " with the following product description" + product + " And he wants to find clients like " + partners
        },
        {
        "role": "user",
        "content": "Generate one combined search term for me. Don't categorize them. Simply print the search prompt - nothing else"
        }
    ], temperature= 0.6
    )

    data = json.loads(completion.to_json())
    searchTerm = data['choices'][0]['message']['content']
    return searchTerm




def main():

    while not frontEnd.submit:
        time.sleep(1)

    # Take inputs from the user
    software_desc = frontEnd.product
    company_desc = frontEnd.company
    possible_users = frontEnd.partners

    # Remove results_filtered.csv if it exists
    if os.path.exists('results_filtered.csv'):
        os.remove('results_filtered.csv')


    
   

    k = 0  
    # Generate Google search query
    google_q = get_google_search(software_desc, company_desc, possible_users)
    print("we are here: google_q")

    # Start scrape_emails in a separate thread
    scrape_thread = threading.Thread(target=scrape_emails_thread, args=(google_q,))
    scrape_thread.daemon = True  # Daemon thread will exit when the main thread exits
    scrape_thread.start()
    print("we are here: 2")
    time.sleep(10)  # Allow some time for the scraping to begin


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
                email_content = generate_email(software_desc, description,company_desc,k)
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
