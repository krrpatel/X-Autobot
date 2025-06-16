import os, json, time, random
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import google.generativeai as genai

# === CONFIG ===
COOKIES_FILE = "x_cookies.json"
COMMUNITY_NAME = "Crypto Bhavesh Kaito Community"
POST_INTERVAL = 10800  # Every 1 hour

# === OpenAI API Setup ===
genai.configure(api_key="AIzaSyAMuMRYCDdZtKTKYXCo5vabC8XIGb1YTRo")  # or use os.getenv("GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-2.0-flash")

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def get_credentials_and_folder():
    config = load_config()
    use_saved = 'n'
    if config.get("USERNAME") and config.get("PASSWORD") and config.get("IMAGE_FOLDER"):
        use_saved = input("🔐 Use saved credentials and image folder from config.json? (y/n): ").lower()

    if use_saved == 'y':
        return config["USERNAME"], config["PASSWORD"], config["IMAGE_FOLDER"]

    username = input("👤 Enter Twitter Username: ")
    password = input("🔑 Enter Twitter Password: ")
    folder = input("🖼️ Enter folder path containing 3 images: ")

    save_config({"USERNAME": username, "PASSWORD": password, "IMAGE_FOLDER": folder})
    return username, password, folder

# === Load Credentials & Folder ===
USERNAME, PASSWORD, IMAGE_FOLDER = get_credentials_and_folder()

def get_random_image(folder_path):
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not images:
        raise FileNotFoundError("❌ No image files found in the folder.")
    random_image = random.choice(images)
    abs_path = os.path.abspath(os.path.join(folder_path, random_image))
    return abs_path
    
# === Browser Setup ===
def get_driver():
    options = Options()
    options.add_argument("--headless")  # headless mode
    options.add_argument("--no-sandbox")  # needed for root/VPS
    options.add_argument("--disable-dev-shm-usage")  # fixes /dev/shm issues
    options.add_argument("--disable-gpu")  # safe for headless
    options.add_argument("--remote-debugging-port=9222")  # prevents DevToolsActivePort issue

    return webdriver.Chrome(options=options)

def save_cookies(driver):
    with open(COOKIES_FILE, "w") as f:
        json.dump(driver.get_cookies(), f)

def load_cookies(driver):
    try:
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                if "expiry" in cookie:
                    del cookie["expiry"]
                driver.add_cookie(cookie)
        return True
    except:
        return False

def check_session(driver):
    driver.get("https://x.com/home")
    time.sleep(5)
    return "/login" not in driver.current_url

def login_and_save(driver, wait):
    driver.get("https://x.com/login")
    wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(USERNAME)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    time.sleep(2)
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//span[text()='Log in']").click()

    try:
        otp_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        otp_code = input("📨 Enter OTP: ")
        otp_field.send_keys(otp_code)
        driver.save_screenshot("screenshot.png")
        driver.find_element(By.XPATH, "//span[text()='Next']").click()
    except TimeoutException:
        pass

    try:
        wait.until(lambda d: "/home" in d.current_url)
        save_cookies(driver)
        return True
    except TimeoutException:
        return False

def generate_post(ai_prompt):
    response = model.generate_content(ai_prompt)
    return response.text.strip()

def strip_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def make_post(driver, wait, post_text):
    driver.get("https://x.com/compose/post")
    audience_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Choose audience']")))
    audience_btn.click()
    time.sleep(2)

    community_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{COMMUNITY_NAME}']")))
    try:
        community_option.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", community_option)

    content_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
    content_box.click()
    clean_message = strip_non_bmp(post_text)
    content_box.send_keys(clean_message)

    # === Upload Image ===
    image_path = get_random_image(IMAGE_FOLDER)
    print(f"🖼️ Attaching image: {image_path}")
    upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
    upload_input.send_keys(image_path)

    time.sleep(3)  # wait for image to upload

    content_box.send_keys(Keys.CONTROL, Keys.ENTER)
    print(f"✅ Posted with image:\n{clean_message}")

# === Main Posting Loop ===
if __name__ == "__main__":
    ai_prompt = input("💡 Enter AI prompt for tweet generation (used every hour): ")
    while True:
        driver = get_driver()
        wait = WebDriverWait(driver, 30)

        try:
            driver.get("https://x.com/")
            if not (load_cookies(driver) and check_session(driver)):
                print("🔐 Logging in...")
                if not login_and_save(driver, wait):
                    raise Exception("Login failed.")

            print("🤖 Generating new tweet...")
            ai_post = generate_post(ai_prompt)
            make_post(driver, wait, ai_post)

        except Exception as e:
            print("❌ Error:", str(e))
        finally:
            driver.quit()

        print(f"⏳ Sleeping for {POST_INTERVAL // 60} minutes...")
        time.sleep(POST_INTERVAL)
