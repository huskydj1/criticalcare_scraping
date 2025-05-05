import pandas as pd
import requests
import time

# Read the combined dataframe
input_path = '../FindPublications/FN_combined_df.csv'
df = pd.read_csv(input_path)

import os
from dotenv import load_dotenv
import dimcli
from tqdm import tqdm

# Initialize Dimensions API
load_dotenv()
api_key = os.getenv("DIMENSIONS_API_KEY")
endpoint = "https://app.dimensions.ai"
if api_key is None:
    raise ValueError("API key not found. Make sure to set DIMENSIONS_API_KEY in your .env file.")
dimcli.login(key=api_key, endpoint=endpoint)
dsl = dimcli.Dsl()

def get_orcid_works(orcid_id, years=[2017, 2023]):
    """
    For a given ORCID, fetch publications where year is 2017 or 2023 from Dimensions API.
    Returns a list of publication dicts.
    """
    results = []
    year_filter = " or ".join(f"year = {y}" for y in years)
    query = f'''
    search publications
    where researchers.orcid_id = "{orcid_id.strip()}" and ({year_filter})
    return publications [basics + extras]
    '''
    try:
        res = dsl.query(query)
        if 'errors' in res.data:
            print(f"Query error for ORCID {orcid_id}: {res.data['errors']}")
        elif 'publications' in res.data and len(res.data['publications']) > 0:
            for pub in res.data['publications']:
                pub['orcid_id'] = orcid_id
                results.append(pub)
        else:
            print(f"No publications found for ORCID: {orcid_id}")
    except Exception as e:
        print(f"Exception for ORCID {orcid_id}: {e}")
    return results

def get_publication_url(pub: dict) -> str | None:
    """
    Return a single resolvable link for a publication dictionary that may include
    'doi', 'id' (Dimensions), 'pmcid', or 'pmid'. Returns None if nothing usable.
    """
    # helper to clean a DOI (strip prefixes, whitespace)
    def _clean_doi(raw: str) -> str:
        raw = raw.strip()
        prefixes = ("doi:", "DOI:", "https://doi.org/", "http://doi.org/")
        for p in prefixes:
            if raw.startswith(p):
                return raw[len(p):]
        return raw

    # order of preference — change if you like
    if (doi := pub.get("doi")):
        return f"https://doi.org/{_clean_doi(doi)}"

    if (dims_id := pub.get("id")):
        # Dimensions public landing pages use the pattern below
        return f"https://app.dimensions.ai/details/publication/pub.{dims_id}"

    if (pmcid := pub.get("pmcid")):
        pmcid = pmcid.upper().removeprefix("PMC")
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"

    if (pmid := pub.get("pmid")):
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    # nothing recognized
    return None


def extract_links_from_works(works):
    """
    Extracts external article links for the given years from ORCID works.
    Returns a dict: {year: [links]}
    """
    
    count_2017 = 0
    count_2023 = 0

    out_list = []
    for group in works:
        # print("GROUPI", group.keys(), group.get('doi'), group.get('id'), group.get('pmcid'), group.get('pmid'), group.get('research_orgs'),  group.get('orcid_id'))

        url_i = get_publication_url(group)
        assert url_i is not None

        assert group.get('year') in [2017, 2023]
        if group.get('year') == 2017:
            count_2017 += 1
            out_list.append({
                'year': 2017,
                'url': url_i
            })
        else:
            count_2023 += 1
            out_list.append({
                'year': 2023,
                'url': url_i
            })

    return count_2017, count_2023, out_list

def main():
    out_rows = []
    wrong_rows = []

    grouped = df.groupby('orcid_id')
    for orcid_id, group in tqdm(grouped):

        author_name = group.iloc[0]['name']
        print(author_name)
        print(f'Processing {author_name} ({orcid_id})')

        works = get_orcid_works(orcid_id)

        count_2017, count_2023, links = extract_links_from_works(works)

        for link_i in links:
            link_i['orcid_id'] = orcid_id
            link_i['author'] = author_name 

        if count_2017 == len(group[group['year'] == 2017]) and count_2023 == len(group[group['year'] == 2023]):
            out_rows.extend(links)
        else:
            wrong_rows.extend(links)

    out_df = pd.DataFrame(out_rows)
    out_df.to_csv('author_publication_links.csv', index=False)
    
    wrong_df = pd.DataFrame(wrong_rows)
    wrong_df.to_csv('author_publication_links_wrong.csv', index=False)
    
    print('Saved to author_publication_links.csv')

if __name__ == '__main__':
    main()