# core/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import threading
import time
import re
from .whatsapp_handler import WhatsAppHandler
from .ai_handler import AIHandler

whatsapp_handler = None
ai_handler = AIHandler()
lock = threading.Lock()

def get_handler():
    global whatsapp_handler
    with lock:
        if whatsapp_handler is None:
            whatsapp_handler = WhatsAppHandler()
            whatsapp_handler.init_driver()
        return whatsapp_handler

def index(request):
    return render(request, 'core/index.html')

@csrf_exempt
def check_connection(request):
    handler = get_handler()
    return JsonResponse({
        'connected': True,
        'message': 'WhatsApp Business API Ready',
        'qr_code': None
    })

@csrf_exempt
def generate_message(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'friendly')
        language = data.get('language', 'en')
        
        if not prompt:
            return JsonResponse({'error': 'Please enter a prompt'}, status=400)
        
        message = ai_handler.generate_message(prompt, tone, language)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def send_messages(request):
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        message = data.get('message', '')
        messages_per_number = int(data.get('messages_per_number', 1))
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Parse numbers
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [n.strip() for n in numbers if n.strip()]
        
        # Clean numbers
        clean_numbers = []
        for num in numbers:
            clean_num = re.sub(r'[^\d]', '', num)
            if clean_num:
                if not clean_num.startswith('92'):
                    clean_num = '92' + clean_num.lstrip('0')
                clean_numbers.append(clean_num)
        
        if not clean_numbers:
            return JsonResponse({'error': 'No valid phone numbers'}, status=400)
        
        handler = get_handler()
        
        # Check rate limit
        rate_limit = 3  # seconds between messages
        
        results = []
        total_sent = 0
        total_failed = 0
        total_attempts = len(clean_numbers) * messages_per_number
        
        for number in clean_numbers:
            for i in range(messages_per_number):
                if messages_per_number > 1:
                    final_msg = f"[{i+1}/{messages_per_number}] {message}"
                else:
                    final_msg = message
                
                result = handler.send_message(number, final_msg)
                
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
                
                time.sleep(rate_limit)
        
        return JsonResponse({
            'success': True,
            'results': results,
            'summary': {
                'total_numbers': len(clean_numbers),
                'messages_per_number': messages_per_number,
                'total_attempts': total_attempts,
                'successful': total_sent,
                'failed': total_failed,
                'success_rate': f"{(total_sent/total_attempts*100):.1f}%" if total_attempts > 0 else "0%"
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def check_numbers(request):
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [n.strip() for n in numbers if n.strip()]
        
        # Format check only - API will validate during send
        results = []
        for num in numbers[:50]:
            clean_num = re.sub(r'[^\d]', '', num)
            is_valid = len(clean_num) >= 10 and len(clean_num) <= 15
            
            results.append({
                'number': num,
                'has_whatsapp': is_valid,
                'status': '✅ Number format valid' if is_valid else '❌ Invalid number format'
            })
        
        return JsonResponse({'success': True, 'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_debug(request):
    handler = get_handler()
    return JsonResponse({'logs': handler.get_debug_logs()})

@csrf_exempt
def create_template(request):
    """Create message template for marketing (requires approval)"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '')
        body = data.get('body', '')
        
        handler = get_handler()
        result = handler.create_template(name, body)
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)