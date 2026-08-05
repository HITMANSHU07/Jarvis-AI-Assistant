from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = None

def get_driver():

    global driver
    if driver is not None:
        try:
            _ = driver.current_url 
        except:
         driver = None 
    if driver is None:

        try:

            chrome_options = Options()

            chrome_options.add_argument("--start-maximized")

            chrome_options.add_argument("--disable-notifications")

            service = Service(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=chrome_options)

        except Exception as e:

            print(f"DRIVER SETUP ERROR: {e}")

            return None

    return driver

def play_youtube(query: str):
    d = get_driver()
    if not d: return
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        d.get(search_url)
        
        # Youtube load hone ka wait
        time.sleep(3)
        
        # Naya selector jo YouTube ke har layout mein kaam karta hai
        # Hum 'ytd-video-renderer' ke andar 'h3' ya 'a' dhoond rahe hain
        videos = d.find_elements(By.XPATH, '(//a[@id="video-title"])[1]')
        
        if videos:
            videos[0].click()
            print(f"▶️ Playing: {query}")
        else:
            print("DEBUG: Could not find video element using XPATH")
            
    except Exception as e:
        print(f"CRITICAL BROWSER ERROR: {e}")

def open_website(url: str):
    d = get_driver()
    if not d: return
    try:
        if not url.startswith("http"): url = "https://" + url
        d.get(url)
        print(f"🌐 Opened: {url}")
    except Exception as e:
        print(f"BROWSER ERROR: {e}")