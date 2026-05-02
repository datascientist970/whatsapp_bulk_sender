# core/whatsapp_handler.py
import requests
import logging
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
        self.is_ready = True  # API always ready
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.debug_logs.append(log_entry)
        print(log_entry)
        
    def get_debug_logs(self):
        return self.debug_logs[-50:]
    
    def init_driver(self):
        """No driver needed for API"""
        self.log("✅ WhatsApp Business API Ready")
        return True
    
    def check_ready(self):
        """API always ready"""
        return True
    
    def get_qr_code(self):
        """No QR needed for API"""
        return None
    
    def create_template(self, name, body_text):
        """Create message template (needs approval)"""
        url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "name": name,
            "category": "MARKETING",
            "language": "en",
            "components": [
                {
                    "type": "BODY",
                    "text": body_text
                }
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def send_message(self, to_number, message):
        """Send message using WhatsApp Business API"""
        try:
            # Clean number
            import re
            clean_number = re.sub(r'[^\d]', '', to_number)
            if not clean_number.startswith('92'):
                clean_number = '92' + clean_number.lstrip('0')
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # For free-form messages (within 24h window)
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
            
            self.log(f"📨 Sending to +{clean_number}...")
            response = requests.post(self.api_url, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                self.log(f"✅ Sent to +{clean_number}")
                return {'success': True, 'number': clean_number, 'response': response.json()}
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                self.log(f"❌ Failed: {error_msg}", "ERROR")
                return {'success': False, 'number': clean_number, 'error': error_msg}
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return {'success': False, 'number': to_number, 'error': str(e)}
    
    def send_template_message(self, to_number, template_name, language="en"):
        """Send template message (for bulk marketing)"""
        try:
            import re
            clean_number = re.sub(r'[^\d]', '', to_number)
            if not clean_number.startswith('92'):
                clean_number = '92' + clean_number.lstrip('0')
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    }
                }
            }
            
            response = requests.post(self.api_url, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                return {'success': True, 'number': clean_number}
            else:
                return {'success': False, 'number': clean_number, 'error': response.json()}
                
        except Exception as e:
            return {'success': False, 'number': to_number, 'error': str(e)}
    
    def send_bulk_messages(self, numbers, message, messages_per_number=1, rate_limit_seconds=3):
        """Send bulk messages with rate limiting"""
        results = []
        total_sent = 0
        total_failed = 0
        
        for number in numbers:
            for i in range(messages_per_number):
                if messages_per_number > 1:
                    final_msg = f"[{i+1}/{messages_per_number}] {message}"
                else:
                    final_msg = message
                
                result = self.send_message(number, final_msg)
                results.append({
                    'number': number,
                    'message_num': i+1,
                    'success': result['success'],
                    'error': result.get('error', '')
                })
                
                if result['success']:
                    total_sent += 1
                else:
                    total_failed += 1
                
                import time
                time.sleep(rate_limit_seconds)
        
        return {
            'results': results,
            'summary': {
                'total_attempts': len(numbers) * messages_per_number,
                'successful': total_sent,
                'failed': total_failed
            }
        }
    
    def close(self):
        pass