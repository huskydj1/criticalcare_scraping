from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd 
from tqdm import tqdm 
import re

def save_progress(results, start_row, end_row, is_temp=True):
    # Save to a temporary file if it's an intermediate save
    suffix = 'temp_' if is_temp else ''
    filename = f'articles_with_authors_{suffix}{start_row}_{end_row}.csv'
    pd.DataFrame(results).to_csv(filename, index=False)
    if not is_temp:
        print(f"Final results saved to {filename}")

def main(start_row=0, end_row=None):
    # Read the articles CSV
    articles_df = pd.read_csv('articles.csv')
    
    # Validate and adjust row ranges
    if end_row is None:
        end_row = len(articles_df)
    start_row = max(0, start_row)  # Ensure start_row is not negative
    end_row = min(len(articles_df), end_row)  # Ensure end_row doesn't exceed dataframe length
    
    print(f"Processing rows {start_row} to {end_row-1}")
    results = []
    
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    skipped_rows = []
    
    # Save progress every N articles
    save_interval = 10

    # Use iloc to slice the dataframe by row numbers
    for index, row in tqdm(articles_df.iloc[start_row:end_row].iterrows(), total=end_row-start_row):
        # Check if title matches expected format using regex
        title = row['Article Title']
        if not re.match(r'^\d+:\s+.+', title):
            print(f"Skipping non-standard title: {title}")
            skipped_rows.append((index, title))
            continue

        try:
            # Navigate to article URL
            driver.get(row['Article URL'])
            
            # Handle cookie acceptance
            if not results:
                try:
                    accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                    accept_cookies_button.click()
                    time.sleep(2)
                except Exception as e:
                    print(f"No cookie dialog for article {index + 1}")
            
            # First get the author text
            author_element = wait.until(EC.presence_of_element_located((By.ID, "ejp-article-authors")))
            author_list = author_element.text
            # print(f"Authors: {author_text}")

            # Find and click the author information button
            found = False
            scroll_attempts = 0
            while not found and scroll_attempts < 10:
                print("Trying to find author information button")
                try:
                    author_info_button = driver.find_element(By.ID, "ejp-article-authors-link")
                    if author_info_button.is_displayed() and author_info_button.is_enabled():
                        author_info_button.click()
                        found = True
                    else:
                        driver.execute_script("window.scrollBy(0, 300);")  # Scroll by 300 pixels
                        time.sleep(0.5)
                        scroll_attempts += 1
                except:
                    driver.execute_script("window.scrollBy(0, 300);")  # Scroll by 300 pixels
                    time.sleep(0.5)
                    scroll_attempts += 1
            
            if not found:
                raise Exception("Could not find clickable author information button")

            print("Clicked on Author Information")
            
            # Try multiple times to get the text as it might need time to populate
            max_attempts = 5
            author_text = ""
            for attempt in range(max_attempts):
                # Wait for and scroll to the author information dropdown
                author_info = wait.until(EC.presence_of_element_located((By.ID, "ejp-article-authors-info")))
                
                print("Scrolled to reveal info")

                # Scroll the info into view and wait for it to settle
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", author_info)
                time.sleep(1)

                print("Trying to reveal author organzations")
                author_text = author_info.text.strip()
                if author_text:
                    break
                print(f"Attempt {attempt + 1}: Text empty, waiting...")
                time.sleep(10)
            
            if not author_text:
                print(f"Warning: Author info text empty for {row['Article Title']}")
            
            print(f"Title: {row['Article Title']}\nAuthor Info: {author_text}\n---")
            
            # Store results
            results.append({
                'Article Title': row['Article Title'],
                'Authors': author_list,
                'Article URL': row['Article URL'],
                'Author Information': author_text
            })
            
            # Save progress periodically
            if len(results) % save_interval == 0:
                save_progress(results, start_row, end_row, is_temp=True)
                print(f"Progress saved after {len(results)} articles")
            
            time.sleep(1)  # Brief pause between articles
            
        except Exception as e:
            print(f"Error processing article {index + 1}: {e}")
            results.append({
                'Article Title': row['Article Title'],
                'Article URL': row['Article URL'],
                'Author Information': f"Error: {str(e)}"
            })
            # Save progress after error
            save_progress(results, start_row, end_row, is_temp=True)
            print("Progress saved after error")
    
    # Save final results
    save_progress(results, start_row, end_row, is_temp=False)

    # Print skipped rows
    if skipped_rows:
        print("Skipped rows:")
        for index, title in skipped_rows:
            print(f"Row {index + 1}: {title}")
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape author affiliations for articles')
    parser.add_argument('--start', type=int, default=0, help='Starting row number (inclusive)')
    parser.add_argument('--end', type=int, default=None, help='Ending row number (exclusive)')
    
    args = parser.parse_args()
    main(start_row=args.start, end_row=args.end)
    
    #1766 -> [0, 441], [441, 882], [882, 1323], [1323, 1766]
    # python collectAffilliations.py --start 0 --end 441
    # python collectAffilliations.py --start 441 --end 882
    # python collectAffilliations.py --start 882 --end 1323
    # python collectAffilliations.py --start 1323 --end 1766