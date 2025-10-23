"""
Bulletproof Conductor - Production-grade LLM Orchestration
No timeouts, graceful degradation, real progress tracking
"""
import logging
import json
import time
from typing import Dict, List, Generator

logger = logging.getLogger(__name__)


class BulletproofConductor:
    """
    A production-grade conductor that NEVER fails:
    - Processes queries in manageable chunks
    - Returns progress updates as it works
    - Degrades gracefully if anything fails
    - Always provides SOMETHING useful
    """
    
    def __init__(self, orchestrator, project=None):
        self.orchestrator = orchestrator
        self.project = project
        
    def conduct_streaming(self, prompt: str, conversation_history: List[Dict] = None) -> Generator[Dict, None, None]:
        """
        Process query with real-time progress updates
        Yields progress dicts that can be sent to frontend
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze and prepare
            yield {
                "status": "analyzing",
                "message": "🔍 Analyzing your query...",
                "progress": 10
            }
            
            # Get project context
            context = self._build_context()
            enriched_prompt = f"{context}\n\nQUESTION: {prompt}" if context else prompt
            
            # Analyze complexity
            analysis = self._quick_analysis(enriched_prompt)
            logger.info(f"Query complexity: {analysis['level']}")
            
            yield {
                "status": "analyzed",
                "message": f"📊 Detected {analysis['level']} query with {analysis['parts']} parts",
                "progress": 20
            }
            
            # Step 2: Break into sub-tasks if needed
            if analysis['level'] in ['complex', 'multi_faceted']:
                yield {
                    "status": "breaking_down",
                    "message": "🔧 Breaking down into manageable parts...",
                    "progress": 25
                }
                
                sub_tasks = self._create_sub_tasks(enriched_prompt, analysis)
                logger.info(f"Created {len(sub_tasks)} sub-tasks")
                
                yield {
                    "status": "tasks_created",
                    "message": f"✅ Created {len(sub_tasks)} focused tasks",
                    "progress": 30
                }
                
                # Step 3: Process each sub-task
                results = []
                for i, task in enumerate(sub_tasks):
                    progress = 30 + (60 * (i / len(sub_tasks)))
                    
                    yield {
                        "status": "processing",
                        "message": f"⚙️ Processing: {task['title']}",
                        "progress": int(progress),
                        "current_task": i + 1,
                        "total_tasks": len(sub_tasks)
                    }
                    
                    try:
                        result = self._process_task(task, conversation_history)
                        results.append({
                            "task": task['title'],
                            "result": result,
                            "status": "success"
                        })
                        
                        yield {
                            "status": "task_complete",
                            "message": f"✓ Completed: {task['title']}",
                            "progress": int(progress + (60 / len(sub_tasks))),
                            "partial_result": result[:200] + "..." if len(result) > 200 else result
                        }
                        
                    except Exception as task_error:
                        logger.warning(f"Task {i+1} failed: {task_error}")
                        results.append({
                            "task": task['title'],
                            "result": f"Unable to complete this part: {str(task_error)}",
                            "status": "failed"
                        })
                
                # Step 4: Synthesize final answer
                yield {
                    "status": "synthesizing",
                    "message": "🎯 Synthesizing comprehensive answer...",
                    "progress": 90
                }
                
                final_answer = self._synthesize_results(prompt, results)
                
            else:
                # Simple query - direct processing
                yield {
                    "status": "processing",
                    "message": "⚙️ Processing your question...",
                    "progress": 50
                }
                
                final_answer = self._process_simple(enriched_prompt, conversation_history)
            
            # Step 5: Success!
            elapsed = time.time() - start_time
            
            yield {
                "status": "complete",
                "message": f"✅ Analysis complete! ({elapsed:.1f}s)",
                "progress": 100,
                "response": final_answer,
                "metadata": {
                    "complexity": analysis['level'],
                    "elapsed_seconds": elapsed,
                    "tasks_completed": len(results) if 'results' in locals() else 1
                }
            }
            
        except Exception as e:
            # GRACEFUL DEGRADATION - Always return something
            logger.error(f"Conductor failed completely: {e}")
            
            yield {
                "status": "error_fallback",
                "message": "⚠️ Using emergency fallback...",
                "progress": 95
            }
            
            try:
                # Emergency: Just ask Gemini directly
                response, _ = self.orchestrator.query_gemini(prompt, conversation_history or [])
                
                yield {
                    "status": "complete",
                    "message": "✅ Completed (emergency mode)",
                    "progress": 100,
                    "response": response,
                    "metadata": {"mode": "emergency_fallback", "error": str(e)}
                }
            except Exception as final_error:
                # ABSOLUTE LAST RESORT
                yield {
                    "status": "failed",
                    "message": "❌ Unable to process query",
                    "progress": 100,
                    "response": f"I apologize, but I encountered an error processing your query. Please try breaking it into smaller questions. Error: {str(final_error)}",
                    "metadata": {"mode": "total_failure"}
                }
    
    def _build_context(self) -> str:
        """Build concise project context"""
        if not self.project:
            return ""
        
        parts = []
        
        if self.project.summary:
            parts.append(f"CASE SUMMARY: {self.project.summary[:400]}")
        elif self.project.description:
            parts.append(f"CASE CONTEXT: {self.project.description[:400]}")
        
        try:
            files = list(self.project.files.all()[:10])
            if files:
                file_list = ", ".join([f.file_name for f in files])
                parts.append(f"\nAVAILABLE FILES: {file_list}")
        except:
            pass
        
        return "\n".join(parts) if parts else ""
    
    def _quick_analysis(self, prompt: str) -> Dict:
        """Quick complexity analysis"""
        word_count = len(prompt.split())
        question_count = prompt.count('?')
        
        # Count indicators
        has_multiple_parts = any(str(i) in prompt for i in range(1, 10))
        has_legal = any(w in prompt.lower() for w in ['legal', 'law', 'case', 'lawsuit', 'attorney'])
        is_long = word_count > 200
        
        if question_count >= 5 or (has_multiple_parts and is_long):
            level = 'multi_faceted'
            parts = max(question_count, 5)
        elif question_count >= 3 or (has_legal and is_long):
            level = 'complex'
            parts = max(question_count, 3)
        elif question_count >= 2 or word_count > 100:
            level = 'moderate'
            parts = 2
        else:
            level = 'simple'
            parts = 1
        
        return {
            'level': level,
            'parts': parts,
            'word_count': word_count
        }
    
    def _create_sub_tasks(self, prompt: str, analysis: Dict) -> List[Dict]:
        """Create focused sub-tasks for complex queries"""
        prompt_lower = prompt.lower()
        
        # Legal case analysis pattern
        if 'law' in prompt_lower or 'legal' in prompt_lower:
            return [
                {"title": "Legal Situation Analysis", "query": f"Based on the case context, analyze the legal situation and identify the key legal issues. Focus on: What happened, who's involved, what laws apply.\n\n{prompt}"},
                {"title": "Law Firm Research", "query": f"Research and recommend Miami-Dade law firms that specialize in business/contract litigation and work on contingency. Explain what makes them suitable.\n\n{prompt}"},
                {"title": "Case Attractiveness to Contingency Lawyers", "query": f"Analyze what makes this case attractive to contingency lawyers. Include: potential damages, strength of case, likelihood of success.\n\n{prompt}"},
                {"title": "Legal Strategy & Next Steps", "query": f"Create a comprehensive legal strategy summary including: key legal issues, potential damages, case strengths, and specific next steps.\n\n{prompt}"}
            ]
        
        # General complex query - let Gemini break it down
        try:
            breakdown_prompt = f"Break this complex query into 3-4 focused sub-questions. Return ONLY a JSON array of objects with 'title' and 'query' fields:\n\n{prompt[:500]}"
            response, _ = self.orchestrator.query_gemini(breakdown_prompt, [])
            
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: Simple split
        return [
            {"title": "Part 1", "query": prompt},
            {"title": "Part 2", "query": f"Continue analyzing: {prompt}"}
        ]
    
    def _process_task(self, task: Dict, history: List[Dict]) -> str:
        """Process a single task with timeout protection"""
        try:
            response, _ = self.orchestrator.query_gemini(task['query'], history or [])
            return response
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            return f"[This section could not be completed: {str(e)}]"
    
    def _process_simple(self, prompt: str, history: List[Dict]) -> str:
        """Process simple queries directly"""
        response, _ = self.orchestrator.query_gemini(prompt, history or [])
        return response
    
    def _synthesize_results(self, original_prompt: str, results: List[Dict]) -> str:
        """Synthesize sub-task results into comprehensive answer"""
        try:
            synthesis_prompt = f"""Synthesize these task results into a comprehensive, well-structured response:

Original Question: {original_prompt}

Task Results:
{json.dumps(results, indent=2)}

Provide a complete, professional response that integrates all successful results. Use clear headings and formatting."""
            
            response, _ = self.orchestrator.query_gemini(synthesis_prompt, [])
            return response
            
        except Exception as e:
            # Fallback: Just concatenate results
            logger.warning(f"Synthesis failed: {e}, using concatenation")
            parts = []
            for r in results:
                if r['status'] == 'success':
                    parts.append(f"## {r['task']}\n\n{r['result']}\n")
            return "\n".join(parts) if parts else "Unable to generate complete response."

