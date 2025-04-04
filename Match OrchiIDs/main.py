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


def check_org_match(target_org, researcher_orgs, threshold=70):
    """Check if target organization matches any of the researcher's organizations"""
    if not researcher_orgs:
        return False, None
    
    best_match = None
    best_score = 0
    
    for org in researcher_orgs:
        print(f"CALCULATING SCORE BETWEEN {target_org} and {org['name']}")
        score = fuzz.token_sort_ratio(target_org.lower(), org['name'].lower())
        print(f"RECEIVED SCORE: {score}")
        if score > best_score:
            best_score = score
            best_match = org
    
    return best_score >= threshold, (best_match, best_score)

def search_researcher(first_name, last_name, target_org):
    # Construct the query to search for researchers by first and last name
    query = f"""
    search researchers 
    where first_name = "{first_name}" 
    and last_name = "{last_name}"
    return researchers[id + first_name + last_name + current_research_org + orcid_id + research_orgs]
    """
    
    try:
        print(f"\nSearching for: {first_name} {last_name}")
        results = dsl.query(query)
        
        if len(results.researchers) > 0:
            for researcher in results.researchers:
                print(f"\nFound: {researcher['first_name']} {researcher['last_name']}")
                
                # Check organization matches
                if 'research_orgs' in researcher:
                    has_match, match_details = check_org_match(target_org, researcher['research_orgs'])
                    print("BEST_MATCH", match_details)
                
                if 'current_research_org' in researcher:
                    print(f"Current org: {researcher['current_research_org']}")
                if 'orcid_id' in researcher:
                    print(f"ORCID: {researcher['orcid_id']}")
                print("---")
        else:
            print("No results found")
            
        time.sleep(1)  # Rate limiting
        return results.researchers if len(results.researchers) > 0 else None
        
    except Exception as e:
        print(f"Error searching for {first_name} {last_name}: {str(e)}")
        return None

if __name__ == "__main__":
    # Load environment variables from .env
    load_dotenv()

    api_key = os.getenv("DIMENSIONS_API_KEY")
    endpoint="https://app.dimensions.ai"

    if api_key is None:
        raise ValueError("API key not found. Make sure to set DIMENSIONS_API_KEY in your .env file.")

    dimcli.login(key=api_key, endpoint=endpoint)
    dsl = dimcli.Dsl()

    # iterate through combined_csv
    combined_df = pd.read_csv('combined.csv')

    first_author_list, first_affiliation_list = extract_first(combined_df)


    # Process each author-affiliation pair
    for first_author_i, first_affiliation_i in zip(first_author_list, first_affiliation_list):
        print(f"\nProcessing: {first_author_i}")
        print(f"Affiliation: {first_affiliation_i}")
        
        # Split name into parts (assuming format is "Last, First")
        name_parts = first_author_i.split(", ")
        if len(name_parts) == 2:
            last_name, first_name = name_parts
            researchers = search_researcher(first_name.strip(), last_name.strip(), first_affiliation_i)

            if researchers:
                print("\nMatches found!")
                break

            else:
                print("\nNo matches found")
        else:
            print(f"Unexpected name format: {first_author_i}")

