import logging
import pandas as pd
import re
from googlesearch import search

# Disable Scrapy logging
logging.getLogger('scrapy').propagate = False


# Function to perform Google search
def get_urls(tag, n, language):
    urls = [url for url in search(tag, stop=n, lang=language)][:n]
    return urls


# Helper function to filter out domains that contain numbers
def is_valid_domain(domain):
    return not re.search(r'\d', domain)


# Parse the CSV file, filter duplicates, and remove invalid emails
def process_csv(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Remove duplicates based on 'email', keeping the first occurrence
    df_filtered = df.drop_duplicates(subset=['email'], keep='first')

    # Extract the domain part from 'email' and add it as a new column in the DataFrame
    df_filtered['domain'] = df_filtered['email'].apply(
        lambda email: re.search(r'@([A-Za-z0-9.-]+)', email).group(1) if re.search(r'@([A-Za-z0-9.-]+)', email) else '')

    # Filter out rows where the domain contains numbers (like animejs@3.0)
    df_filtered = df_filtered[df_filtered['domain'].apply(is_valid_domain)]

    # Remove duplicates based on the 'domain' column, keeping the first occurrence
    df_filtered = df_filtered.drop_duplicates(subset=['domain'], keep='first')

    # Save the filtered DataFrame to 'results_filtered.csv'
    filtered_file_path = 'results_filtered.csv'
    df_filtered.to_csv(filtered_file_path, index=False)

    # Print the remaining valid domains
    for email, domain in zip(df_filtered['email'], df_filtered['domain']):
        print(f"Valid domain extracted from {email}: {domain}")

    print(f"Filtered CSV saved as {filtered_file_path}")
    return filtered_file_path


if __name__ == "__main__":
    # Test function for Google search (example usage)
    print(get_urls('who is dotsquares.com', 5, 'en'))

    # Example CSV file path
    csv_file = 'results.csv'

    # Process the CSV file and filter duplicates
    process_csv(csv_file)
