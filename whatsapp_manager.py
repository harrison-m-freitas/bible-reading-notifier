import os
import json
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pyperclip

CHROME_PROFILE = os.path.abspath("C:\\Users\\hmarx\\AppData\\Local"
                                 "\\Google\\Chrome\\User Data\\Profile 2\\")
CHROME_DRIVER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "driver",
        "chromedriver.exe"
    )
)


class WhatsAppManager:
    """
    A class to manager WhatsApp Web automation using Selenium WebDriver
    
    Attributes:
        chrome_profile_path (str): Path to the Chrome user profile.
        chrome_driver_path (str): Path to the ChromeDriver executable.
        driver (webdriver.Chrome): Instance of the Chrome WebDriver
    """
    config_data = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "config",
            "data"
        )
    )
    
    debug_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "debug"
        )
    )
    
    cookies_path = os.path.join(config_data, "session_cookies.json")
    
    def __init__(self, chrome_profile_path: str, chrome_driver_path: str) -> None:
        """
        Initializes the WhatsAppManager with the specified Chrome profile and driver paths.
        
        Args:
            chrome_profile_path (str): Path to the Chrome user profile.
            chrome_driver_path (str): Path to the ChromeDriver executable.
        """
        self.chrome_profile_path = chrome_profile_path
        self.chrome_driver_path = chrome_driver_path
        self.driver = self.initialize_driver()
        if not self.is_logged_in():
            print("Please scan the QR code to log in to WhatsApp Web.")
            time.sleep(60)
            self.save_session()
            self.driver.quit()
            self.driver = self.initialize_driver(True)
        else:
            self.driver.quit()
            self.driver = self.initialize_driver(True)
            self.load_session()
        
    def initialize_driver(self, headless: bool = False) -> webdriver.Chrome:
        """
        Initializes the Chrome WebDriver with the specified user profile.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode.
        
        Returns:
            webdriver.Chrome: The initialized Chrome WebDriver.
        """
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={self.chrome_profile_path}")
        
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        

        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            
        chrome_service = Service(self.chrome_driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get("https://web.whatsapp.com")
        return driver
    
    def is_logged_in(self) -> bool:
        """Checks if the user is logged in to WhatsApp Web
        
        Returns:
            bool: True if the user is logged in, False otherwise
        """
        try:
            logged_in = EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[role='textbox']")
            )
            WebDriverWait(self.driver, 20).until(logged_in)
            return True
        except:
            return False
    
    def save_session(self) -> None:
        """
        Saves the session cookies to a file.
        """
        cookies = self.driver.get_cookies()
        with open(self.cookies_path, "w", encoding="UTF-8") as file:
            json.dump(cookies, file)
            
    def load_session(self) -> None:
        """"""
        with open(self.cookies_path, "r", encoding="UTF-8") as file:
            cookies = json.load(file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
            
    def find_chat(self, contact_name: str) -> None:
        """
        Finds and opens a chat with the specified contact name.
        
        Args:
            contact_name (str): The name of the contact to find 
            
        """
        search_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                "div[contenteditable='true'][data-tab='3']"
            ))
        )
        
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(4)
        
        chat = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[@title='{contact_name}']")
            )
        )
        chat.click()
    
    def send_message(self, contact_name: str, message: str) -> None:
        """
        Sends a message to the specified contact.
        
        Args:
            contact_name (str): The name of the contact to send the message to.
            message (str): The message to be sent.
        """
        self.find_chat(contact_name)
        message_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
            )
        )
        message_box.clear()
        
        print("Test Message Box")
        
        file_name = os.path.join(self.debug_folder, f"screenshot_message_box.png")
        message_box.screenshot(file_name)
        
        # pyperclip.copy(message)
        # print(message)
        
        # message_box.send_keys(message)
        
        # self.driver.execute_script("arguments[0].textContent = arguments[1];", message_box, message)
        
        send_button = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button[aria-label='Enviar']")
            )
        )
        send_button.click()
        time.sleep(2)
    
    def take_screenshot(self, file_name: str) -> None:
        """
        Takes a screenshot of the current state of the browser.
        
        Args:
            file_name (str): The name of the file to save the screenshot.
        """
        try:
            self.driver.save_screenshot(file_name)
            print(f"Screenshot saved as {file_name}")
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
    
    def start_debug_screenshots(self, interval: int = 5) -> None:
        """
        Starts taking screenshots every `interval` seconds and saves them in the debug folder.
        
        Args:
            interval (int): The time interval between each screenshot in seconds.
        """
        if not os.path.exists(self.debug_folder):
            os.makedirs(self.debug_folder)

        def take_screenshots():
            while True:
                
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                file_name = os.path.join(self.debug_folder, f"screenshot_{timestamp}.png")
                self.take_screenshot(file_name)
                time.sleep(interval)

        thread = threading.Thread(target=take_screenshots)
        thread.daemon = True
        thread.start()
    
    def close(self) -> None:
        """
        Closes the Chrome WebDriver.
        """
        self.driver.quit()
        
        
if __name__ == "__main__":
    # print(CHROME_DRIVER)
    # print(CHROME_PROFILE)
    whatsapp_manager = WhatsAppManager(CHROME_PROFILE, CHROME_DRIVER)
    whatsapp_manager.start_debug_screenshots()
    whatsapp_manager.send_message("Bloco de Notas", "Test Message! :), :smile\n\n\nTesting (\\n)")
    whatsapp_manager.close()
