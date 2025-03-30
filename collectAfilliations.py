from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def main():
    # Read the articles CSV
    articles_df = pd.read_csv('articles.csv')
    results = []
    
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    for index, row in articles_df.iterrows():
        try:
            # Navigate to article URL
            driver.get(row['Article URL'])
            
            # Handle cookie acceptance
            try:
                accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                accept_cookies_button.click()
                time.sleep(2)
            except Exception as e:
                print(f"No cookie dialog for article {index + 1}")
            
            # Find and click the author information button
            found = False
            scroll_attempts = 0
            while not found and scroll_attempts < 10:
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
            
            # Wait for the author information dropdown to appear and get its text
            author_info = wait.until(EC.presence_of_element_located((By.ID, "ejp-article-authors-info")))
            author_text = author_info.text
            print(author_text)
            
            # Store results
            results.append({
                'Article Title': row['Article Title'],
                'Article URL': row['Article URL'],
                'Author Information': author_text
            })
            
            print(f"Processed article {index + 1}/{len(articles_df)}")
            time.sleep(2)  # Brief pause between articles
            
        except Exception as e:
            print(f"Error processing article {index + 1}: {e}")
            results.append({
                'Article Title': row['Article Title'],
                'Article URL': row['Article URL'],
                'Author Information': f"Error: {str(e)}"
            })
    
    # Save results to CSV
    pd.DataFrame(results).to_csv('articles_with_authors.csv', index=False)
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()