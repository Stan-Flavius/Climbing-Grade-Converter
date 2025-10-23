import time
import pandas as pd
import re
import os
import undetected_chromedriver as uc
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

url = "https://www.thecrag.com/en/climbing/romania/routes?sortby=popularity,desc"


def perform_login(driver, username, password):
    print("Attempting to log in...")
    try:
        wait = WebDriverWait(driver, 45)

        print("Waiting for login page elements...")
        try:
            username_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#loginInputLogin")))
        except TimeoutException:
            print("Login failed: Timeout waiting for the login form to load.")
            return False

        password_input = driver.find_element(By.CSS_SELECTOR, "input#loginInputPassword")
        login_button = driver.find_element(By.CSS_SELECTOR, "button#btnLogin")

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button.click()

        try:
            error_message_selector = "div.alert.alert-danger"
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector)))
            print("Login failed. The website reported an 'Invalid login or password'.")
            return False
        except TimeoutException:
            pass

        print("Login button clicked. Waiting for successful redirection...")
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "input#loginInputLogin")))

        print("Login successful.")
        time.sleep(random.uniform(2.0, 4.0))
        return True

    except Exception as e:
        print(f"Login failed. An unexpected error occurred: {e}")
        return False


def scrape_thecrag_routes(start_url, username, password):
    print("Starting the scraper with undetected_chromedriver...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=138)

    scraped_data = []
    next_page_to_scrape = start_url
    page_num = 1

    try:
        while next_page_to_scrape:
            print(f"--- Navigating to page {page_num} ---")
            current_page_url = next_page_to_scrape
            driver.get(next_page_to_scrape)

            is_login_page = False
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input#loginInputLogin"))
                )
                is_login_page = True
            except TimeoutException:
                pass

            if is_login_page:
                print("Detected redirection to login page.")
                if not perform_login(driver, username, password):
                    print("Login failed. Aborting scrape.")
                    break

                print(f"Re-navigating to the page where we left off: {current_page_url}")
                driver.get(current_page_url)

            print(f"Now on page {page_num}. Scraping routes...")

            try:
                wait = WebDriverWait(driver, 15)
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.routetable tbody tr.actionable")))
            except TimeoutException:
                print(f"Timeout on page {page_num}. Route table not found.")
                break

            route_rows = driver.find_elements(By.CSS_SELECTOR, "table.routetable tbody tr.actionable")
            if not route_rows:
                print(f"No routes found on page {page_num}. Ending scrape.")
                break

            for row in route_rows:
                try:
                    route_name_element = row.find_element(By.CSS_SELECTOR, "td.rt_name a")
                    route_name = route_name_element.text.strip()
                    try:
                        grade = row.find_element(By.CSS_SELECTOR,
                                                 "span.pull-right[class*='gb']").text.strip()
                    except NoSuchElementException:
                        grade = "N/A"

                    ascents = "0"
                    try:
                        ascents_element = row.find_element(By.CSS_SELECTOR, "a.iblock.pop")
                        ascents_title = ascents_element.get_attribute("title")
                        match = re.search(r'(\d+)\s+ascent', ascents_title)
                        if match:
                            ascents = match.group(1)
                    except NoSuchElementException:
                        pass

                    scraped_data.append({
                        "Route Name": route_name,
                        "Grade": grade,
                        "Ascents": ascents
                    })
                except Exception as e:
                    print(f"Skipping a row on page {page_num} due to an error: {e}")
                    continue

            print(f"Finished scraping page {page_num}. Total routes so far: {len(scraped_data)}")

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next:not(.disabled) a")
                next_page_to_scrape = next_button.get_attribute('href')
                page_num += 1
                time.sleep(random.uniform(3.0, 5.0))
            except NoSuchElementException:
                print("No active 'next' button found. This is the last page.")
                next_page_to_scrape = None

        if not scraped_data:
            print("No data was scraped.")
            return

        df = pd.DataFrame(scraped_data)
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "crag_routes.csv")
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n Success! Scraped {len(df)} routes. Data saved to {output_file}")

    except Exception as e:
        print(f"An unexpected error occurred during the scrape: {e}")
    finally:
        print("Closing the browser.")
        driver.quit()


if __name__ == "__main__":
    my_username = "Fiullly"
    my_password = "flaviuS54321!"

    scrape_thecrag_routes(url, my_username, my_password)