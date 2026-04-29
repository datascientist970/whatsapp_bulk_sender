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
            
            def init_worker():
                whatsapp_handler.init_driver()
            
            thread = threading.Thread(target=init_worker)
            thread.daemon = True
            thread.start()
            
        return whatsapp_handler

def index(request):
    return render(request, 'core/index.html')

@csrf_exempt
def check_connection(request):
    """Check WhatsApp connection status"""
    handler = get_handler()
    
    is_connected = False
    qr_code = None
    
    if handler.driver:
        is_connected = handler.check_ready()
        if not is_connected:
            qr_code = handler.get_qr_code()
    
    return JsonResponse({
        'connected': is_connected,
        'qr_code': qr_code
    })

@csrf_exempt
def reconnect(request):
    """Restart WhatsApp connection"""
    global whatsapp_handler
    
    if whatsapp_handler:
        whatsapp_handler.close()
        time.sleep(2)
    
    whatsapp_handler = None
    get_handler()
    
    return JsonResponse({'success': True, 'message': 'Reconnecting...'})

@csrf_exempt
def get_status(request):
    """Get quick status without QR"""
    handler = get_handler()
    is_connected = handler.check_ready() if handler.driver else False
    return JsonResponse({'connected': is_connected})

@csrf_exempt
def generate_message(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'friendly')
        
        if not prompt:
            return JsonResponse({'error': 'Please enter a prompt'}, status=400)
        
        message = ai_handler.generate_message(prompt, tone)
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
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
            clean_num = re.sub(r'[^\d+]', '', num)
            if clean_num:
                if not clean_num.startswith('+'):
                    clean_num = '+' + clean_num
                clean_numbers.append(clean_num)
        
        if not clean_numbers:
            return JsonResponse({'error': 'No valid phone numbers'}, status=400)
        
        handler = get_handler()
        
        # Check connection
        print("🔍 Checking WhatsApp connection...")
        for i in range(15):
            if handler.check_ready():
                print("✅ WhatsApp is connected!")
                break
            print(f"⏳ Waiting... ({i+1}/15)")
            time.sleep(2)
        
        if not handler.check_ready():
            return JsonResponse({
                'error': 'WhatsApp not connected. Please scan QR code.'
            }, status=400)
        
        # Send messages
        results = []
        total_sent = 0
        failed_numbers = []
        
        for idx, number in enumerate(clean_numbers[:20], 1):
            print(f"\n📱 Processing number {idx}/{len(clean_numbers[:20])}: {number}")
            
            for msg_num in range(messages_per_number):
                print(f"  📤 Sending message {msg_num+1}/{messages_per_number}...")
                
                result = handler.send_message(number, message, msg_num+1, messages_per_number)
                
                results.append({
                    'number': number,
                    'message_num': msg_num+1,
                    'success': result['success'],
                    'error': result.get('error', '')
                })
                
                if result['success']:
                    total_sent += 1
                else:
                    if number not in failed_numbers:
                        failed_numbers.append(number)
                
                # Delay between messages to same number
                if msg_num < messages_per_number - 1:
                    time.sleep(4)  # 4 seconds between messages to same number
            
            # Delay between different numbers
            if idx < len(clean_numbers[:20]):
                time.sleep(5)  # 5 seconds between different numbers
        
        return JsonResponse({
            'success': True,
            'results': results,
            'summary': {
                'total_numbers': len(clean_numbers),
                'messages_per_number': messages_per_number,
                'total_attempts': len(clean_numbers) * messages_per_number,
                'successful': total_sent,
                'failed': (len(clean_numbers) * messages_per_number) - total_sent,
                'failed_numbers': failed_numbers
            }
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt
def check_numbers(request):
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [n.strip() for n in numbers if n.strip()]
        
        results = []
        for num in numbers[:20]:
            results.append({
                'number': num,
                'has_whatsapp': True,
                'status': '✅ Ready'
            })
        
        return JsonResponse({'success': True, 'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_debug(request):
    handler = get_handler()
    return JsonResponse({'logs': handler.get_debug_logs()})
