import re
import time
import os
import subprocess
import urllib.request
import zipfile
import platform
import shutil
import logging
import psutil
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.debug_logs = []
        self.profile_dir = os.path.join(os.getcwd(), "whatsapp_dedicated_profile")
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        log_entry = f"[{timestamp}] {message}"
        self.debug_logs.append(log_entry)
        print(log_entry)
        if level == "ERROR":
            logger.error(log_entry)
        
    def get_debug_logs(self):
        return self.debug_logs[-50:]
    
    def is_whatsapp_chrome_running(self):
        """Check if WhatsApp Chrome is already running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info.get('cmdline', []))
                        if 'whatsapp_dedicated_profile' in cmdline:
                            return True
                except:
                    pass
        except:
            pass
        return False
    
    def kill_only_whatsapp_chrome(self):
        """Kill ONLY WhatsApp Chrome"""
        try:
            killed = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info.get('cmdline', []))
                        if 'whatsapp_dedicated_profile' in cmdline:
                            proc.kill()
                            killed += 1
                except:
                    pass
            
            if killed > 0:
                self.log(f"🗑️ Cleaned {killed} old Chrome processes")
                time.sleep(2)
        except Exception as e:
            self.log(f"⚠️ Cleanup warning: {str(e)}")
    
    def clean_profile_locks(self):
        """Clean profile locks"""
        try:
            if os.path.exists(self.profile_dir):
                lock_files = ['SingletonLock', 'SingletonCookie', 'SingletonSocket']
                for lock_file in lock_files:
                    lock_path = os.path.join(self.profile_dir, lock_file)
                    if os.path.exists(lock_path):
                        try:
                            os.remove(lock_path)
                        except:
                            pass
        except:
            pass
    
    def get_chrome_version(self):
        """Get Chrome version"""
        try:
            if platform.system() == "Windows":
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                    version = winreg.QueryValueEx(key, "version")[0]
                    return version
                except:
                    pass
                
                paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
                ]
                for path in paths:
                    if os.path.exists(path):
                        result = subprocess.run([path, '--version'], capture_output=True, text=True)
                        version = result.stdout.strip().split()[-1]
                        return version
            else:
                result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            pass
        return "131.0.6778.85"
    
    def download_chromedriver(self, chrome_version):
        """Download ChromeDriver"""
        try:
            if platform.system() == "Windows":
                platform_name = "win64"
                driver_name = "chromedriver.exe"
            elif platform.system() == "Darwin":
                platform_name = "mac-arm64" if platform.machine() == "arm64" else "mac-x64"
                driver_name = "chromedriver"
            else:
                platform_name = "linux64"
                driver_name = "chromedriver"
            
            url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/{platform_name}/chromedriver-{platform_name}.zip"
            
            driver_dir = os.path.join(os.getcwd(), "temp_driver")
            os.makedirs(driver_dir, exist_ok=True)
            zip_path = os.path.join(driver_dir, "chromedriver.zip")
            
            urllib.request.urlretrieve(url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
            extracted_folder = os.path.join(driver_dir, f"chromedriver-{platform_name}")
            source = os.path.join(extracted_folder, driver_name)
            destination = os.path.join(os.getcwd(), driver_name)
            
            if os.path.exists(destination):
                os.remove(destination)
            
            shutil.copy(source, destination)
            shutil.rmtree(driver_dir)
            
            return destination
            
        except Exception as e:
            self.log(f"❌ Download failed: {e}", "ERROR")
            return None
    
    def get_chromedriver_path(self):
        """Get ChromeDriver path"""
        driver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
        local_path = os.path.join(os.getcwd(), driver_name)
        
        if os.path.exists(local_path):
            return local_path
        
        chrome_version = self.get_chrome_version()
        if chrome_version:
            return self.download_chromedriver(chrome_version)
        
        return None
    
    def init_driver(self):
        """Initialize WhatsApp Web driver"""
        self.log("🚀 Starting WhatsApp Web...")
        
        if self.is_whatsapp_chrome_running():
            self.kill_only_whatsapp_chrome()
        
        self.clean_profile_locks()
        
        chromedriver_path = self.get_chromedriver_path()
        if not chromedriver_path:
            self.log("❌ ChromeDriver not found", "ERROR")
            return False
        
        os.makedirs(self.profile_dir, exist_ok=True)
        
        try:
            options = Options()
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-extensions")
            
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument("--profile-directory=WhatsAppProfile")
            
            import random
            debug_port = random.randint(9500, 9999)
            options.add_argument(f"--remote-debugging-port={debug_port}")
            
            options.add_argument("--window-size=900,700")
            options.add_argument("--window-position=50,50")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            
            service = Service(chromedriver_path)
            service.log_path = os.path.devnull
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("document.title = '🔴 WhatsApp - Connecting...';")
            
            self.log("📱 Opening WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Wait and check multiple times
            for i in range(10):
                time.sleep(2)
                if self.check_ready():
                    self.log("✅ Connected to WhatsApp!")
                    return True
            
            self.log("📲 Waiting for QR scan...")
            return True
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def check_ready(self):
        """Check if WhatsApp is connected - MULTIPLE METHODS"""
        if not self.driver:
            return False
        
        try:
            # METHOD 1: Check for side menu (pane-side)
            try:
                self.driver.find_element(By.ID, "pane-side")
                if not self.is_ready:
                    self.is_ready = True
                    self.log("✅ WhatsApp Connected (Method 1: Side Panel)")
                    self.driver.execute_script("document.title = '🟢 WhatsApp - Connected ✓';")
                return True
            except:
                pass
            
            # METHOD 2: Check for search box
            try:
                search = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                if search.is_displayed():
                    if not self.is_ready:
                        self.is_ready = True
                        self.log("✅ WhatsApp Connected (Method 2: Search Box)")
                        self.driver.execute_script("document.title = '🟢 WhatsApp - Connected ✓';")
                    return True
            except:
                pass
            
            # METHOD 3: Check for chat list
            try:
                self.driver.find_element(By.XPATH, "//div[@aria-label='Chat list']")
                if not self.is_ready:
                    self.is_ready = True
                    self.log("✅ WhatsApp Connected (Method 3: Chat List)")
                    self.driver.execute_script("document.title = '🟢 WhatsApp - Connected ✓';")
                return True
            except:
                pass
            
            # METHOD 4: Check URL
            current_url = self.driver.current_url
            if "web.whatsapp.com" in current_url and "qr" not in current_url.lower():
                # Check if not on QR page by looking for main app structure
                try:
                    self.driver.find_element(By.TAG_NAME, "header")
                    if not self.is_ready:
                        self.is_ready = True
                        self.log("✅ WhatsApp Connected (Method 4: URL Check)")
                        self.driver.execute_script("document.title = '🟢 WhatsApp - Connected ✓';")
                    return True
                except:
                    pass
            
            # Not connected
            if self.is_ready:
                self.is_ready = False
                self.log("⚠️ WhatsApp Disconnected")
                self.driver.execute_script("document.title = '🔴 WhatsApp - Scan QR Code';")
            
            return False
            
        except Exception as e:
            self.log(f"⚠️ Check error: {str(e)}", "ERROR")
            self.is_ready = False
            return False
    
    def get_qr_code(self):
        """Get QR code for display"""
        if not self.driver:
            return None
            
        if self.is_ready:
            return None
        
        try:
            # Try canvas method
            qr_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan this QR code to link a device!']"))
            )
            qr_base64 = self.driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(21);", 
                qr_element
            )
            self.log("📱 QR Code generated - Scan with WhatsApp")
            return f"data:image/png;base64,{qr_base64}"
        except:
            # Check if already connected
            if self.check_ready():
                return None
        
        return None
    
    def send_message(self, number, message, msg_count=1, total=1):
        """Send message to number"""
        if not self.check_ready():
            self.log("❌ WhatsApp not connected", "ERROR")
            return {'success': False, 'number': number, 'error': 'WhatsApp not connected'}
        
        try:
            clean_number = re.sub(r'[^\d+]', '', number)
            if not clean_number.startswith('+'):
                clean_number = '+' + clean_number
            
            # ✅ REMOVED: Counter logic - send original message only
            final_message = message
            
            self.log(f"📤 Sending message {msg_count}/{total} to {clean_number}...")
            
            # Direct URL method
            from urllib.parse import quote
            encoded_message = quote(final_message)
            url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_message}"
            
            self.driver.get(url)
            
            # Wait for chat to load
            time.sleep(5)  # Increased wait time
            
            # Check if invalid number
            try:
                invalid = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]")
                self.log(f"❌ Invalid number: {clean_number}", "ERROR")
                return {'success': False, 'number': number, 'error': 'Invalid phone number'}
            except:
                pass
            
            # Try multiple methods to send
            sent = False
            
            # METHOD 1: Click send button
            send_selectors = [
                "//span[@data-icon='send']",
                "//button[@aria-label='Send']",
                "//span[@data-testid='send']",
                "//*[@data-icon='send']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    send_button.click()
                    time.sleep(2)
                    sent = True
                    self.log(f"✅ Message {msg_count}/{total} sent to {clean_number}")
                    break
                except Exception as e:
                    continue
            
            # METHOD 2: Press Enter key if button not found
            if not sent:
                try:
                    msg_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                    msg_box.send_keys(Keys.ENTER)
                    time.sleep(2)
                    sent = True
                    self.log(f"✅ Message {msg_count}/{total} sent to {clean_number} (Enter key)")
                except Exception as e:
                    pass
            
            if not sent:
                self.log(f"❌ Failed to send to {clean_number}", "ERROR")
                return {'success': False, 'number': number, 'error': 'Send button not found'}
            
            return {'success': True, 'number': number}
            
        except Exception as e:
            self.log(f"❌ Error sending to {number}: {str(e)}", "ERROR")
            return {'success': False, 'number': number, 'error': str(e)}
            
    def close(self):
        """Close driver"""
        if self.driver:
            try:
                self.log("🔄 Closing WhatsApp...")
                self.driver.quit()
                self.is_ready = False
                time.sleep(1)
            except:
                pass
