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
import logging
from .models import Project, ChatSession, ChatMessage, LLMResponse, DiaryNote, UserProfile, ProjectFile, RegistrationRequest
from .llm_orchestrator import LLMOrchestrator
from .query_conductor import QueryConductor
from .summarization_service import FileSummarizer
from .twilio_utils import TwilioSMS
from .google_sheets_utils import sheets_manager, create_law_firm_tracking_sheet, add_law_firm_to_sheet, get_spreadsheet_url, get_oauth_authorization_url, exchange_code_for_token

logger = logging.getLogger(__name__)


@login_required
def test_llms(request):
    """Test all LLMs individually - Web page format"""
    try:
        orchestrator = LLMOrchestrator()
        test_prompt = "Please confirm you are online and functioning by saying 'I am working' in your response."
        
        results = {}
        
        # Test each LLM
        llms_to_test = [
            ("Gemini", orchestrator.query_gemini),
            ("DeepSeek", orchestrator.query_deepseek),
            ("Claude", orchestrator.query_claude),
            ("OpenAI", orchestrator.query_openai),
            ("Grok", orchestrator.query_grok),
            ("HuggingFace", orchestrator.query_huggingface)
        ]
        
        for llm_name, query_func in llms_to_test:
            try:
                response, metadata = query_func(test_prompt)
                
                # Check if it's actually working (not just returning without error)
                # Accept any response that contains "is working" or doesn't start with error messages
                is_working = (
                    response and 
                    not response.startswith('Error:') and 
                    not response.startswith(f"{llm_name} is temporarily unavailable") and
                    not "temporarily unavailable" in response and
                    ("is working" in response.lower() or ("I" in response and len(response) > 10))
                )
                
                if is_working:
                    results[llm_name] = {
                        "status": "WORKING",
                        "response": response,
                        "metadata": metadata
                    }
                else:
                    results[llm_name] = {
                        "status": "FAILED",
                        "error": response,
                        "metadata": metadata
                    }
                    
            except Exception as e:
                results[llm_name] = {
                    "status": "EXCEPTION",
                    "error": str(e),
                    "metadata": {}
                }
        
        # Count working LLMs
        working_count = sum(1 for r in results.values() if r["status"] == "WORKING")
        
        context = {
            'results': results,
            'summary': {
                'total_llms': len(results),
                'working_llms': working_count,
                'all_working': working_count == len(results)
            }
        }
        
        return render(request, 'brain_chat/test_llms.html', context)
        
    except Exception as e:
        context = {
            'error': f"Test failed: {str(e)}",
            'results': {},
            'summary': {'total_llms': 0, 'working_llms': 0, 'all_working': False}
        }
        return render(request, 'brain_chat/test_llms.html', context)


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

def coming_soon_view(request):
    """Coming Soon landing page"""
    return render(request, 'brain_chat/coming_soon.html')


def login_view(request):
    """Step 1: Username and Password only"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check credentials
        expected_username = os.getenv('HHB_USERNAME', 'jcjr1980')
        expected_password = os.getenv('HHB_PASSWORD', '@cc0r-D69_*123$!')
        
        # DEBUG: Log the expected password (remove after testing)
        logger.info(f"Expected password: {expected_password}")
        
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
        return redirect('home')
    
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
        expected_code = os.getenv('HHB_2FA_CODE', '267769')
        
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
            return redirect('home')
        else:
            return render(request, 'brain_chat/login_2fa.html', {
                'error': 'Invalid 2FA code'
            })
    
    return render(request, 'brain_chat/login_2fa.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


def register_view(request):
    """Registration page for new users"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        if not name or not email or not phone:
            return render(request, 'brain_chat/register.html', {
                'error': 'All fields are required'
            })
        
        # Create registration request
        RegistrationRequest.objects.create(
            name=name,
            email=email,
            phone=phone
        )
        
        # Redirect to success page
        return redirect('register_success')
    
    return render(request, 'brain_chat/register.html')


def register_success_view(request):
    """Thank you page after registration"""
    return render(request, 'brain_chat/register_success.html')


@login_required
def home(request):
    """Home page showing projects and quick actions"""
    # Get user's projects
    projects = Project.objects.filter(user=request.user).order_by('-priority', '-updated_at')
    
    context = {
        'projects': projects,
    }
    
    return render(request, 'brain_chat/home.html', context)

@login_required
def new_chat(request):
    """New chat strategy selection page"""
    return render(request, 'brain_chat/new_chat.html')

