"""
Streaming Views for Real-Time Progress Updates
"""
import json
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage, Project
from .llm_orchestrator import LLMOrchestrator
from .bulletproof_conductor import BulletproofConductor

logger = logging.getLogger(__name__)


@login_required
def send_message_streaming(request):
    """
    Stream LLM response with real-time progress updates
    Uses Server-Sent Events (SSE) for live progress
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        prompt = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not prompt:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Get or create session
        session = ChatSession.objects.get(id=session_id, user=request.user)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content=prompt
        )
        
        # Get conversation history
        history = []
        for msg in session.messages.order_by('created_at')[:-1]:  # Exclude current message
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Get project context
        project = session.project if session.project else None
        
        # Initialize orchestrator and conductor
        orchestrator = LLMOrchestrator()
        conductor = BulletproofConductor(orchestrator, project=project)
        
        def event_stream():
            """Generator that yields Server-Sent Events"""
            try:
                # Stream progress updates
                for progress_update in conductor.conduct_streaming(prompt, history):
                    # Format as SSE
                    event_data = json.dumps(progress_update)
                    yield f"data: {event_data}\n\n"
                    
                    # If this is the final result, save it
                    if progress_update.get('status') == 'complete':
                        response_text = progress_update.get('response', '')
                        metadata = progress_update.get('metadata', {})
                        
                        # Save assistant response
                        ChatMessage.objects.create(
                            session=session,
                            role='assistant',
                            content=response_text,
                            llm_provider='multi',
                            tokens_used=metadata.get('total_tokens', 0),
                            response_time_ms=int(metadata.get('elapsed_seconds', 0) * 1000),
                            metadata=metadata
                        )
                        
                        # Update session
                        session.updated_at = ChatMessage.objects.filter(session=session).latest('created_at').created_at
                        session.save()
                
                # Send completion signal
                yield f"data: {json.dumps({'status': 'done'})}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_event = json.dumps({
                    'status': 'error',
                    'message': f'Error: {str(e)}'
                })
                yield f"data: {error_event}\n\n"
        
        # Return SSE response
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
        return response
        
    except Exception as e:
        logger.error(f"Streaming view error: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)

