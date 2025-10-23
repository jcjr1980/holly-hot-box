"""
Celery Tasks for Async LLM Processing
This is the "brain" that processes complex queries in the background
"""
from celery import shared_task
import logging
import json
from .models import ChatSession, ChatMessage
from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_complex_query(self, prompt, session_id, history=None):
    """
    Background task that processes complex queries
    This is the BRAIN that:
    1. Analyzes the question
    2. Breaks into micro-tasks
    3. Processes each task
    4. Combines into final answer
    """
    try:
        logger.info(f"🧠 BRAIN: Processing complex query for session {session_id}")
        
        # Get session and project
        session = ChatSession.objects.get(id=session_id)
        project = session.project
        
        orchestrator = LLMOrchestrator()
        
        # Step 1: BRAIN analyzes the question
        logger.info("🔍 Step 1: Analyzing question complexity...")
        
        analysis_prompt = f"""Analyze this complex legal query and break it into 3-5 specific, focused sub-questions.
Each sub-question should be answerable independently in a single paragraph.

Original Query: {prompt}

Return a JSON array with objects containing:
- "id": number (1, 2, 3...)
- "question": the specific focused question
- "category": legal_analysis, research, tools, or strategy

Return ONLY valid JSON, nothing else."""
        
        analysis_response, _ = orchestrator.query_gemini(analysis_prompt, [])
        
        # Parse sub-questions
        import re
        json_match = re.search(r'\[.*\]', analysis_response, re.DOTALL)
        if json_match:
            sub_questions = json.loads(json_match.group())
            logger.info(f"✅ Created {len(sub_questions)} sub-questions")
        else:
            raise ValueError("Failed to break down query")
        
        # Step 2: BRAIN processes each micro-task
        logger.info("⚙️ Step 2: Processing micro-tasks...")
        
        micro_results = []
        for sq in sub_questions:
            logger.info(f"🔄 Processing: {sq['question'][:80]}...")
            
            # Build context for this specific question
            task_context = ""
            if project and project.summary:
                task_context = f"CASE CONTEXT: {project.summary[:400]}\n\n"
            
            task_prompt = f"{task_context}{sq['question']}"
            
            # Process this micro-task
            task_response, task_meta = orchestrator.query_gemini(task_prompt, [])
            
            micro_results.append({
                "id": sq['id'],
                "question": sq['question'],
                "answer": task_response,
                "category": sq.get('category', 'general')
            })
            
            logger.info(f"✅ Micro-task {sq['id']} completed")
        
        # Step 3: BRAIN combines micro-solutions into comprehensive answer
        logger.info("🎯 Step 3: Synthesizing final answer...")
        
        synthesis_prompt = f"""You are a legal AI assistant synthesizing a comprehensive response.

Original Complex Query: {prompt}

Individual Focused Answers:
{json.dumps(micro_results, indent=2)}

Create a comprehensive, well-structured final response that:
1. Addresses the original query completely
2. Integrates all the focused answers cohesively
3. Uses clear headings and formatting
4. Provides actionable recommendations
5. Is professional and thorough"""
        
        final_response, final_meta = orchestrator.query_gemini(synthesis_prompt, [])
        
        logger.info("✅ BRAIN: Final synthesis complete!")
        
        # Save the response to database
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=final_response,
            llm_provider='multi',
            tokens_used=final_meta.get('total_tokens', 0),
            response_time_ms=final_meta.get('total_response_time_ms', 0),
            metadata={
                "mode": "brain_processed",
                "micro_tasks": len(micro_results),
                "sub_questions": sub_questions
            }
        )
        
        session.save()
        
        return {
            "success": True,
            "response": final_response,
            "micro_tasks_completed": len(micro_results)
        }
        
    except Exception as e:
        logger.error(f"🔥 BRAIN FAILED: {e}")
        
        # Save error message
        try:
            session = ChatSession.objects.get(id=session_id)
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=f"I encountered an error processing your complex query. Please try breaking it into smaller questions. Error: {str(e)}",
                llm_provider='error'
            )
        except:
            pass
        
        return {
            "success": False,
            "error": str(e)
        }

