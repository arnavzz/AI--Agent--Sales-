import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')


LINKEDIN_SESSION_COOKIE = "AQEDAT1gcx8DNZl4AAABlK3b3_IAAAGU0ehj8k4AitIjWLZ8Hpt2v6WRPx4J9yQamVrAWWtMlQ3PrS0Mk215XSnnNW6PiS7EyohIYR72HQ8gSUkooVxQZiilPTawwT7QODJ4avDGeadUGGUGe2L89fVh"

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")

service = Service("C:\\Users\\LENOVO\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")  
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.linkedin.com/")
driver.add_cookie({"name": "li_at", "value": LINKEDIN_SESSION_COOKIE})
driver.refresh()
time.sleep(3)

# Search for a job title
search_query = "Machine Learning Engineer"
driver.get(f"https://www.linkedin.com/search/results/people/?keywords={search_query}")
time.sleep(5)

# Wait for profiles to load
try:
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "WjGsMcGljQaqRBgKiPuVFwqVyJhewVYTIumc")))  # Updated class
except Exception as e:
    with open("debug_page_source.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)
    print(f"Error: {e}")
    print("Page source saved to debug_page_source.html for further inspection.")
    driver.quit()
    exit()

# Scroll to load more results
for _ in range(5):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(3)

# Extract page source after scrolling
soup = BeautifulSoup(driver.page_source, "html.parser")
profiles = soup.find_all("li", class_="WjGsMcGljQaqRBgKiPuVFwqVyJhewVYTIumc")  # Updated selector for profile containers

print(f"Found {len(profiles)} profiles")

# Extract data
data = []
for profile in profiles:
    name_tag = profile.find("span", class_="fzjkwwSlzBgmvJcGSaTLyJUZRWGWlxpftXJmUQ")  # Updated class for name
    job_title_tag = profile.find("div", class_="HplMppXllPuLiFcyKFtLraZumseoiayxWIes") # Updated class for job title
    company_tag = profile.find("p", class_="LDORiBkbJCmvBpuWZnlNSBDJqHZlxbAwRlmVY") # Updated class for company
    location_tag = profile.find("div", class_="MkzEBsduGocwPwTMdsCNbHApLkxsXnigTpbghQ")  # Updated class for location

    name = name_tag.get_text(strip=True) if name_tag else "N/A"
    company = company_tag.get_text(strip=True) if company_tag else "N/A"
    job_title = job_title_tag.get_text(strip=True) if job_title_tag else "N/A"
    location = location_tag.get_text(strip=True) if location_tag else "N/A"

    print(f"Name: {name}, Job Title: {job_title}, Location: {location}")

    data.append([name, job_title, location])

# Save data to CSV
df = pd.DataFrame(data, columns=["Name", "Job Title", "Location"])
df.to_csv("linkedin_leads.csv", index=False)

print("✅ Scraping complete. Data saved in linkedin_leads.csv")

# Close browser
driver.quit()
