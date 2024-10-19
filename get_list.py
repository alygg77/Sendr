import logging
import pandas as pd
import re
import os

# Disable Scrapy logging
logging.getLogger('scrapy').propagate = False

# Helper function to filter out domains that contain numbers
def is_valid_domain(domain):
    return not re.search(r'\d', domain)

# Helper function to extract domain from the 'link' column
def extract_domain(link):
    match = re.search(r'https://([^/]+)', link)
    return match.group(1) if match else ''

# Parse the CSV file, filter duplicates, and remove invalid domains
def process_csv(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Remove duplicates based on 'email', keeping the first occurrence
    df_filtered = df.drop_duplicates(subset=['email'], keep='first')

    # Extract the domain part from 'link' and add it as a new column in the DataFrame
    df_filtered['domain'] = df_filtered['link'].apply(extract_domain)

    # Filter out rows where the domain contains numbers
    df_filtered = df_filtered[df_filtered['domain'].apply(is_valid_domain)]

    # Remove duplicates based on the 'domain' column, keeping the first occurrence
    df_filtered = df_filtered.drop_duplicates(subset=['domain'], keep='first')

    filtered_file_path = 'results_filtered.csv'

    if os.path.exists(filtered_file_path):
        # If 'results_filtered.csv' exists, read it
        df_existing = pd.read_csv(filtered_file_path)

        # Concatenate df_filtered and df_existing, but only update 'email', 'link', and 'domain'
        df_existing.update(df_filtered[['email', 'link', 'domain']])

        # Save the combined DataFrame to 'results_filtered.csv'
        df_existing.to_csv(filtered_file_path, index=False)

        # Print the remaining valid domains
        for email, domain in zip(df_existing['email'], df_existing['domain']):
            print(f"Valid domain extracted from {email}: {domain}")

        print(f"Filtered CSV updated and saved as {filtered_file_path}")
    else:
        # Save the filtered DataFrame to 'results_filtered.csv'
        df_filtered.to_csv(filtered_file_path, index=False)

        # Print the remaining valid domains
        for email, domain in zip(df_filtered['email'], df_filtered['domain']):
            print(f"Valid domain extracted from {email}: {domain}")

        print(f"Filtered CSV saved as {filtered_file_path}")

if __name__ == "__main__":
    # Example CSV file path
    csv_file = 'results.csv'

    # Process the CSV file and filter duplicates
    process_csv(csv_file)
