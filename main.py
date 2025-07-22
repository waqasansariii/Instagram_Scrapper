from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from dotenv import load_dotenv
import pandas as pd
import os

# === Load .env for Instagram credentials ===
load_dotenv()
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

# === Setup WebDriver ===
service = Service("D:/Freelancing/Gagan/chromedriver-win64/chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# === Instagram Login ===
driver.get("https://www.instagram.com/accounts/login/")
wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
time.sleep(5)

# Dismiss "Save Your Login Info?" and "Turn on Notifications" popups
try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not now')]"))).click()
except:
    print("No first popup")

try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))).click()
except:
    print("No second popup")

# === Visit Target Profile ===
target_username = "mustafafahad26"
driver.get(f"https://www.instagram.com/{target_username}/")
time.sleep(5)

# === Open "Following" List ===
try:
    following_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following')]")))
    following_btn.click()
    time.sleep(7)  # Longer wait to let the popup load fully
except Exception as e:
    print("❌ Failed to open following list:", e)
    driver.quit()
    exit()

# === Scroll Modal to Collect Usernames ===
try:
    scroll_box = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")))
except Exception as e:
    print("❌ Failed to find scroll box:", e)
    driver.quit()
    exit()

usernames = set()
scroll_attempts = 0
max_attempts = 500  # Increased for more usernames

print("\n🔁 Scrolling to collect usernames...\n")

while scroll_attempts < max_attempts:
    links = scroll_box.find_elements(By.TAG_NAME, "a")
    new_usernames = {link.text.strip() for link in links if link.text.strip()}

    prev_count = len(usernames)
    usernames.update(new_usernames)

    if len(usernames) == prev_count:
        scroll_attempts += 1
    else:
        scroll_attempts = 0

    print(f"🌀 Collected: {len(usernames)} usernames | Attempt: {scroll_attempts}")
    driver.execute_script("arguments[0].scrollTop += arguments[0].offsetHeight;", scroll_box)
    time.sleep(random.uniform(2.0, 4.0))  # Random delay

# === Done: Print or Save ===
print(f"\n✅ Found {len(usernames)} following accounts:\n")
for uname in sorted(usernames):
    print(uname)

output_file = "following_list.csv"

# Load existing data if the file exists
if os.path.exists(output_file):
    old_df = pd.read_csv(output_file)
    old_usernames = set(old_df['username'].str.strip())
else:
    old_usernames = set()

# Merge old and new usernames
combined_usernames = old_usernames.union(usernames)

# Save updated unique list
df = pd.DataFrame({'username': sorted(combined_usernames)})
df.to_csv(output_file, index=False)

print(f"\n✅ Total unique followers saved: {len(combined_usernames)}")
print("📁 Saved to", output_file)

# Close the browser
driver.quit()
