from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .agents.orchestrator import get_orchestrator
from .models import ChatLog, ChatMonitoring
import json

def signup(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            
            return JsonResponse({'status': 'success', 'redirect': '/chat'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'interagent/signup.html')

def user_login(request):
    # If user is already authenticated, redirect to chat
    if request.user.is_authenticated:
        return redirect('chat')
        
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # Set session variable to prevent back button access after logout
                request.session['is_logged_in'] = True
                return JsonResponse({'status': 'success', 'redirect': '/chat'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'interagent/login.html')

@login_required
def chat_view(request):
    # Get chat history
    chat_logs = ChatLog.objects.filter(user=request.user).order_by('timestamp')
    # Determine if monitoring is currently active for this user
    active_monitoring = ChatMonitoring.objects.filter(user=request.user, end_time__isnull=True).last()
    is_monitored = bool(active_monitoring)
    return render(request, 'interagent/chat.html', {'chat_logs': chat_logs, 'is_monitored': is_monitored})

@login_required
@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            # Parse the incoming message
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Message is required'
                })
            
            # Process through orchestrator
            orchestrator = get_orchestrator()
            result = orchestrator.process_message(message)
            
            # Get current monitoring session if exists
            active_monitoring = ChatMonitoring.objects.filter(
                user=request.user,
                end_time__isnull=True
            ).last()
            
            # Save to chat log
            ChatLog.objects.create(
                user=request.user,
                sender='user',
                message=message,
                monitoring_session=active_monitoring
            )
            
            # Save agent responses with appropriate sender types
            sender_types = ['assistant', 'search', 'decision']
            for i, bot_message in enumerate(result['messages']):
                sender = sender_types[i] if i < len(sender_types) else 'assistant'
                ChatLog.objects.create(
                    user=request.user,
                    sender=sender,
                    message=bot_message,
                    monitoring_session=active_monitoring
                )
            
            return JsonResponse({
                'status': 'success',
                'messages': result['messages']
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error processing message: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

@login_required
def chat_history(request):
    # Get all chat logs for current user
    chat_logs = ChatLog.objects.filter(user=request.user).order_by('timestamp')
    
    # Format for display
    history = [{
        'sender': log.sender,
        'message': log.message,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for log in chat_logs]
    
    return JsonResponse({
        'status': 'success',
        'history': history
    })

@login_required
def toggle_monitoring(request):
    """Toggle human monitoring for chat"""
    if request.method == 'POST':
        try:
            # Get current monitoring status
            current_monitoring = ChatMonitoring.objects.filter(
                user=request.user,
                end_time__isnull=True
            ).last()
            
            if current_monitoring:
                # Turn off monitoring
                current_monitoring.end_time = timezone.now()
                current_monitoring.save()
                return JsonResponse({
                    'status': 'success',
                    'monitoring': False,
                    'message': 'Chat monitoring disabled'
                })
            else:
                # Start new monitoring session
                ChatMonitoring.objects.create(user=request.user)
                return JsonResponse({
                    'status': 'success',
                    'monitoring': True,
                    'message': 'Chat monitoring enabled'
                })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

@login_required
def admin_chat_view(request):
    """View for admins to see monitored chats"""
    if not request.user.is_staff:
        return redirect('chat')
        
    # Get all monitored chat sessions
    monitored_sessions = ChatMonitoring.objects.all().order_by('-start_time')
    
    # Get chats for these sessions
    monitored_chats = {}
    for session in monitored_sessions:
        chats = ChatLog.objects.filter(
            monitoring_session=session
        ).order_by('timestamp')
        
        if chats.exists():
            monitored_chats[session] = [{
                'sender': chat.sender,
                'message': chat.message,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            } for chat in chats]
    
    return render(request, 'interagent/admin_chat.html', {
        'monitored_chats': monitored_chats
    })

def user_logout(request):
    """Handle user logout"""
    if request.user.is_authenticated:
        # End any active monitoring session
        from .models import ChatMonitoring
        active_monitoring = ChatMonitoring.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).last()
        if active_monitoring:
            active_monitoring.end_time = timezone.now()
            active_monitoring.save()
            
        # Clear session
        request.session.flush()
        logout(request)
        
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
