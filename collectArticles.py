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
    driver.get("https://journals.lww.com/ccmjournal/toc/2020/01001")


    # Wait for and click the "Accept all cookies" button
    try:
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_cookies_button.click()
    except Exception as e:
        print("Error handling cookie dialog:", e)

    # Select 100 results per page
    try:
        print("Finding items-per-page container")
        # First find and scroll to the container
        container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "wp-items-on-page")))
        print("Scrolling to container")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container)
        time.sleep(1)

        print("Finding visible selectize input")
        # Find all selectize inputs and filter for the visible one
        selectize_inputs = driver.find_elements(By.CLASS_NAME, "selectize-input")
        visible_input = None
        for input_el in selectize_inputs:
            if input_el.is_displayed():
                visible_input = input_el
                break
        
        if visible_input:
            print("Found visible selectize input, clicking...")
            visible_input.click()
            time.sleep(1)
        else:
            raise Exception("No visible selectize input found")

        # After clicking, the dropdown should open showing the options
        print("Looking for 100 option in dropdown")
        option_100 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".selectize-dropdown-content .option[data-value='100']")))
        print("Found 100 option, clicking...")
        option_100.click()
        time.sleep(5)

    except Exception as e:
        print(f"Error setting results per page: {e}")
        print(f"Current page source: {driver.page_source}")


    for page_i in range(1, 19):
        time.sleep(5)

        # Wait for the articles to load; adjust the CSS selector to match article containers
        articles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))  # Changed to find <article> tags

        for article in articles:
            try:
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
                # time.sleep(0.5)
                
            except Exception as e:
                print("Error processing article:", e)

        # Go to the next page
        try:
            # First find the next button
            next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.element__nav.element__nav--next[aria-label='Goto Next page']")))
            
            # Scroll the button into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
            time.sleep(0.5)  # Wait for scroll to complete
            
            # Now wait for it to be clickable and click
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.element__nav.element__nav--next[aria-label='Goto Next page']")))
            driver.execute_script("arguments[0].click();", next_button)  # Use JavaScript click instead of Selenium click
            time.sleep(0.5)
        except Exception as e:
            print(f"Error clicking next button: {e}")

    # Close the browser when done
    driver.quit()


    pandas.DataFrame(article_list).to_csv('articles.csv', index=False)

if __name__ == "__main__":
    main()
