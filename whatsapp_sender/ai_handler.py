import os
import requests
import random

class AIHandler:
    def __init__(self):
        # Get Groq API key from environment variable
        self.api_key = os.environ.get('GROQ_API_KEY', '')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Fallback to templates if no API key
        self.use_ai = bool(self.api_key)
        
        if self.use_ai:
            print("✅ AI Handler: Using Groq API")
        else:
            print("⚠️ AI Handler: Using template mode (Set GROQ_API_KEY for real AI)")
    
    def generate_message(self, prompt, tone="friendly"):
        """Generate WhatsApp message using AI or templates"""
        
        # Try AI generation first
        if self.use_ai:
            try:
                return self._generate_with_ai(prompt, tone)
            except Exception as e:
                print(f"⚠️ AI generation failed: {e}")
                print("📝 Falling back to templates")
        
        # Fallback to templates
        return self._generate_with_templates(prompt, tone)
    
    def _generate_with_ai(self, prompt, tone):
        """Generate message using Groq AI"""
        
        # Tone-specific instructions
        tone_instructions = {
            "friendly": "Create a warm, friendly WhatsApp message. Use emojis moderately. Keep it casual and personal.",
            "professional": "Create a professional business WhatsApp message. Be formal and respectful. Use minimal emojis.",
            "casual": "Create a very casual, relaxed WhatsApp message. Use modern slang and lots of emojis. Be fun!",
            "urgent": "Create an urgent WhatsApp message. Make it clear this requires immediate attention. Use warning emojis.",
            "promotional": "Create an exciting promotional WhatsApp message. Make it persuasive and action-oriented. Use attractive emojis."
        }
        
        system_prompt = f"""You are a WhatsApp message writer. 
{tone_instructions.get(tone, tone_instructions['friendly'])}

IMPORTANT RULES:
1. Keep the message SHORT (max 5 lines)
2. Make it RELEVANT to the user's request
3. Write ONLY the message content (no explanations)
4. Use natural WhatsApp language
5. DON'T just repeat the user's prompt - EXPAND on it meaningfully"""

        user_message = f"Write a {tone} WhatsApp message about: {prompt}"
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 300,
            "top_p": 0.9
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content'].strip()
            
            # Remove any markdown formatting
            message = message.replace('**', '').replace('*', '')
            
            return message
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def _generate_with_templates(self, prompt, tone):
        """Generate message using templates (fallback)"""
        
        templates = {
            "friendly": [
                f"Hey! 👋\n\n{self._expand_prompt(prompt, tone)}\n\nWhat do you think? Let me know! 😊",
                f"Hello friend! 🌟\n\n{self._expand_prompt(prompt, tone)}\n\nWould love to hear your thoughts!\n\nBest regards!",
                f"Hi there! 👋\n\n{self._expand_prompt(prompt, tone)}\n\nLooking forward to connecting!\n\nCheers! 🎉"
            ],
            "professional": [
                f"Dear Sir/Madam,\n\n{self._expand_prompt(prompt, tone)}\n\nThank you for your attention.\n\nBest regards,\nTeam",
                f"Respected Sir/Madam,\n\n{self._expand_prompt(prompt, tone)}\n\nWe appreciate your cooperation.\n\nSincerely,\nManagement",
                f"Hello,\n\n{self._expand_prompt(prompt, tone)}\n\nPlease feel free to contact us for any queries.\n\nRegards"
            ],
            "casual": [
                f"Yo! 🎉\n\n{self._expand_prompt(prompt, tone)}\n\nWhat's up? Let me know!\n\nPeace! ✌️",
                f"Hey! 👋\n\n{self._expand_prompt(prompt, tone)}\n\nHit me back when you can!\n\nLater! 😎",
                f"Sup! 🔥\n\n{self._expand_prompt(prompt, tone)}\n\nCatch ya later! 🤙"
            ],
            "urgent": [
                f"⚠️ URGENT NOTICE ⚠️\n\n{self._expand_prompt(prompt, tone)}\n\nPlease respond ASAP!\n\nThank you.",
                f"🔴 IMPORTANT: {self._expand_prompt(prompt, tone)}\n\nYour immediate response is required.",
                f"⚡ URGENT: {self._expand_prompt(prompt, tone)}\n\nAction needed now!"
            ],
            "promotional": [
                f"🎉 SPECIAL OFFER! 🎉\n\n{self._expand_prompt(prompt, tone)}\n\nLimited time only! Don't miss out!\n\nAct now! 🚀",
                f"🔥 EXCLUSIVE DEAL! 🔥\n\n{self._expand_prompt(prompt, tone)}\n\nHurry! Offer ends soon!\n\nGrab it now! ⚡",
                f"💎 AMAZING OPPORTUNITY! 💎\n\n{self._expand_prompt(prompt, tone)}\n\nLimited spots available!\n\nClaim yours! 🎯"
            ]
        }
        
        selected = templates.get(tone, templates["friendly"])
        return random.choice(selected)
    
    def _expand_prompt(self, prompt, tone):
        """Expand user prompt into proper message content"""
        
        # Simple prompt expansion logic
        prompt_lower = prompt.lower()
        
        # If it's a command-like prompt, convert to natural message
        expansions = {
            # Welcoming messages
            "welcoming": "It's wonderful to have you here! I hope we can connect and share great moments together.",
            "welcome": "Welcome! I'm so glad you're here. Looking forward to getting to know you better!",
            
            # Greetings
            "greeting": "I hope this message finds you well! Just wanted to reach out and say hello.",
            "hello": "Hello! I hope you're having a great day. Just wanted to check in with you!",
            
            # Promotional
            "sale": "We're having an amazing sale right now with incredible discounts on all products!",
            "offer": "I have a fantastic offer for you that I think you'll absolutely love!",
            "discount": "Get exclusive discounts up to 50% off on selected items this week only!",
            
            # Business
            "meeting": "I'd like to schedule a meeting with you to discuss some important matters.",
            "proposal": "I have an exciting business proposal that I'd love to share with you.",
            
            # General
            "update": "I wanted to share some exciting updates with you!",
            "news": "I have some great news to share with you today!",
        }
        
        # Check if prompt matches any expansion
        for key, expansion in expansions.items():
            if key in prompt_lower:
                return expansion
        
        # If no match, intelligently expand based on tone
        if tone == "friendly":
            return f"I wanted to reach out about {prompt}. Hope you're doing great!"
        elif tone == "professional":
            return f"This is regarding {prompt}. We would appreciate your attention to this matter."
        elif tone == "casual":
            return f"So, about {prompt}... thought you'd wanna know!"
        elif tone == "urgent":
            return f"IMPORTANT: This concerns {prompt} and requires your immediate attention."
        elif tone == "promotional":
            return f"Exciting news about {prompt}! You don't want to miss this amazing opportunity!"
        else:
            return prompt
