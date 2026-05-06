import requests
import logging
import re
from datetime import datetime
from decouple import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.access_token = config('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = config('PHONE_NUMBER_ID')
        self.business_account_id = config('WHATSAPP_BUSINESS_ACCOUNT_ID')
        self.api_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        self.debug_logs = []
        self.is_ready = True
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.debug_logs.append(log_entry)
        print(log_entry)
        
    def get_debug_logs(self):
        return self.debug_logs[-50:]
    
    def init_driver(self):
        """Initialize API handler (no driver needed)"""
        self.log("✅ WhatsApp Business API Ready")
        return True
    
    def check_ready(self):
        """API always ready"""
        return True
    
    def get_qr_code(self):
        """No QR needed for API"""
        return None
    
    def send_message(self, to_number, message):
        """Send message using WhatsApp Business API"""
        try:
            # Clean number
            clean_number = re.sub(r'[^\d]', '', to_number)
            if not clean_number.startswith('92'):
                clean_number = '92' + clean_number.lstrip('0')
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            self.log(f"📨 Sending to {clean_number}...")
            response = requests.post(self.api_url, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                self.log(f"✅ Sent to {clean_number}")
                return {'success': True, 'number': clean_number}
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                self.log(f"❌ Failed: {error_msg}", "ERROR")
                return {'success': False, 'number': clean_number, 'error': error_msg}
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return {'success': False, 'number': to_number, 'error': str(e)}
    
    def close(self):
        pass