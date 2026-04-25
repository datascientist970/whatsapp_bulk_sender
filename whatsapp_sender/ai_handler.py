# core/ai_handler.py
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def generate_message(self, prompt, tone="professional", max_length=500):
        """Generate message using Groq API or fallback"""
        
        tone_styles = {
            "professional": "Write a professional, formal business message. Use proper language.",
            "casual": "Write a casual, friendly, everyday conversation style.",
            "friendly": "Write a warm, friendly message with emojis and positive language.",
            "urgent": "Write with urgency, be direct and action-oriented.",
            "promotional": "Write an exciting promotional message highlighting benefits.",
            "humorous": "Write a funny, entertaining message that still gets the point across."
        }
        
        # Fallback messages if API fails
        fallback_messages = {
            "professional": f"Dear Customer,\n\nRegarding: {prompt}\n\nThank you for your interest. Please contact us for more information.\n\nBest regards,\nTeam",
            "casual": f"Hey there! 👋\n\nAbout {prompt}\n\nLet me know if you need anything! Cheers! 🎉",
            "friendly": f"Hello friend! 😊\n\n{prompt}\n\nFeel free to reach out anytime! Take care! 🌟",
            "urgent": f"⚠️ URGENT UPDATE ⚠️\n\n{prompt}\n\nPlease respond as soon as possible! ⏰",
            "promotional": f"🎉 SPECIAL OFFER! 🎉\n\n{prompt}\n\nLimited time only! Don't miss out! 🚀",
            "humorous": f"Guess what?! 😄\n\n{prompt}\n\nThat's the deal! What do you think? 😎"
        }
        
        # If no API key, use fallback
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            return fallback_messages.get(tone, fallback_messages["professional"])
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a WhatsApp message writer. {tone_styles.get(tone, '')} Keep it concise, max 500 characters. Use emojis appropriately. Add line breaks for readability."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a WhatsApp message about: {prompt}"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": max_length
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            message = result['choices'][0]['message']['content']
            return message.strip()
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return fallback_messages.get(tone, fallback_messages["professional"])