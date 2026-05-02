# core/ai_handler.py - FIXED VERSION
import os
import requests
import json
import logging
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        print(f"GROQ API Key: {'✓ Found' if self.api_key else '✗ Not found'}")
        
    def generate_message(self, prompt, tone="friendly", language="en"):
        """Generate human-like WhatsApp message using Groq AI"""
        
        if not self.api_key:
            print("⚠️ No API key, using fallback")
            return self._fallback_generation(prompt, tone)
        
        # Tone instructions
        tone_prompts = {
            "friendly": "Write a warm, friendly, conversational message. Use emojis naturally. Sound like a friend texting.",
            "professional": "Write a professional, respectful message. Be formal but not robotic.",
            "casual": "Write a casual, relaxed message. Use slang naturally. Like texting a buddy.",
            "urgent": "Write with urgency. Create a need to act quickly. Be direct but polite.",
            "promotional": "Write an exciting promotional message. Highlight benefits and create excitement."
        }
        
        # Create a simple, working prompt
        messages = [
            {
                "role": "system",
                "content": f"You are a WhatsApp message writer. {tone_prompts.get(tone, tone_prompts['friendly'])} Keep it short (max 300 characters). Make it sound human, not robotic. Use line breaks. Add 1-2 emojis naturally."
            },
            {
                "role": "user",
                "content": f"Write a WhatsApp message for: {prompt}"
            }
        ]
        
        try:
            print(f"🤖 Calling Groq API...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.3-70b-versatile",  # Using Llama 3 (more stable)
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 300,
                "top_p": 0.9
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']['content'].strip()
                print(f"✅ AI message generated")
                return message
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self._fallback_generation(prompt, tone)
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return self._fallback_generation(prompt, tone)
    
    def _fallback_generation(self, prompt, tone):
        """Fallback when API fails"""
        
        # Extract discount
        discount_match = re.search(r'(\d+)%', prompt)
        discount = discount_match.group(1) if discount_match else "great"
        
        # Detect product
        if "laptop" in prompt.lower():
            product = "laptops"
        elif "phone" in prompt.lower():
            product = "phones"
        elif "watch" in prompt.lower():
            product = "watches"
        else:
            product = "products"
        
        fallbacks = {
            "friendly": [
                f"Hey! 👋\n\nGuess what? We've got {discount}% off on {product}! 🎉\n\nThis is a steal! Want me to save one for you?\n\nLet me know! 😊",
                f"Hi there! 🌟\n\n{discount}% OFF on {product}! Just wanted to share this awesome deal with you.\n\nShould I reserve one for you?\n\nCheers! 🚀"
            ],
            "professional": [
                f"Hello,\n\nWe are pleased to offer {discount}% discount on our {product}.\n\nThis is a limited-time offer. Please reply for details.\n\nBest regards,\nTeam",
                f"Dear Customer,\n\n{discount}% OFF on {product}.\n\nFor more information, please reply to this message.\n\nThank you."
            ],
            "casual": [
                f"Yo! 🎉\n\n{discount}% off on {product}! Crazy right?\n\nLet me know if you want one!\n\nPeace! ✌️",
                f"Hey! 👋\n\n{discount}% OFF on {product}! What do you think?\n\nHit me up! 😎"
            ],
            "urgent": [
                f"⚠️ Quick heads up!\n\n{discount}% OFF on {product}!\n\nLimited time only! Don't miss out!\n\nReply now! 🚀",
                f"🔴 URGENT: {discount}% OFF on {product}!\n\nStock running low!\n\nMessage me ASAP! ⏰"
            ],
            "promotional": [
                f"🎉 FLASH SALE! 🎉\n\n{discount}% OFF on {product}!\n\n✓ Limited time\n✓ Best price\n✓ Quality guaranteed\n\nGrab yours now! 🛒",
                f"🔥 HOT DEAL! 🔥\n\n{discount}% OFF on {product}!\n\nDon't miss this opportunity!\n\nOrder now! 🚀"
            ]
        }
        
        import random
        selected = fallbacks.get(tone, fallbacks["friendly"])
        return random.choice(selected)