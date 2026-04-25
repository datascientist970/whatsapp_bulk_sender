# core/whatsapp_handler.py (updated send_message method)
import re
import time
import os
import traceback
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.debug_logs = []
        self.qr_code_data = None
        
    def log(self, message, level="INFO"):
        """Add debug log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.debug_logs.append(log_entry)
        print(log_entry)
        if level == "ERROR":
            logger.error(message)
        else:
            logger.debug(message)
    
    def get_debug_logs(self):
        """Return all debug logs"""
        return self.debug_logs[-50:]  # Last 50 logs
    
    def init_driver(self, headless=False):
        """Initialize Chrome driver with comprehensive error handling"""
        self.log("Starting WhatsApp Web driver initialization...")
        
        # Step 1: Check Chrome installation
        self.log("Step 1: Checking Chrome browser installation")
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                self.log(f"✓ Chrome found at: {path}")
                chrome_found = True
                break
        
        if not chrome_found:
            self.log("✗ Chrome not found in standard locations", "ERROR")
            self.log("Please install Google Chrome from: https://www.google.com/chrome/", "ERROR")
            return False
        
        # Step 2: Configure Chrome options
        self.log("Step 2: Configuring Chrome options")
        try:
            chrome_options = Options()
            
            # Create user data directory for persistent session
            profile_dir = os.path.join(os.getcwd(), "whatsapp_profile")
            os.makedirs(profile_dir, exist_ok=True)
            self.log(f"✓ Profile directory: {profile_dir}")
            
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.log("✓ Chrome options configured")
        except Exception as e:
            self.log(f"✗ Failed to configure Chrome options: {str(e)}", "ERROR")
            return False
        
        # Step 3: Setup ChromeDriver
        self.log("Step 3: Setting up ChromeDriver")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.log("Attempting to download/update ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            self.log(f"✓ ChromeDriver installed at: {driver_path}")
            service = Service(driver_path)
        except Exception as e:
            self.log(f"WebDriver manager failed: {str(e)}", "WARNING")
            self.log("Trying system ChromeDriver...")
            try:
                service = Service()
                self.log("✓ Using system ChromeDriver")
            except Exception as e2:
                self.log(f"✗ Failed to create ChromeDriver service: {str(e2)}", "ERROR")
                self.log("Please install ChromeDriver manually from: https://chromedriver.chromium.org/", "ERROR")
                return False
        
        # Step 4: Create WebDriver
        self.log("Step 4: Creating WebDriver instance")
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.log("✓ WebDriver created successfully")
        except Exception as e:
            self.log(f"✗ Failed to create WebDriver: {str(e)}", "ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
        
        # Step 5: Navigate to WhatsApp Web
        self.log("Step 5: Navigating to WhatsApp Web")
        try:
            self.driver.get("https://web.whatsapp.com")
            self.log("✓ WhatsApp Web page loaded")
            self.log(f"Current URL: {self.driver.current_url}")
        except Exception as e:
            self.log(f"✗ Failed to load WhatsApp Web: {str(e)}", "ERROR")
            return False
        
        # Step 6: Wait for initial load
        self.log("Step 6: Waiting for page to stabilize...")
        time.sleep(3)
        
        # Check page title
        try:
            title = self.driver.title
            self.log(f"Page title: {title}")
        except:
            pass
        
        self.log("✓ Driver initialization complete")
        return True
    
    def check_ready(self):
        """Check if already logged into WhatsApp"""
        self.log("Checking WhatsApp login status...")
        
        if not self.driver:
            self.log("Driver not initialized", "WARNING")
            return False
        
        try:
            # Check for various elements that indicate logged-in state
            login_indicators = [
                ("//div[@contenteditable='true']", "Search box (logged in)"),
                ("//div[@data-tab='3']", "Chats tab (logged in)"),
                ("//div[@title='Menu']", "Menu button (logged in)"),
                ("//canvas[@aria-label='Scan this QR code']", "QR code (not logged in)")
            ]
            
            for xpath, description in login_indicators:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if "QR code" in description:
                        self.log(f"Found: {description} - Not logged in yet")
                        self.is_ready = False
                        return False
                    else:
                        self.log(f"✓ Found: {description} - User is logged in!")
                        self.is_ready = True
                        return True
                except TimeoutException:
                    continue
            
            # Check URL
            current_url = self.driver.current_url
            self.log(f"Current URL: {current_url}")
            
            if "web.whatsapp.com" in current_url:
                self.log("On WhatsApp Web, checking for QR code availability...")
            
            self.is_ready = False
            return False
            
        except Exception as e:
            self.log(f"Error checking ready state: {str(e)}", "ERROR")
            self.is_ready = False
            return False
    
    def get_qr_code(self):
        """Extract QR code from WhatsApp Web with multiple methods"""
        self.log("Attempting to extract QR code...")
        
        if not self.driver:
            self.log("Driver not initialized, cannot get QR code", "ERROR")
            return None
        
        # Method 1: Get data-ref attribute
        self.log("Method 1: Looking for data-ref attribute")
        try:
            qr_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-ref]"))
            )
            qr_data = qr_element.get_attribute("data-ref")
            if qr_data:
                self.log(f"✓ Found data-ref QR data (length: {len(qr_data)} characters)")
                # Generate QR code image using external API
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_data}"
                self.qr_code_data = qr_url
                return qr_url
        except TimeoutException:
            self.log("No data-ref element found after 10 seconds")
        except Exception as e:
            self.log(f"Method 1 failed: {str(e)}")
        
        # Method 2: Look for canvas element
        self.log("Method 2: Looking for canvas element")
        try:
            canvas = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            if canvas:
                self.log("✓ Found canvas element, capturing screenshot")
                screenshot = canvas.screenshot_as_base64
                self.log(f"✓ Canvas screenshot captured (length: {len(screenshot)})")
                qr_base64 = f"data:image/png;base64,{screenshot}"
                self.qr_code_data = qr_base64
                return qr_base64
        except TimeoutException:
            self.log("No canvas element found")
        except Exception as e:
            self.log(f"Method 2 failed: {str(e)}")
        
        # Method 3: Take full page screenshot
        self.log("Method 3: Taking full page screenshot")
        try:
            screenshot = self.driver.get_screenshot_as_base64()
            self.log(f"✓ Page screenshot captured (length: {len(screenshot)})")
            # This is not ideal but better than nothing
            return f"data:image/png;base64,{screenshot}"
        except Exception as e:
            self.log(f"Method 3 failed: {str(e)}")
        
        self.log("All QR code extraction methods failed", "ERROR")
        return None
    
    def check_number_whatsapp(self, number):
        """Check if a phone number has WhatsApp"""
        if not self.check_ready():
            return False
        
        try:
            clean_number = re.sub(r'[^\d+]', '', number)
            if not clean_number.startswith('+'):
                clean_number = '+' + clean_number
            
            # Find search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            search_box.clear()
            search_box.send_keys(clean_number)
            time.sleep(2)
            
            # Check if contact exists
            try:
                contact = self.driver.find_element(By.XPATH, f"//span[@title='{clean_number}']")
                return True
            except NoSuchElementException:
                return False
        except Exception as e:
            self.log(f"Error checking number {number}: {str(e)}", "ERROR")
            return False
    
    def send_message(self, number, message):
        """Send WhatsApp message to a number"""
        if not self.check_ready():
            return {'success': False, 'number': number, 'error': 'WhatsApp not connected'}
        
        try:
            clean_number = re.sub(r'[^\d+]', '', number)
            if not clean_number.startswith('+'):
                clean_number = '+' + clean_number
            
            # Click new chat button
            try:
                new_chat = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@title='New chat']"))
                )
                new_chat.click()
                time.sleep(1)
            except:
                # Alternative method
                pass
            
            # Search for number
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            search_input.clear()
            search_input.send_keys(clean_number)
            time.sleep(2)
            
            # Click on contact
            try:
                contact = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{clean_number}']"))
                )
                contact.click()
                time.sleep(1)
            except:
                # Try alternative selector
                first_result = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='_ak8q']"))
                )
                first_result.click()
                time.sleep(1)
            
            # Type and send message
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            message_box.clear()
            message_box.send_keys(message)
            time.sleep(1)
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            return {'success': True, 'number': number, 'message': message[:50]}
            
        except Exception as e:
            return {'success': False, 'number': number, 'error': str(e)}
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.log("Driver closed")