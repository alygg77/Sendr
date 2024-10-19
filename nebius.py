import os
from openai import OpenAI
import pandas as pd
import json
import csv



client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key="eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNDQ1Mzc2NjE4MTgyMDQwNjYyMyIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg4NzAyNzQ4MiwidXVpZCI6Ijc5NjUxMDdjLWU1YWEtNGE2My1hZGNlLTZiM2UxMDM0YWQ0OSIsIm5hbWUiOiJVbm5hbWVkIGtleSIsImV4cGlyZXNfYXQiOiIyMDI5LTEwLTE4VDE0OjE4OjAyKzAwMDAifQ.Y-84JOUhbJmzeR-nvI5ubCEOn9Cc0CyE9IpbilRn_CI"
)

company ="I am a small startup focused on guitar tuning"
product = "I have an application that listens to guitar sounds and helps user to tune the guitar"
partners = "Music shops could work, maybe online music platforms"
id = "email"

#WRITES STRING TO FILE
def write_message_to_file(message_content, id, i):
    # Create a filename by combining id and i
    filename = f"{id}_{i + 1}.txt"
    # Open the file in write mode and write the message content
    with open(filename, 'w') as file:
        file.write(message_content)

    print(f"Message written to {filename}")

#EXTRACTS DESCRIPTION FROM THE number,email,link,description FORMAT
def extract_description(data_string):
    # Split the input string by commas
    parts = data_string.split(',')
    
    # Check if there are at least 4 parts to extract the description
    if len(parts) < 4:
        return "Invalid format: not enough parts"
    
    # Join all parts after the first three to form the description
    description = ','.join(parts[3:]).strip()  # Strip whitespace from the description
    return description

# Example usage
data_string = "123, example@example.com, http://example.com, This is the description of the item."
description = extract_description(data_string)

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
    print(searchTerm)


#X IS THE LINE NUMBER IN THE CSV FILE indexed 0
def emailGenerator(x, company, product):


    ##GETTING THE LINE FROM CSV TO SPECIFIC_LINE

        # Specify the path to your CSV file and the line number you want to read (0-indexed).
        file_path = 'compdata.csv'
        line_number = x

        # Initialize a string variable to store the line.
        specific_line = ""

        # Open the CSV file and read the specific line.
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            
            # Iterate through the rows and get the specific line.
            for index, row in enumerate(reader):
                if index == line_number:
                    specific_line = ','.join(row)  # Join the row elements with commas if needed.
                    break
        description = extract_description(specific_line)
    ##REQUEST TO NEBIUS
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[
            {
            "role": "system",
            "content": "You are an email generating tool. You will receive data about a company that you will be emailing to. User will inpput details about his software/application, and your job is to compile an email to offer the software/application services to the company in data. Your answer should be formated as follows: Subject: .... /n *Write the email here *. Data is here (ignore the email and link): " + description
            },
            {
            "role": "user",
            "content": "Hello! I own a company " + company + "Our main product is the following:" + product + "Put my name as Daniil Bekirov. In your respons include the subject and email only as it will be sent directly to the people. Don't write *Here is the compiled email:* in the beginning of the response"
            }
        ], temperature= 0.6
        )

    ##LOADING DATA FROM JSON TO STRING VARIABLE

        data = json.loads(completion.to_json())

        # Extract the message content
        message_content = data['choices'][0]['message']['content']


    ## WRITING THE MESSAGE TO A FILE
        write_message_to_file(message_content, id, x)

    



#Running both functions:
searchTerm(company,product,partners)
emailGenerator(4,company,product)