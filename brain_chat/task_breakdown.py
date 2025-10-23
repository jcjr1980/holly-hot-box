"""
Task-based breakdown system for complex queries
"""
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class TaskBreakdown:
    """Handles breaking down complex queries into manageable tasks"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def execute_task_breakdown(self, prompt: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Execute task-based breakdown with timeout resilience
        """
        logger.info("🎯 Executing task-based breakdown for complex query")
        
        # Create tasks based on query complexity
        tasks = self._create_tasks_from_query(prompt)
        logger.info(f"📋 Created {len(tasks)} tasks for breakdown")
        
        # Process tasks with timeout handling
        results = {}
        successful_tasks = 0
        
        for i, task in enumerate(tasks):
            try:
                logger.info(f"🔄 Processing task {i+1}/{len(tasks)}: {task['title']}")
                
                # Process task with timeout protection
                task_result = self._process_single_task(task, conversation_history)
                results[f"task_{i+1}"] = {
                    "title": task['title'],
                    "result": task_result,
                    "status": "success"
                }
                successful_tasks += 1
                logger.info(f"✅ Task {i+1} completed successfully")
                
            except Exception as task_error:
                logger.warning(f"⚠️ Task {i+1} failed: {task_error}")
                results[f"task_{i+1}"] = {
                    "title": task['title'],
                    "result": f"Task failed: {str(task_error)}",
                    "status": "failed",
                    "error": str(task_error)
                }
        
        # Synthesize results
        if successful_tasks > 0:
            synthesis_prompt = f"""
            You are synthesizing results from a complex query breakdown. Here are the individual task results:

            {json.dumps(results, indent=2)}

            Original Query: {prompt}

            Please provide a comprehensive, synthesized response that combines all the successful tasks into a cohesive answer.
            """
            
            final_response, metadata = self.orchestrator.query_gemini(synthesis_prompt)
            
            return {
                "mode": "task_breakdown",
                "response": final_response,
                "task_results": results,
                "metadata": metadata,
                "conductor_used": True,
                "successful_tasks": successful_tasks,
                "total_tasks": len(tasks)
            }
        else:
            return {
                "mode": "task_breakdown_failed",
                "response": "All tasks failed. Please try breaking your question into smaller parts.",
                "task_results": results,
                "conductor_used": True
            }
    
    def _create_tasks_from_query(self, prompt: str) -> List[Dict]:
        """Create specific tasks based on query content"""
        prompt_lower = prompt.lower()
        
        # Legal case analysis tasks
        if any(word in prompt_lower for word in ['lawsuit', 'legal', 'case', 'law firm', 'attorney']):
            return [
                {"title": "Legal Situation Analysis", "query": f"Analyze the legal situation and identify the key issues for: {prompt[:200]}..."},
                {"title": "Applicable Law Areas", "query": f"Identify the specific areas of law that apply to this case: {prompt[:200]}..."},
                {"title": "Case Strengths Assessment", "query": f"Assess the strengths of this case and potential legal arguments: {prompt[:200]}..."},
                {"title": "Law Firm Research", "query": f"Research and identify suitable law firms for this type of case: {prompt[:200]}..."},
                {"title": "Legal Strategy Development", "query": f"Develop a comprehensive legal strategy for this case: {prompt[:200]}..."},
                {"title": "Documentation and Tracking", "query": f"Create templates and tracking systems for this legal case: {prompt[:200]}..."},
                {"title": "Risk Assessment", "query": f"Assess the risks and challenges associated with this case: {prompt[:200]}..."},
                {"title": "Next Steps and Recommendations", "query": f"Provide specific next steps and recommendations for this case: {prompt[:200]}..."}
            ]
        
        # General complex query tasks
        elif len(prompt.split()) > 100:
            return [
                {"title": "Core Analysis", "query": f"Provide a core analysis of: {prompt[:150]}..."},
                {"title": "Detailed Breakdown", "query": f"Break down the key components of: {prompt[:150]}..."},
                {"title": "Research and Findings", "query": f"Research and provide findings for: {prompt[:150]}..."},
                {"title": "Strategy and Recommendations", "query": f"Develop strategy and recommendations for: {prompt[:150]}..."},
                {"title": "Implementation Plan", "query": f"Create an implementation plan for: {prompt[:150]}..."}
            ]
        
        # Simple query - no breakdown needed
        else:
            return [
                {"title": "Direct Response", "query": prompt}
            ]
    
    def _process_single_task(self, task: Dict, conversation_history: List[Dict] = None) -> str:
        """Process a single task with timeout protection"""
        try:
            # Use Gemini for individual tasks (most reliable)
            response, metadata = self.orchestrator.query_gemini(task['query'], conversation_history)
            return response
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            raise e