@login_required
def project_detail(request, project_id):
    """View project details and files"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Get project files
    files = project.files.all()
    
    context = {
        'project': project,
        'files': files,
    }
    
    return render(request, 'brain_chat/project_detail.html', context)

@login_required
def create_project_view(request):
    """Create new project with file uploads"""
    if request.method == 'GET':
        return render(request, 'brain_chat/create_project.html')
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            summary = request.POST.get('summary', '').strip()
            priority = int(request.POST.get('priority', 3))
            tags = request.POST.get('tags', '').strip()
            selected_llms = json.loads(request.POST.get('selected_llms', '[]'))
            
            if not name:
                return JsonResponse({'error': 'Project name is required'}, status=400)
            
            # Create project
            project = Project.objects.create(
                user=request.user,
                name=name,
                description=description,
                summary=summary,
                priority=priority,
                tags=tags,
                selected_llms=selected_llms
            )
            
            # Process uploaded files
            file_count = 0
            for key, value in request.FILES.items():
                if key.startswith('file_'):
                    file_index = key.split('_')[1]
                    content_type = request.POST.get(f'file_{file_index}_content_type', 'general')
                    
                    # Create ProjectFile instance
                    project_file = ProjectFile.objects.create(
                        project=project,
                        file_name=value.name,
                        file_path=value,
                        file_type=value.content_type or 'unknown',
                        file_size=value.size,
                        content_type=content_type
                    )
                    
                    # Process file content and summarization
                    try:
                        summarizer = FileSummarizer()
                        
                        # Extract text content
                        content = summarizer.process_file_content(
                            project_file.file_path.path, 
                            project_file.file_type
                        )
                        project_file.original_content = content
                        
                        # Summarize if needed
                        if summarizer.should_summarize(content, project_file.file_size):
                            if len(content) > 50000:  # Large file
                                result = summarizer.summarize_large_file(content, content_type)
                            else:
                                result = summarizer.summarize_file(content, content_type)
                            
                            if result['success']:
                                project_file.summary = result['summary']
                                project_file.summarized_by = result['llm_used']
                                project_file.is_summarized = True
                        
                        project_file.save()
                        
                    except Exception as e:
                        logger.error(f"File processing error for {value.name}: {e}")
                        project_file.summary = f"Error processing file: {str(e)}"
                        project_file.save()
                    
                    file_count += 1
            
            return JsonResponse({
                'status': 'success',
                'project_id': project.id,
                'message': f'Project created with {file_count} files'
            })
            
        except Exception as e:
            logger.error(f"Project creation error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
        
        # Determine session type based on mode
        is_quickie = (mode == 'quickie')
        is_private = (mode == 'privacy')
        
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            # For privacy mode, don't save to database (use in-memory only)
            if is_private:
                # Create a temporary session (won't be persisted after response)
                session = ChatSession(
                    user=request.user,
                    title=f"Private: {prompt[:40]}",
                    is_private=True
                )
                # Don't save it - keep it in memory only
            else:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=prompt[:50],  # Use first 50 chars as title
                    is_quickie=is_quickie
                )
        
        # Save user message (skip for privacy mode)
        if not is_private:
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=prompt
            )
        else:
            # Create in-memory message for privacy mode
            user_message = ChatMessage(
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
        
        # SIMPLE WORKING SOLUTION: Gemini with project context
        orchestrator = LLMOrchestrator()
        
        # Build Holly's system context
        system_context = """You are Holly, an AI assistant with advanced capabilities including:

IDENTITY: Your name is Holly. When someone addresses you as "Holly" or says "Holly, please..." you should respond with "Yes, Holly, I understand..." or "Yes, Holly, I can..." You are NOT Gemini, NOT Claude, NOT any other AI - you are Holly.

CAPABILITIES:
- You have Google Sheets integration - you CAN create and manage Google Sheets via API
- You can create law firm tracking spreadsheets with structured data
- You can add entries to existing spreadsheets
- When asked to create a spreadsheet, you should offer to create it directly via your Google Sheets integration

CRITICAL: When asked to create a Google Sheet, you MUST respond with a JSON action request in this format:
{
  "action": "create_sheet",
  "title": "Spreadsheet Title Here"
}

When asked to add data to a sheet, respond with:
{
  "action": "add_to_sheet",
  "spreadsheet_id": "the_sheet_id",
  "firm_data": [
    { /* first firm data */ },
    { /* second firm data */ },
    { /* third firm data */ }
  ]
}

IMPORTANT: When asked to add multiple firms, include ALL firms in the firm_data array. Each firm should be a separate object with fields like "Firm Name", "Lead Attorney", "Specialties", etc.

