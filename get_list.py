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
    df = pd.read_csv(file_path)
    df_filtered = df.drop_duplicates(subset=['email'], keep='first')
    df_filtered['domain'] = df_filtered['link'].apply(extract_domain)

    # Add a temporary index column to maintain order
    df_filtered['order'] = df_filtered.index

    # Filter out rows where the domain contains numbers
    df_filtered = df_filtered[df_filtered['domain'].apply(is_valid_domain)]

    # Remove duplicates based on the 'domain' column, keeping the first occurrence
    df_filtered = df_filtered.drop_duplicates(subset=['domain'], keep='first')

    filtered_file_path = 'results_filtered.csv'

    if os.path.exists(filtered_file_path):
        # If 'results_filtered.csv' exists, read it
        df_existing = pd.read_csv(filtered_file_path)

        # Merge the new data with the existing data, conserving the 'description' column
        df_combined = pd.merge(
            df_existing,
            df_filtered[['email', 'link', 'domain', 'order']],
            on='domain',
            how='outer',
            suffixes=('_existing', '_new')
        )

        # Keep the existing 'description' column
        df_combined['description'] = df_combined['description'].fillna('')

        # Fill missing data from the new file
        df_combined['email'] = df_combined['email_new'].combine_first(df_combined['email_existing'])
        df_combined['link'] = df_combined['link_new'].combine_first(df_combined['link_existing'])

        # Drop the unnecessary duplicate columns
        df_combined = df_combined.drop(columns=['email_existing', 'link_existing', 'email_new', 'link_new'])

        # Sort by the original order from df_filtered (using the 'order' column)
        df_combined = df_combined.sort_values(by='order').drop(columns=['order'])

        # Save the combined DataFrame to 'results_filtered.csv'
        df_combined.to_csv(filtered_file_path, index=False)

        # Print the remaining valid domains
        for email, domain in zip(df_combined['email'], df_combined['domain']):
            print(f"Valid domain extracted from {email}: {domain}")

        print(f"Filtered CSV updated and saved as {filtered_file_path}")
    else:
        # Sort by the original order before saving
        df_filtered = df_filtered.sort_values(by='order').drop(columns=['order'])

        # Save the filtered DataFrame to 'results_filtered.csv'
        df_filtered.to_csv(filtered_file_path, index=False)

        # Print the remaining valid domains
        for email, domain in zip(df_filtered['email'], df_filtered['domain']):
            print(f"Valid domain extracted from {email}: {domain}")

        print(f"Filtered CSV saved as {filtered_file_path}")
