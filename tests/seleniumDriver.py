import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

# Setup Chrome options to disable GPU hardware acceleration
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU to avoid GPU state error

# Gmail URL
GMAIL_URL = "https://mail.google.com/"

def login_to_gmail(driver, email, password):
    """Log into Gmail using the provided credentials."""
    driver.get(GMAIL_URL)

    time.sleep(random.uniform(1.5, 3))  # Random sleep time

    # Example: Move mouse to an element before clicking
    actions = ActionChains(driver)
    

    # Wait for email input field to be clickable
    email_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@type="email"]'))
    )
    email_input.send_keys(email)
    actions.move_to_element(email_input).perform()  # Move to email input field before typing
    email_input.send_keys(Keys.ENTER)

    time.sleep(random.uniform(1.5, 3))  # Random sleep time
    
    # Wait for password input field to be clickable
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@type="password"]'))
    )
    password_input.send_keys(password)
    actions.move_to_element(password_input).perform()  # Move to email input field before typing
    password_input.send_keys(Keys.ENTER)

    # Wait for the inbox to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
    )
    print("Logged in successfully.")

def wait_for_email_click(driver):
    """Wait for the user to click on an email and print its content."""
    print("Waiting for you to click on an email...")

    while True:
        # Check if an email is opened
        try:
            email_view = driver.find_element(By.XPATH, "//div[@role='dialog']")
            subject = email_view.find_element(By.XPATH, ".//h2").text
            body = email_view.find_element(By.XPATH, ".//div[@class='a3s aiL ']").text
            
            print("\nEmail Opened:")
            print(f"Subject: {subject}")
            print(f"Body: {body[:500]}...")  # Print the first 500 characters
            print("=" * 50)
            
            input("Press Enter to wait for another email or Ctrl+C to exit...")

        except Exception as e:
            # Ignore errors if the email is not opened
            pass
        
        time.sleep(2)

if __name__ == "__main__":
    email = "your_gmail"
    password = getpass.getpass(prompt="Enter your Gmail password: ")  # Prompt user for password securely

    # Alternate webdriver usage
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    try:
        # Login to Gmail
        login_to_gmail(driver, email, password)

        # Wait for email clicks
        wait_for_email_click(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()