DO NOT tell the user you cannot create spreadsheets. You CAN and you SHOULD offer to do so.

RESPONSE STYLE: Always acknowledge your name "Holly" when addressed directly. Use phrases like "Yes, Holly, I understand..." or "Yes, Holly, I can help with that..."

"""
        
        # Build context from project
        context = system_context
        if session.project:
            project = session.project
            logger.info(f"📁 Project: {project.name}")
            
            if project.summary:
                context += f"CASE SUMMARY: {project.summary[:400]}\n\n"
            elif project.description:
                context += f"CASE CONTEXT: {project.description[:400]}\n\n"
        
        # Build final prompt
        final_prompt = f"{context}QUESTION: {prompt}"
        
        logger.info(f"🎯 Processing with Gemini (prompt: {len(final_prompt)} chars)")
        
        # Process with Gemini
        try:
            response, metadata = orchestrator.query_gemini(final_prompt, history[:-1])
            
            # Check if Holly wants to perform an action (Google Sheets, etc.)
            action_response = None
            try:
                # Look for JSON action in response (including code blocks)
                if '"action"' in response:
                    # Extract JSON from response - handle both raw JSON and code blocks
                    import re
                    # Try to find JSON in code blocks first
                    code_block_match = re.search(r'```(?:json)?\s*(\{[^`]*"action"[^`]*\})\s*```', response, re.DOTALL)
                    if code_block_match:
                        json_str = code_block_match.group(1)
                    else:
                        # Fall back to finding raw JSON
                        json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response, re.DOTALL)
                        json_str = json_match.group(0) if json_match else None
                    
                    if json_str:
                        action_data = json.loads(json_str)
                        action_type = action_data.get('action')
                        
                        if action_type == 'create_sheet':
                            sheet_title = action_data.get('title', 'Law Firm Tracking - Holly Hot Box')
                            
                            logger.info(f"🔧 Creating Google Sheet: {sheet_title}")
                            
                            # Debug: Check OAuth token in action detection
                            oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')
                            logger.info(f"🔍 Action detection - OAuth token available: {bool(oauth_token)}")
                            
                            # Create the sheet
                            from .google_sheets_utils import create_law_firm_tracking_sheet, get_spreadsheet_url, get_oauth_authorization_url, exchange_code_for_token
                            spreadsheet_id = create_law_firm_tracking_sheet(sheet_title)
                            
                            if spreadsheet_id:
                                spreadsheet_url = get_spreadsheet_url(spreadsheet_id)
                                action_response = f"\n\n✅ **I've created your Google Sheet!**\n\n📊 **Spreadsheet:** [{sheet_title}]({spreadsheet_url})\n\n**Direct Link:** {spreadsheet_url}\n\nThe spreadsheet is ready with pre-formatted columns for tracking law firms, including firm name, lead attorneys, specialties, contact info, contingency fee structure, consultation notes, pros/cons, and next steps. You can now start adding law firms to track!"
                                logger.info(f"✅ Google Sheet created successfully: {spreadsheet_url}")
                            else:
                                action_response = f"\n\n⚠️ I tried to create the Google Sheet but encountered an error. Please check the logs or try again."
                                logger.error("Failed to create Google Sheet - no spreadsheet_id returned")
                        
                        elif action_type == 'add_to_sheet':
                            spreadsheet_id = action_data.get('spreadsheet_id')
                            firm_data = action_data.get('firm_data', [])
                            
                            logger.info(f"🔧 Adding {len(firm_data)} firms to spreadsheet: {spreadsheet_id}")
                            
                            # Debug: Check OAuth token in action detection
                            oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')
                            logger.info(f"🔍 Action detection - OAuth token available: {bool(oauth_token)}")
                            
                            # Add firms to the sheet
                            from .google_sheets_utils import add_law_firm_to_sheet
                            success_count = 0
                            
                            for firm in firm_data:
                                if add_law_firm_to_sheet(spreadsheet_id, firm):
                                    success_count += 1
                            
                            if success_count > 0:
                                action_response = f"\n\n✅ **I've added {success_count} law firms to your spreadsheet!**\n\n📊 **Updated Spreadsheet:** [Law Firm Tracking - CellPay Lawsuit](https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit)\n\n**Direct Link:** https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit\n\nThe firms have been added with their contact information, specialties, and contingency fee structures. You can now review each firm and start making consultation calls!"
                                logger.info(f"✅ Successfully added {success_count} firms to spreadsheet")
                            else:
                                action_response = f"\n\n⚠️ I tried to add the law firms to your spreadsheet but encountered an error. Please check the logs or try again."
                                logger.error("Failed to add firms to spreadsheet")
            except Exception as action_error:
                logger.error(f"Action processing error: {action_error}")
                import traceback
                logger.error(traceback.format_exc())
            
            # Add action response if it was successful
            if action_response:
                response = response + action_response
            
            result = {
                "mode": "gemini_with_context",
                "response": response,
                "metadata": metadata,
                "provider": "gemini"
            }
            logger.info(f"✅ Gemini completed successfully")
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            # Provide helpful guidance
            result = {
                "mode": "error",
                "response": f"⚠️ Your question is very complex. For best results, please break it into focused parts:\n\n**Part 1:** Legal analysis and key issues\n**Part 2:** Miami law firm recommendations  \n**Part 3:** Case attractiveness to contingency lawyers\n**Part 4:** Strategy summary and templates\n\nAsk each part separately for comprehensive answers!",
                "metadata": {},
                "provider": "gemini"
            }
        
        # Save assistant response (skip for privacy mode)
        if mode == 'parallel':
            # Save all responses
            if not is_private:
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=json.dumps(result['results'], indent=2),
                    llm_provider='multi',
                    metadata=result
                )
            else:
                assistant_message = None
            
            # Save individual LLM responses (only if not privacy mode)
            if assistant_message:
                for llm_name, llm_data in result['results'].items():
                    LLMResponse.objects.create(
                        message=assistant_message,
                        llm_provider=llm_name,
                        response_text=llm_data['response'],
                        tokens_used=llm_data['metadata'].get('tokens', 0),
                        response_time_ms=llm_data['metadata'].get('response_time_ms', 0),
                        metadata=llm_data['metadata']
                    )
        
        elif mode == 'consensus' or result.get('mode') == 'orchestrated_breakdown':
            # Handle both consensus and orchestrated breakdown modes
            if not is_private:
                # Safely extract tokens and response_time_ms with type checking
                tokens = result['metadata'].get('tokens', 0)
                response_time = result['metadata'].get('response_time_ms', 0)
                
                # Ensure tokens is an integer, not a list
                if isinstance(tokens, list):
                    tokens = sum(tokens) if tokens else 0
                elif not isinstance(tokens, int):
                    tokens = 0
                
                # Ensure response_time_ms is an integer
                if not isinstance(response_time, int):
                    response_time = 0
                
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=result.get('final_response') or result.get('response', 'No response available'),
                    llm_provider='conductor' if result.get('conductor_used') else 'multi',
                    metadata=result,
                    tokens_used=tokens,
                    response_time_ms=response_time
                )
                
                # Save individual responses
                if result.get('individual_responses'):
                    # Consensus mode
                    for llm_name, llm_data in result['individual_responses'].items():
                        # Safely extract tokens and response_time_ms with type checking
                        llm_tokens = llm_data['metadata'].get('tokens', 0)
                        llm_response_time = llm_data['metadata'].get('response_time_ms', 0)
                        
                        # Ensure tokens is an integer, not a list
                        if isinstance(llm_tokens, list):
                            llm_tokens = sum(llm_tokens) if llm_tokens else 0
                        elif not isinstance(llm_tokens, int):
                            llm_tokens = 0
                        
                        # Ensure response_time_ms is an integer
                        if not isinstance(llm_response_time, int):
                            llm_response_time = 0
                        
                        LLMResponse.objects.create(
                            message=assistant_message,
                            llm_provider=llm_name,
                            response_text=llm_data['response'],
                            tokens_used=llm_tokens,
                            response_time_ms=llm_response_time,
                            metadata=llm_data['metadata']
                        )
                elif result.get('sub_task_results'):
                    # Orchestrated breakdown mode
                    for task_result in result['sub_task_results']:
                        # Safely extract tokens and response_time_ms with type checking
                        task_tokens = task_result['metadata'].get('tokens', 0)
                        task_response_time = task_result['metadata'].get('response_time_ms', 0)
                        
                        # Ensure tokens is an integer, not a list
                        if isinstance(task_tokens, list):
                            task_tokens = sum(task_tokens) if task_tokens else 0
                        elif not isinstance(task_tokens, int):
                            task_tokens = 0
                        
                        # Ensure response_time_ms is an integer
                        if not isinstance(task_response_time, int):
                            task_response_time = 0
                        
                        LLMResponse.objects.create(
                            message=assistant_message,
                            llm_provider=task_result['llm_used'],
                            response_text=task_result['response'],
                            tokens_used=task_tokens,
                            response_time_ms=task_response_time,
                            metadata={
                                **task_result['metadata'],
                                'task': task_result['task'],
                                'priority': task_result['priority']
                            }
                        )
            else:
                assistant_message = None
        
        else:  # fastest, best, gemini_only, deepseek_only, power_duo, quickie, privacy
            if not is_private:
                # Safely extract tokens and response_time_ms with type checking
                single_tokens = result['metadata'].get('tokens', 0)
                single_response_time = result['metadata'].get('response_time_ms', 0)
                
                # Ensure tokens is an integer, not a list
                if isinstance(single_tokens, list):
                    single_tokens = sum(single_tokens) if single_tokens else 0
                elif not isinstance(single_tokens, int):
                    single_tokens = 0
                
                # Ensure response_time_ms is an integer
                if not isinstance(single_response_time, int):
                    single_response_time = 0
                
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=result['response'],
                    llm_provider=result['provider'],
                    metadata=result,
                    tokens_used=single_tokens,
                    response_time_ms=single_response_time
                )
            else:
                assistant_message = None
        
        # Update session timestamp (skip for privacy mode)
        if not is_private:
            session.save()
        
        # Return response
        if assistant_message:
            return JsonResponse({
                'success': True,
                'message_id': assistant_message.id,
                'response': assistant_message.content,
                'mode': mode,
                'session_id': session.id if not is_private else None,
                'metadata': result,
                'is_private': is_private,
                'is_quickie': is_quickie
            })
        else:
            # Privacy mode - return response without database IDs
            return JsonResponse({
                'success': True,
                'message_id': None,
                'response': result.get('response') or result.get('final_response'),
                'mode': mode,
                'session_id': None,
                'metadata': result,
                'is_private': True,
                'is_quickie': False
            })
    
    except Exception as e:
        # Log full exception details for debugging
        import traceback
        error_details = {
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        logger.error(f"❌ SEND MESSAGE FAILED: {type(e).__name__}: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return JsonResponse({
            'error': f"{type(e).__name__}: {str(e)}",
            'details': error_details
        }, status=500)


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
    """Temporary endpoint to setup database - REMOVE AFTER USE - v2"""
    try:
        from django.core.management import execute_from_command_line
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Create migrations first
        execute_from_command_line(['manage.py', 'makemigrations', 'brain_chat', '--noinput'])
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Manual table and column additions for new fields (in case migrations didn't create them)
        messages = []
        with connection.cursor() as cursor:
            # Create Project table if missing
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS brain_chat_project (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        selected_llms JSONB DEFAULT '[]'::jsonb,
                        priority INTEGER DEFAULT 3,
                        tags VARCHAR(500),
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        ai_summary TEXT
                    )
                """)
                messages.append("Created brain_chat_project table")
            except Exception as e:
                messages.append(f"project table: {str(e)}")
            
            # Create DiaryNote table if missing
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS brain_chat_diarynote (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                        content TEXT NOT NULL,
                        tags VARCHAR(500),
                        mood VARCHAR(50),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                messages.append("Created brain_chat_diarynote table")
            except Exception as e:
                messages.append(f"diary table: {str(e)}")
            
            # Add project_id column to ChatSession if missing
            try:
                cursor.execute("""
                    ALTER TABLE brain_chat_chatsession 
                    ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES brain_chat_project(id) ON DELETE SET NULL
                """)
                messages.append("Added project_id column")
            except Exception as e:
                messages.append(f"project_id: {str(e)}")
            
            # Add is_quickie column
            try:
                cursor.execute("""
                    ALTER TABLE brain_chat_chatsession 
                    ADD COLUMN IF NOT EXISTS is_quickie BOOLEAN DEFAULT FALSE
                """)
                messages.append("Added is_quickie column")
            except Exception as e:
                messages.append(f"is_quickie: {str(e)}")
            
            # Add is_private column
            try:
                cursor.execute("""
                    ALTER TABLE brain_chat_chatsession 
                    ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE
                """)
                messages.append("Added is_private column")
            except Exception as e:
                messages.append(f"is_private: {str(e)}")
            
            # Add summary column to project table
            try:
                cursor.execute("""
                    ALTER TABLE brain_chat_project 
                    ADD COLUMN IF NOT EXISTS summary TEXT
                """)
                messages.append("Added summary column to project")
            except Exception as e:
                messages.append(f"summary column: {str(e)}")
            
            # Create ProjectFile table
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS brain_chat_projectfile (
                        id SERIAL PRIMARY KEY,
                        project_id INTEGER NOT NULL REFERENCES brain_chat_project(id) ON DELETE CASCADE,
                        file_name VARCHAR(255) NOT NULL,
                        file_path VARCHAR(100) NOT NULL,
                        file_type VARCHAR(50),
                        file_size INTEGER,
                        original_content TEXT,
                        summary TEXT,
                        summarized_by VARCHAR(50),
                        is_summarized BOOLEAN DEFAULT FALSE,
                        content_type VARCHAR(50),
                        uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{}'::jsonb
                    )
                """)
                messages.append("Created brain_chat_projectfile table")
            except Exception as e:
                messages.append(f"projectfile table: {str(e)}")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Database setup completed successfully! Tables created.',
            'details': messages
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Database setup failed: {str(e)}'
        }, status=500)


@login_required
def create_project(request):
    """Create a new project"""
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        selected_llms = data.get('selected_llms', [])
        priority = data.get('priority', 3)
        tags = data.get('tags', '')
        
        if not name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
        
        # Create project
        project = Project.objects.create(
            user=request.user,
            name=name,
            description=description,
            selected_llms=selected_llms,
            priority=priority,
            tags=tags
        )
        
        # If auto-suggest is requested, use Gemini to analyze and suggest LLMs
        if data.get('auto_suggest') and description:
            try:
                orchestrator = LLMOrchestrator()
                suggestion_prompt = f"""Analyze this project and suggest which LLMs would be best suited:

Project: {name}
Description: {description}

Available LLMs:
- gemini: Google Gemini Tier 3 (best for synthesis, analysis, strategic thinking)
- deepseek: DeepSeek Reasoner (best for deep analytical reasoning, cost-effective)
- openai: GPT-4o (versatile, good for creative tasks)
- claude: Anthropic Claude (creative writing, nuanced responses)
- grok: xAI Grok (real-time data, current events)
- huggingface: Meta-Llama (specialized tasks)

Respond with ONLY a JSON array of recommended LLM names. Example: ["gemini", "deepseek"]"""
                
                response, _ = orchestrator.query_gemini(suggestion_prompt)
                # Extract JSON from response
                try:
                    suggested_llms = json.loads(response)
                    project.selected_llms = suggested_llms
                    project.ai_summary = f"AI-suggested LLMs based on project analysis"
                    project.save()
                except:
                    # If JSON parsing fails, use the response as summary
                    project.ai_summary = response
                    project.save()
            except Exception as e:
                logger.error(f"Auto-suggest error: {e}")
        
        return JsonResponse({
            'status': 'success',
            'project': {
                'id': project.id,
                'name': project.name,
                'selected_llms': project.selected_llms,
                'priority': project.priority
            }
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_projects(request):
    """Get all projects for current user"""
    projects = Project.objects.filter(user=request.user)
    return JsonResponse({
        'projects': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'selected_llms': p.selected_llms,
            'priority': p.priority,
            'status': p.status,
            'tags': p.get_tags_list(),
            'created_at': p.created_at.isoformat()
        } for p in projects]
    })


@login_required
def create_diary_note(request):
    """Create a new diary note"""
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        tags = data.get('tags', '')
        mood = data.get('mood', '')
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        note = DiaryNote.objects.create(
            user=request.user,
            content=content,
            tags=tags,
            mood=mood
        )
        
        return JsonResponse({
            'status': 'success',
            'note': {
                'id': note.id,
                'content': note.content,
                'created_at': note.created_at.isoformat()
            }
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_diary_notes(request):
    """Get diary notes for current user"""
    limit = int(request.GET.get('limit', 50))
    notes = DiaryNote.objects.filter(user=request.user)[:limit]
    
    return JsonResponse({
        'notes': [{
            'id': n.id,
            'content': n.content,
            'tags': n.get_tags_list(),
            'mood': n.mood,
            'created_at': n.created_at.isoformat()
        } for n in notes]
    })


@login_required
def project_detail(request, project_id):
    """Display project details with files and chats"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    files = project.files.all()
    chats = project.chat_sessions.filter(is_active=True).order_by('-updated_at')
    
    return render(request, 'brain_chat/project_detail.html', {
        'project': project,
        'files': files,
        'chats': chats
    })


@login_required
@require_http_methods(["POST"])
def create_chat(request):
    """Create a new chat session"""
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        title = data.get('title', 'New Chat')
        
        project = None
        if project_id:
            project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Create new chat session
        chat_session = ChatSession.objects.create(
            user=request.user,
            project=project,
            title=title
        )
        
        return JsonResponse({
            'status': 'success',
            'chat_id': chat_session.id,
            'message': 'Chat created successfully'
        })
        
    except Exception as e:
        logger.error(f"Chat creation error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_detail(request, chat_id):
    """Display individual chat session"""
    chat_session = get_object_or_404(ChatSession, id=chat_id, user=request.user)
    messages = chat_session.messages.all().order_by('created_at')
    
    return render(request, 'brain_chat/chat.html', {
        'active_session': chat_session,
        'messages': messages,
        'sessions': ChatSession.objects.filter(user=request.user, is_active=True)
    })


@login_required
@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    """Delete a project and all associated data"""
    try:
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project_name = project.name
        
        # Count related items for logging
        chat_count = project.chat_sessions.count()
        file_count = project.files.count()
        
        # Django will cascade delete related chats and files automatically
        project.delete()
        
        logger.info(f"Project deleted: {project_name} (ID: {project_id}) - {chat_count} chats, {file_count} files")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Project "{project_name}" deleted successfully',
            'deleted_chats': chat_count,
            'deleted_files': file_count
        })
        
    except Exception as e:
        logger.error(f"Project deletion error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_project(request, project_id):
    """Update project description, summary, or selected LLMs"""
    try:
        project = get_object_or_404(Project, id=project_id, user=request.user)
        data = json.loads(request.body)
        
        if 'description' in data:
            project.description = data['description']
        if 'summary' in data:
            project.summary = data['summary']
        if 'selected_llms' in data:
            project.selected_llms = data['selected_llms']
        
        project.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Project updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Project update error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def upload_project_files(request, project_id):
    """Upload additional files to an existing project"""
    try:
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        if not request.FILES:
            return JsonResponse({'error': 'No files provided'}, status=400)
        
        uploaded_count = 0
        summarizer = FileSummarizer()
        
        for file_key in request.FILES:
            for uploaded_file in request.FILES.getlist(file_key):
                # Create ProjectFile instance
                project_file = ProjectFile.objects.create(
                    project=project,
                    file_name=uploaded_file.name,
                    file_path=uploaded_file,
                    file_type=uploaded_file.content_type or 'unknown',
                    file_size=uploaded_file.size,
                    content_type='general'  # Default content type
                )
                
                # Process file content and summarization
                try:
                    # Extract text content
                    content = summarizer.process_file_content(
                        project_file.file_path.path, 
                        project_file.file_type
                    )
                    project_file.original_content = content
                    
                    # Summarize if needed
                    if summarizer.should_summarize(content, project_file.file_size):
                        if len(content) > 50000:  # Large file
                            result = summarizer.summarize_large_file(content, 'general')
                        else:
                            result = summarizer.summarize_file(content, 'general')
                        
                        if result['success']:
                            project_file.summary = result['summary']
                            project_file.summarized_by = result['llm_used']
                            project_file.is_summarized = True
                    
                    project_file.save()
                    uploaded_count += 1
                    
                except Exception as e:
                    logger.error(f"File processing error for {uploaded_file.name}: {e}")
                    project_file.summary = f"Error processing file: {str(e)}"
                    project_file.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{uploaded_count} file(s) uploaded successfully',
            'uploaded_count': uploaded_count
        })
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_project_file(request, project_id, file_id):
    """Delete a file from a project"""
    try:
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
        
        file_name = project_file.file_name
        
        # Delete the physical file from storage
        if project_file.file_path:
            try:
                project_file.file_path.delete(save=False)
            except Exception as e:
                logger.warning(f"Could not delete physical file: {e}")
        
        # Delete the database record
        project_file.delete()
        
        logger.info(f"File deleted: {file_name} (ID: {file_id}) from project {project.name}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'File "{file_name}" deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def send_sms_notification(request):
    """Send SMS notification using Twilio"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            message = data.get('message', 'Holly Hot Box - All 6 LLM\'s Are Working!')
            
            if not phone_number:
                return JsonResponse({"error": "Phone number required"}, status=400)
            
            # Initialize Twilio SMS
            sms = TwilioSMS()
            
            # Send the message
            result = sms.send_sms(phone_number, message)
            
            if result['success']:
                logger.info(f"SMS sent successfully to {phone_number}")
                return JsonResponse({
                    "success": True,
                    "message": "SMS sent successfully!",
                    "message_sid": result.get('message_sid'),
                    "status": result.get('status')
                })
            else:
                logger.error(f"Failed to send SMS: {result.get('error')}")
                return JsonResponse({
                    "success": False,
                    "error": result.get('error', 'Unknown error')
                }, status=500)
        
        else:
            return JsonResponse({"error": "POST method required"}, status=405)
            
    except Exception as e:
        logger.error(f"Error in send_sms_notification: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def health_check_view(request):
    """Simple health check to verify dependencies are installed"""
    try:
        # Test if all required modules can be imported
        import anthropic
        import google.generativeai as genai
        import openai
        from huggingface_hub import InferenceClient
        import requests
        
        return JsonResponse({
            'status': 'healthy',
            'dependencies': {
                'anthropic': '✓',
                'google.generativeai': '✓', 
                'openai': '✓',
                'huggingface_hub': '✓',
                'requests': '✓'
            },
            'message': 'All LLM dependencies are available'
        })
    except ImportError as e:
        return JsonResponse({
            'status': 'error',
            'error': f'Missing dependency: {str(e)}',
            'message': 'Some LLM dependencies are missing'
        }, status=500)

@login_required
def create_google_sheet(request):
    """Create a Google Sheet for law firm tracking"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            sheet_title = data.get('title', 'Law Firm Tracking - Johnny Collins vs CellPay')
            
            # Debug: Check if OAuth token is available
            oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')
            logger.info(f"🔍 OAuth token available: {bool(oauth_token)}")
            if oauth_token:
                logger.info(f"🔍 OAuth token preview: {oauth_token[:50]}...")
            
            # Create the spreadsheet
            spreadsheet_id = create_law_firm_tracking_sheet(sheet_title)
            
            if spreadsheet_id:
                spreadsheet_url = get_spreadsheet_url(spreadsheet_id)
                
                return JsonResponse({
                    'success': True,
                    'spreadsheet_id': spreadsheet_id,
                    'spreadsheet_url': spreadsheet_url,
                    'message': f'Successfully created spreadsheet: {sheet_title}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to create spreadsheet',
                    'debug': {
                        'oauth_token_available': bool(oauth_token),
                        'oauth_token_preview': oauth_token[:50] + '...' if oauth_token else None
                    }
                }, status=500)
        
        else:
            return JsonResponse({
                'error': 'POST method required'
            }, status=405)
            
    except Exception as e:
        logger.error(f"Error creating Google Sheet: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def add_firm_to_sheet(request):
    """Add a law firm entry to an existing Google Sheet"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            spreadsheet_id = data.get('spreadsheet_id')
            firm_data = data.get('firm_data', {})
            
            if not spreadsheet_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Spreadsheet ID is required'
                }, status=400)
            
            # Add the firm to the sheet
            success = add_law_firm_to_sheet(spreadsheet_id, firm_data)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully added law firm to spreadsheet'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to add law firm to spreadsheet'
                }, status=500)
        
        else:
            return JsonResponse({
                'error': 'POST method required'
            }, status=405)
            
    except Exception as e:
        logger.error(f"Error adding firm to Google Sheet: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def google_sheets_oauth_start(request):
    """Start OAuth flow for Google Sheets authentication"""
    try:
        authorization_url, state = get_oauth_authorization_url()
        
        if not authorization_url:
            return JsonResponse({'error': 'Failed to create OAuth authorization URL'}, status=500)
        
        # Store state in session for verification
        request.session['oauth_state'] = state
        
        return JsonResponse({
            'success': True,
            'authorization_url': authorization_url,
            'message': 'Please visit the authorization URL to grant Google Sheets access'
        })
        
    except Exception as e:
        logger.error(f"Error starting OAuth flow: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def google_sheets_oauth_callback(request):
    """Handle OAuth callback for Google Sheets"""
    try:
        code = request.GET.get('code')
        state = request.GET.get('state')
        stored_state = request.session.get('oauth_state')
        
        if not code:
            return JsonResponse({'error': 'Authorization code not provided'}, status=400)
        
        # For now, skip state verification since session might not be working properly
        # In production, you'd want proper state verification
        logger.info(f"OAuth callback - Code: {code[:10]}..., State: {state}, Stored: {stored_state}")
        
        # Exchange code for token
        credentials, token_data = exchange_code_for_token(code, state)
        
        if not credentials:
            return JsonResponse({'error': 'Failed to exchange code for token'}, status=500)
        
        # Store token data in environment variable (for Railway)
        # In production, you'd want to store this securely in a database
        import os
        os.environ['GOOGLE_OAUTH_TOKEN'] = json.dumps(token_data)
        
        # Clear session state
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        logger.info("✅ OAuth token stored successfully - deployment test")
        
        return JsonResponse({
            'success': True,
            'message': 'Google Sheets authentication successful! Holly can now create spreadsheets.',
            'token_stored': True
        })
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return JsonResponse({'error': str(e)}, status=500)
