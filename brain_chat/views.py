"""
Holly Hot Box Views
Multi-LLM Chat Interface
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import pyotp
import os
import requests
from .models import ChatSession, ChatMessage, LLMResponse, UserProfile
from .llm_orchestrator import LLMOrchestrator


def get_client_country(request):
    """Get client country from IP address"""
    try:
        # Try to get IP from various headers
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Use a free IP geolocation service
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', '').upper()
    except:
        pass
    
    return 'UNKNOWN'

def is_blocked_country(country):
    """Check if country is in blocked list"""
    blocked_countries = [
        'INDIA', 'RUSSIA', 'CHINA', 'NORTH KOREA', 'IRAN', 'IRAQ', 'SYRIA',
        'AFGHANISTAN', 'PAKISTAN', 'BANGLADESH', 'SRI LANKA', 'NEPAL',
        'MYANMAR', 'THAILAND', 'VIETNAM', 'CAMBODIA', 'LAOS', 'MALAYSIA',
        'INDONESIA', 'PHILIPPINES', 'SINGAPORE', 'TAIWAN', 'HONG KONG',
        'MONGOLIA', 'KAZAKHSTAN', 'UZBEKISTAN', 'TURKMENISTAN', 'KYRGYZSTAN',
        'TAJIKISTAN', 'BELARUS', 'UKRAINE', 'MOLDOVA', 'GEORGIA', 'ARMENIA',
        'AZERBAIJAN', 'TURKEY', 'LEBANON', 'JORDAN', 'SAUDI ARABIA',
        'YEMEN', 'OMAN', 'UAE', 'KUWAIT', 'QATAR', 'BAHRAIN'
    ]
    return country in blocked_countries

def login_view(request):
    """Step 1: Username and Password only"""
    if request.user.is_authenticated:
        return redirect('chat_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check credentials
        expected_username = os.getenv('HBB_USERNAME', 'jcjr1980')
        expected_password = os.getenv('HBB_PASSWORD', '@cc0r-D69_8123$!')
        
        if username == expected_username and password == expected_password:
            # Store credentials in session for 2FA step
            request.session['temp_username'] = username
            request.session['temp_password'] = password
            return redirect('login_2fa')
        else:
            return render(request, 'brain_chat/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'brain_chat/login.html')

def login_2fa_view(request):
    """Step 2: 2FA Code with geo-blocking"""
    if request.user.is_authenticated:
        return redirect('chat_home')
    
    # Check if user has valid session from step 1
    if not request.session.get('temp_username'):
        return redirect('login')
    
    # Geo-blocking check - TEMPORARILY DISABLED
    # country = get_client_country(request)
    # if is_blocked_country(country):
    #     return HttpResponseForbidden(
    #         f"<h1>Access Denied</h1><p>Access from {country} is not permitted.</p>",
    #         content_type="text/html"
    #     )
    
    if request.method == 'POST':
        code = request.POST.get('code')
        expected_code = os.getenv('HBB_2FA_CODE', '267769')
        
        if code == expected_code:
            username = request.session['temp_username']
            password = request.session['temp_password']
            
            # Get or create user
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                UserProfile.objects.create(user=user)
            
            # Clear temporary session data
            request.session.pop('temp_username', None)
            request.session.pop('temp_password', None)
            
            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('chat_home')
        else:
            return render(request, 'brain_chat/login_2fa.html', {
                'error': 'Invalid 2FA code'
            })
    
    return render(request, 'brain_chat/login_2fa.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


@login_required
def chat_home(request):
    """Main chat interface"""
    # Get or create active session
    active_session = ChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if not active_session:
        active_session = ChatSession.objects.create(
            user=request.user,
            title="New Chat Session"
        )
    
    # Get all user's sessions
    sessions = ChatSession.objects.filter(user=request.user)
    
    # Get messages for active session
    messages = active_session.messages.all() if active_session else []
    
    return render(request, 'brain_chat/chat.html', {
        'active_session': active_session,
        'sessions': sessions,
        'messages': messages
    })


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Send a message and get LLM response"""
    try:
        data = json.loads(request.body)
        prompt = data.get('message', '').strip()
        mode = data.get('mode', 'consensus')  # consensus, fastest, best, parallel, gemini_only, deepseek_only, power_duo
        session_id = data.get('session_id')
        
        if not prompt:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=prompt[:50]  # Use first 50 chars as title
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=prompt
        )
        
        # Get conversation history
        history = []
        for msg in session.messages.filter(role__in=['user', 'assistant']).order_by('created_at'):
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Orchestrate LLM response
        orchestrator = LLMOrchestrator()
        result = orchestrator.orchestrate_response(prompt, history[:-1], mode=mode)
        
        # Save assistant response
        if mode == 'parallel':
            # Save all responses
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=json.dumps(result['results'], indent=2),
                llm_provider='multi',
                metadata=result
            )
            
            # Save individual LLM responses
            for llm_name, llm_data in result['results'].items():
                LLMResponse.objects.create(
                    message=assistant_message,
                    llm_provider=llm_name,
                    response_text=llm_data['response'],
                    tokens_used=llm_data['metadata'].get('tokens', 0),
                    response_time_ms=llm_data['metadata'].get('response_time_ms', 0),
                    metadata=llm_data['metadata']
                )
        
        elif mode == 'consensus':
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=result['final_response'],
                llm_provider='multi',
                metadata=result,
                tokens_used=result['metadata'].get('tokens', 0),
                response_time_ms=result['metadata'].get('response_time_ms', 0)
            )
            
            # Save individual responses
            for llm_name, llm_data in result['individual_responses'].items():
                LLMResponse.objects.create(
                    message=assistant_message,
                    llm_provider=llm_name,
                    response_text=llm_data['response'],
                    tokens_used=llm_data['metadata'].get('tokens', 0),
                    response_time_ms=llm_data['metadata'].get('response_time_ms', 0),
                    metadata=llm_data['metadata']
                )
        
        else:  # fastest or best
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=result['response'],
                llm_provider=result['provider'],
                metadata=result,
                tokens_used=result['metadata'].get('tokens', 0),
                response_time_ms=result['metadata'].get('response_time_ms', 0)
            )
        
        # Update session timestamp
        session.save()
        
        return JsonResponse({
            'success': True,
            'message_id': assistant_message.id,
            'response': assistant_message.content,
            'mode': mode,
            'session_id': session.id,
            'metadata': result
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def new_session(request):
    """Create a new chat session"""
    session = ChatSession.objects.create(
        user=request.user,
        title="New Chat Session"
    )
    return redirect('chat_home')


@login_required
def load_session(request, session_id):
    """Load a specific chat session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    # Set all sessions to inactive
    ChatSession.objects.filter(user=request.user).update(is_active=False)
    
    # Set this session as active
    session.is_active = True
    session.save()
    
    return redirect('chat_home')


@login_required
def get_session_messages(request, session_id):
    """Get messages for a specific session (AJAX)"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = session.messages.all()
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'llm_provider': msg.llm_provider,
            'created_at': msg.created_at.isoformat(),
            'tokens_used': msg.tokens_used,
            'response_time_ms': msg.response_time_ms
        })
    
    return JsonResponse({'messages': data})


