import dimcli
from dimcli.utils import dslquery_json as dslquery
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import pandas as pd
import time
import re
from fuzzywuzzy import fuzz

def extract_first(combined_df):
    skip_count = 0

    first_author_list = []
    first_affiliation_list = []
    
    for index, row in combined_df.iterrows():
        # Extract First Author and Affiliation
        article_title = row['Article Title']
        authors = row['Authors']
        article_url = row['Article URL']
        author_information = row['Author Information']

        first_author_full = authors.strip().split(';')[0]
        first_affiliation_full = author_information.strip().split('\n')[0]
        
        if "Author Information" in first_author_full:
            skip_count += 1
            continue

        if "Asencio, Jessica" in first_author_full:
            continue

        # Get name part before first number in author
        match_author = re.search(r'\d', first_author_full)
        if not match_author:
            print(f"No number found in author: {first_author_full}")
            continue
        first_author = first_author_full[:match_author.start()].strip()
        first_author_num = match_author.group()

        # Get text after first number in affiliation
        match_affil = re.search(r'[a-zA-Z]', first_affiliation_full)
        if not match_affil:
            print(f"No text found in affiliation: {first_affiliation_full}")
            continue
        first_affiliation = first_affiliation_full[match_affil.start():].strip()

        # print(f"Author: {first_author}")
        # print(f"Author Number: {first_author_num}")
        # print(f"Affiliation: {first_affiliation}\n")

        assert first_author_num == first_affiliation_full[0], f"{first_author_num} {first_affiliation_full} do not match"

        first_author_list.append(first_author)
        first_affiliation_list.append(first_affiliation)

    print(f"Skipped {skip_count} rows")

    return first_author_list, first_affiliation_list    

if __name__ == "__main__":

    # iterate through combined_csv
    combined_df = pd.read_csv('combined.csv')

    first_author_list, first_affiliation_list = extract_first(combined_df)

    # Process each author-affiliation pair
    processed_list = []
    for first_author_i, first_affiliation_i in zip(first_author_list, first_affiliation_list):
        if len(first_author_i.strip().split(','))!=2:
            print("SKIPPING", first_author_i)
            continue 

        last_name, first_name = first_author_i.strip().split(',')

        processed_list.append({
            'first_author': first_name + " " + last_name,
            'institution' : first_affiliation_i.strip().split(',')[0],
            'full_affiliation': first_affiliation_i
        })

    # Save processed list to CSV
    pd.DataFrame(processed_list).to_csv('cleaned_combined.csv', index=False)

