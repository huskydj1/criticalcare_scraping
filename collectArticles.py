from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas

def main():
    article_list = []

    # Initialize the WebDriver (ensure chromedriver is installed and in PATH)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    # Navigate to the table-of-contents page
    driver.get("https://journals.lww.com/ccmjournal/toc/2020/01000#-1145392460")
    
    # Wait for and click the "Accept all cookies" button
    try:
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_cookies_button.click()
    except Exception as e:
        print("Error handling cookie dialog:", e)

    time.sleep(5)
    
    # TODO: Find all articles
    
    # Wait for the articles to load; adjust the CSS selector to match article containers
    articles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))  # Changed to find <article> tags
    
    for article in articles:
        try:
            # Print the HTML content of the article element
            # print("\n=== Article HTML Content ===")
            # print(article.get_attribute('outerHTML'))
            # print("===========================\n")
            
            # Find h4 element within the nested structure
            h4_element = article.find_element(By.CSS_SELECTOR, "h4")
            link_element = h4_element.find_element(By.TAG_NAME, "a")
            print("Article Title:", link_element.text)
            print("Article URL:", link_element.get_attribute('href'))

            article_list.append({
                'Article Title' : link_element.text,
                'Article URL' :  link_element.get_attribute('href')
            })
            
            # Pause briefly to ensure the modal is closed and the page is ready
            time.sleep(1)
            
        except Exception as e:
            print("Error processing article:", e)
    
    # Close the browser when done
    driver.quit()


    pandas.DataFrame(article_list).to_csv('articles.csv', index=False)

if __name__ == "__main__":
    main()