def health_check(request):
    """Health check endpoint with auto-migration and shared DB test"""
    try:
        from django.core.management import execute_from_command_line
        from django.db import connection
        from django.conf import settings
        from .shared_db_utils import get_shared_db_connection, query_shared_database
        
        # Test HBB database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check if auth_user table exists in HBB database
        table_exists = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                table_exists = True
        except Exception:
            table_exists = False
        
        # Run migrations if tables don't exist
        if not table_exists:
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Test shared database connection
        shared_db_status = "connected"
        shared_tables = []
        try:
            shared_conn = get_shared_db_connection()
            if shared_conn:
                # Get list of tables from shared database
                result = query_shared_database("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                shared_tables = [row['table_name'] for row in result] if result else []
                shared_conn.close()
            else:
                shared_db_status = "failed"
        except Exception as e:
            shared_db_status = f"error: {str(e)}"
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'Holly Hot Box',
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'hbb_database': settings.DATABASES['default']['ENGINE'],
            'hbb_table_exists': table_exists,
            'migrations': 'completed' if table_exists else 'running',
            'shared_db_status': shared_db_status,
            'shared_tables_count': len(shared_tables),
            'shared_tables_sample': shared_tables[:5]  # First 5 tables
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'service': 'Holly Hot Box',
            'error': str(e)
        }, status=500)

def setup_database(request):
    """Temporary endpoint to setup database - REMOVE AFTER USE"""
    try:
        from django.core.management import execute_from_command_line
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Database setup completed successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Database setup failed: {str(e)}'
        }, status=500)
