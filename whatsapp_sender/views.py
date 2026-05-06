from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import threading
import time
import re
from datetime import datetime, timedelta
from .whatsapp_handler import WhatsAppHandler
from .ai_handler import AIHandler
import uuid

# Global instances
whatsapp_handler = None
ai_handler = AIHandler()
lock = threading.Lock()
scheduled_tasks = {}
scheduler_thread_running = True

# Message Scheduler Class
class MessageScheduler:
    def __init__(self):
        self.tasks = {}
        self.running = True
        self.task_counter = 0
        
    def add_task(self, task_id, numbers, message, messages_per_number, interval_type, interval_value, total_runs):
        """Add a scheduled task"""
        
        # Convert interval to seconds
        if interval_type == 'seconds':
            interval_seconds = interval_value
        elif interval_type == 'minutes':
            interval_seconds = interval_value * 60
        elif interval_type == 'hours':
            interval_seconds = interval_value * 3600
        else:  # days
            interval_seconds = interval_value * 86400
        
        task = {
            'id': task_id,
            'numbers': numbers,
            'message': message,
            'messages_per_number': messages_per_number,
            'interval_seconds': interval_seconds,
            'total_runs': total_runs,
            'completed_runs': 0,
            'next_run': datetime.now(),
            'status': 'active',
            'created_at': datetime.now(),
            'results': []
        }
        
        self.tasks[task_id] = task
        return task_id
    
    def get_task_status(self, task_id):
        """Get status of a task"""
        return self.tasks.get(task_id, None)
    
    def cancel_task(self, task_id):
        """Cancel a scheduled task"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'cancelled'
            return True
        return False
    
    def get_all_tasks(self):
        """Get all active tasks"""
        return {k: v for k, v in self.tasks.items() if v['status'] == 'active'}
    
    def run(self):
        """Run the scheduler"""
        global whatsapp_handler
        
        while self.running:
            now = datetime.now()
            
            for task_id, task in list(self.tasks.items()):
                if task['status'] != 'active':
                    continue
                
                if now >= task['next_run']:
                    if task['completed_runs'] >= task['total_runs']:
                        task['status'] = 'completed'
                        continue
                    
                    # Send messages
                    print(f"📨 Executing task {task_id} - Run {task['completed_runs'] + 1}/{task['total_runs']}")
                    
                    if not whatsapp_handler:
                        whatsapp_handler = get_handler()
                    
                    results = []
                    successful = 0
                    
                    for number in task['numbers']:
                        for i in range(task['messages_per_number']):
                            if task['messages_per_number'] > 1:
                                final_msg = f"[{i+1}/{task['messages_per_number']}] {task['message']}"
                            else:
                                final_msg = task['message']
                            
                            result = whatsapp_handler.send_message(number, final_msg)
                            results.append(result)
                            if result['success']:
                                successful += 1
                            time.sleep(2)  # Rate limit
                    
                    task['completed_runs'] += 1
                    task['next_run'] = now + timedelta(seconds=task['interval_seconds'])
                    task['results'].append({
                        'run_time': now.isoformat(),
                        'successful': successful,
                        'total': len(task['numbers']) * task['messages_per_number'],
                        'results': results
                    })
                    
                    print(f"✅ Task {task_id} completed run {task['completed_runs']}/{task['total_runs']}")
            
            time.sleep(1)  # Check every second

# Initialize scheduler
scheduler = MessageScheduler()

def start_scheduler():
    """Start the scheduler thread"""
    def run_scheduler():
        scheduler.run()
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

# Start scheduler when app loads
start_scheduler()

def get_handler():
    global whatsapp_handler
    with lock:
        if whatsapp_handler is None:
            whatsapp_handler = WhatsAppHandler()
            # API-based handler doesn't need driver initialization
            whatsapp_handler.init_driver()
        return whatsapp_handler

def index(request):
    return render(request, 'core/index.html')

@csrf_exempt
def check_connection(request):
    """Check API connection status"""
    handler = get_handler()
    # API-based handler always ready, no driver attribute needed
    is_connected = True  # WhatsApp Business API is always ready
    return JsonResponse({'connected': is_connected})

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
        
        # Scheduling parameters
        schedule_enabled = data.get('schedule_enabled', False)
        interval_value = int(data.get('interval_value', 1))
        interval_type = data.get('interval_type', 'hours')
        total_runs = int(data.get('total_runs', 1))
        
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
        
        # If scheduling is enabled
        if schedule_enabled and total_runs > 1:
            task_id = str(uuid.uuid4())[:8]
            
            scheduler.add_task(
                task_id=task_id,
                numbers=clean_numbers,
                message=message,
                messages_per_number=messages_per_number,
                interval_type=interval_type,
                interval_value=interval_value,
                total_runs=total_runs
            )
            
            # Format interval display
            interval_display = f"{interval_value} {interval_type}"
            
            return JsonResponse({
                'success': True,
                'scheduled': True,
                'task_id': task_id,
                'message': f'Campaign scheduled! Will send every {interval_display} for {total_runs} times',
                'summary': {
                    'total_numbers': len(clean_numbers),
                    'messages_per_number': messages_per_number,
                    'total_per_run': len(clean_numbers) * messages_per_number,
                    'total_messages': len(clean_numbers) * messages_per_number * total_runs,
                    'interval': f"{interval_value} {interval_type}",
                    'total_runs': total_runs,
                    'task_id': task_id
                }
            })
        
        # Immediate send (no scheduling)
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
                
                time.sleep(2)
        
        return JsonResponse({
            'success': True,
            'scheduled': False,
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
        print(f"Error in send_messages: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def check_numbers(request):
    try:
        data = json.loads(request.body)
        numbers_raw = data.get('numbers', '')
        
        numbers = re.split(r'[\n,\s]+', numbers_raw)
        numbers = [n.strip() for n in numbers if n.strip()]
        
        results = []
        for num in numbers[:50]:
            clean_num = re.sub(r'[^\d]', '', num)
            is_valid = len(clean_num) >= 10 and len(clean_num) <= 15
            
            results.append({
                'number': num,
                'has_whatsapp': is_valid,
                'status': '✅ Format valid' if is_valid else '❌ Invalid format'
            })
        
        return JsonResponse({'success': True, 'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_debug(request):
    handler = get_handler()
    return JsonResponse({'logs': handler.get_debug_logs()})

@csrf_exempt
def get_task_status(request):
    """Get status of a scheduled task"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id', '')
        
        task = scheduler.get_task_status(task_id)
        if task:
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task['id'],
                    'status': task['status'],
                    'completed_runs': task['completed_runs'],
                    'total_runs': task['total_runs'],
                    'next_run': task['next_run'].isoformat(),
                    'created_at': task['created_at'].isoformat(),
                    'total_numbers': len(task['numbers']),
                    'messages_per_number': task['messages_per_number']
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def cancel_task(request):
    """Cancel a scheduled task"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id', '')
        
        result = scheduler.cancel_task(task_id)
        return JsonResponse({'success': result})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})