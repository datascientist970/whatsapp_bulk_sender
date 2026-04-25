# core/views.py (updated)
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import threading
import time
import re
from .whatsapp_handler import WhatsAppHandler
from .ai_handler import AIHandler

# Global instances
whatsapp_handler = None
ai_handler = AIHandler()
handler_lock = threading.Lock()
initialization_thread = None

def get_handler():
    """Get or create WhatsApp handler singleton"""
    global whatsapp_handler, initialization_thread
    
    with handler_lock:
        if whatsapp_handler is None:
            whatsapp_handler = WhatsAppHandler()
            
            # Initialize in background thread
            def init_worker():
                whatsapp_handler.init_driver()
            
            initialization_thread = threading.Thread(target=init_worker)
            initialization_thread.daemon = True
            initialization_thread.start()
            
        return whatsapp_handler

def index(request):
    """Main page with debug panel"""
    return render(request, 'core/index.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_debug_info(request):
    """Get debug information for troubleshooting"""
    handler = get_handler()
    
    debug_info = {
        'logs': handler.get_debug_logs(),
        'driver_exists': handler.driver is not None,
        'is_ready': handler.is_ready,
        'current_url': handler.driver.current_url if handler.driver else None,
        'timestamp': time.time()
    }
    
    return JsonResponse(debug_info)

@csrf_exempt
@require_http_methods(["GET"])
def check_connection(request):
    """Check WhatsApp connection status and get QR code if needed"""
    handler = get_handler()
    
    # Wait a bit for initialization
    time.sleep(2)
    
    # Check if already connected
    is_connected = False
    if handler.driver:
        is_connected = handler.check_ready()
    
    qr_code = None
    if not is_connected and handler.driver:
        qr_code = handler.get_qr_code()
    
    return JsonResponse({
        'connected': is_connected,
        'qr_code': qr_code,
        'message': 'Connected to WhatsApp' if is_connected else 'Scan QR code to connect'
    })

@csrf_exempt
@require_http_methods(["POST"])
def reconnect_whatsapp(request):
    """Force reconnect WhatsApp"""
    global whatsapp_handler
    
    if whatsapp_handler:
        whatsapp_handler.close()
    
    whatsapp_handler = WhatsAppHandler()
    
    def init_worker():
        whatsapp_handler.init_driver()
    
    thread = threading.Thread(target=init_worker)
    thread.daemon = True
    thread.start()
    
    return JsonResponse({
        'success': True,
        'message': 'Reconnecting... Please wait'
    })

@csrf_exempt
@require_http_methods(["POST"])
def generate_ai_message(request):
    """Generate message using AI"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'professional')
        
        if not prompt:
            return JsonResponse({'error': 'Please provide a prompt'}, status=400)
        
        message = ai_handler.generate_message(prompt, tone)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'tone': tone
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_messages(request):
    """Send WhatsApp messages to multiple numbers with count option"""
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        message = data.get('message', '')
        messages_per_number = int(data.get('messages_per_number', 1))  # New field
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        if messages_per_number < 1 or messages_per_number > 50:
            return JsonResponse({'error': 'Number of messages must be between 1 and 50'}, status=400)
        
        # Parse numbers (support newline, comma, space separated)
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [num.strip() for num in numbers if num.strip()]
        
        # Clean and format numbers
        clean_numbers = []
        for num in numbers:
            clean_num = re.sub(r'[^\d+]', '', num)
            if clean_num:
                if not clean_num.startswith('+'):
                    clean_num = '+' + clean_num
                clean_numbers.append(clean_num)
        
        if not clean_numbers:
            return JsonResponse({'error': 'No valid phone numbers found'}, status=400)
        
        handler = get_handler()
        
        # Check if WhatsApp is ready
        if not handler.driver or not handler.check_ready():
            return JsonResponse({'error': 'WhatsApp not connected. Please scan QR code first.'}, status=400)
        
        # Send messages with count
        results = []
        successful_total = 0
        failed_total = 0
        total_attempts = len(clean_numbers) * messages_per_number
        
        for number in clean_numbers[:20]:  # Limit to 20 numbers per batch
            number_results = {
                'number': number,
                'successful': 0,
                'failed': 0,
                'messages': []
            }
            
            # Send multiple messages to the same number
            for msg_count in range(1, messages_per_number + 1):
                # Add counter to message if sending multiple
                if messages_per_number > 1:
                    numbered_message = f"[{msg_count}/{messages_per_number}] {message}"
                else:
                    numbered_message = message
                
                result = handler.send_message(number, numbered_message)
                
                if result['success']:
                    number_results['successful'] += 1
                    successful_total += 1
                    number_results['messages'].append({'count': msg_count, 'success': True})
                else:
                    number_results['failed'] += 1
                    failed_total += 1
                    number_results['messages'].append({'count': msg_count, 'success': False, 'error': result.get('error', 'Unknown error')})
                
                # Delay between messages to avoid rate limiting
                if messages_per_number > 1:
                    time.sleep(1)  # 1 second between messages to same number
            
            results.append(number_results)
            time.sleep(2)  # Delay between different numbers
        
        return JsonResponse({
            'success': True,
            'results': results,
            'summary': {
                'total_numbers': len(clean_numbers),
                'messages_per_number': messages_per_number,
                'total_attempts': total_attempts,
                'successful': successful_total,
                'failed': failed_total,
                'success_rate': f"{(successful_total/total_attempts*100):.1f}%" if total_attempts > 0 else "0%",
                'processed_numbers': len(results),
                'limited': len(clean_numbers) > 20
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def check_numbers(request):
    """Check if phone numbers have WhatsApp"""
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        
        # Parse numbers
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [num.strip() for num in numbers if num.strip()]
        
        # Clean numbers
        clean_numbers = []
        for num in numbers:
            clean_num = re.sub(r'[^\d+]', '', num)
            if clean_num:
                if not clean_num.startswith('+'):
                    clean_num = '+' + clean_num
                clean_numbers.append(clean_num)
        
        handler = get_handler()
        
        results = []
        for number in clean_numbers[:20]:  # Check max 20 numbers
            has_whatsapp = handler.check_number_whatsapp(number)
            results.append({
                'number': number,
                'has_whatsapp': has_whatsapp,
                'status': '✅ Has WhatsApp' if has_whatsapp else '❌ No WhatsApp'
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'total_checked': len(results),
            'total_numbers': len(clean_numbers)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)