"""
Smart Conductor - Intelligent LLM Orchestration System
Based on research from LangChain, LlamaIndex, and production best practices
"""
import logging
import json
from typing import Dict, List, Tuple, Optional
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SmartConductor:
    """
    Intelligent orchestrator that:
    1. Analyzes query complexity
    2. Retrieves project context (description, summary, files)
    3. Breaks down complex queries into sub-tasks
    4. Routes tasks to appropriate LLMs
    5. Synthesizes final response
    """
    
    def __init__(self, orchestrator, project=None):
        self.orchestrator = orchestrator
        self.project = project
        
    def conduct_query(self, prompt: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Main entry point for conducting a query
        """
        try:
            # Step 1: Build enriched context from project
            enriched_prompt = self._enrich_prompt_with_project_context(prompt)
            
            # Step 2: Analyze complexity
            complexity_analysis = self._analyze_complexity(enriched_prompt)
            logger.info(f"📊 Complexity: {complexity_analysis['level']} (score: {complexity_analysis['score']})")
            
            # Step 3: Choose strategy based on complexity
            if complexity_analysis['level'] == 'simple':
                # Direct Gemini call - fast and reliable
                logger.info("✅ Simple query - using Gemini directly")
                return self._execute_simple(enriched_prompt, conversation_history)
            
            elif complexity_analysis['level'] == 'moderate':
                # Use Gemini with enhanced context
                logger.info("🔧 Moderate query - using Gemini with enhanced prompting")
                return self._execute_moderate(enriched_prompt, conversation_history)
            
            else:  # complex or multi_faceted
                # Break down into focused sub-queries
                logger.info("🎯 Complex query - using iterative breakdown")
                return self._execute_complex(enriched_prompt, conversation_history, complexity_analysis)
                
        except Exception as e:
            logger.error(f"💥 Conductor failed: {e}")
            # Always fall back to simple Gemini
            try:
                response, metadata = self.orchestrator.query_gemini(prompt, conversation_history)
                return {
                    "mode": "gemini_fallback",
                    "response": response,
                    "metadata": metadata,
                    "conductor_used": True,
                    "fallback_reason": str(e)
                }
            except Exception as fallback_error:
                raise Exception(f"Both conductor and fallback failed: {str(e)} | {str(fallback_error)}")
    
    def _enrich_prompt_with_project_context(self, prompt: str) -> str:
        """
        Enrich the prompt with project context if available
        Keep it CONCISE to avoid timeouts
        """
        if not self.project:
            return prompt
        
        context_parts = []
        
        # Add CONCISE project context
        if self.project.summary:
            # Use summary (it's already concise)
            context_parts.append(f"CASE CONTEXT: {self.project.summary[:300]}")
        elif self.project.description:
            # Use description if no summary
            context_parts.append(f"CASE CONTEXT: {self.project.description[:300]}")
        
        # Add file count (not full summaries - too long)
        try:
            files = self.project.files.all()
            file_count = len(list(files))
            if file_count > 0:
                file_names = [f.file_name for f in files[:5]]  # First 5 files only
                context_parts.append(f"\nRELEVANT FILES ({file_count} total): {', '.join(file_names)}")
        except Exception as e:
            logger.warning(f"Could not get files: {e}")
        
        # Add the user's question
        context_parts.append(f"\nQUESTION: {prompt}")
        
        enriched = "\n".join(context_parts)
        logger.info(f"📝 Enriched prompt: {len(enriched)} chars (from {len(prompt)})")
        return enriched
    
    def _analyze_complexity(self, prompt: str) -> Dict:
        """
        Analyze query complexity using multiple indicators
        """
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())
        
        # Complexity indicators
        has_multiple_questions = prompt.count('?') > 1
        has_numbered_list = any(f'{i})' in prompt or f'{i}.' in prompt for i in range(1, 10))
        has_long_context = word_count > 300
        has_legal_keywords = any(word in prompt_lower for word in [
            'lawsuit', 'legal', 'case', 'law firm', 'attorney', 'contract', 'litigation'
        ])
        has_analysis_request = any(word in prompt_lower for word in [
            'analyze', 'review', 'examine', 'assess', 'evaluate', 'identify', 'determine'
        ])
        has_multiple_parts = any(word in prompt_lower for word in [
            'then', 'also', 'additionally', 'furthermore', 'based on', 'after that'
        ])
        has_file_references = any(word in prompt_lower for word in [
            'uploaded', 'attached', 'file', 'document', 'summary', 'case files'
        ])
        
        # Calculate score
        score = sum([
            has_multiple_questions * 2,
            has_numbered_list * 2,
            has_long_context * 3,
            has_legal_keywords * 2,
            has_analysis_request * 1,
            has_multiple_parts * 2,
            has_file_references * 3
        ])
        
        # Determine level
        if score >= 8:
            level = 'multi_faceted'
        elif score >= 5:
            level = 'complex'
        elif score >= 2:
            level = 'moderate'
        else:
            level = 'simple'
        
        return {
            'level': level,
            'score': score,
            'word_count': word_count,
            'indicators': {
                'multiple_questions': has_multiple_questions,
                'numbered_list': has_numbered_list,
                'long_context': has_long_context,
                'legal_keywords': has_legal_keywords,
                'analysis_request': has_analysis_request,
                'multiple_parts': has_multiple_parts,
                'file_references': has_file_references
            }
        }
    
    def _execute_simple(self, prompt: str, history: List[Dict]) -> Dict:
        """Execute simple queries directly with Gemini"""
        response, metadata = self.orchestrator.query_gemini(prompt, history)
        return {
            "mode": "simple_gemini",
            "response": response,
            "metadata": metadata,
            "conductor_used": True
        }
    
    def _execute_moderate(self, prompt: str, history: List[Dict]) -> Dict:
        """Execute moderate queries with enhanced prompting"""
        # Add structure to the prompt
        enhanced_prompt = f"""You are analyzing a detailed query. Please provide a comprehensive, well-structured response.

{prompt}

Please structure your response with:
1. Clear headings for each major point
2. Specific details and examples
3. Actionable recommendations
4. Summary of key takeaways"""
        
        response, metadata = self.orchestrator.query_gemini(enhanced_prompt, history)
        return {
            "mode": "moderate_enhanced",
            "response": response,
            "metadata": metadata,
            "conductor_used": True
        }
    
    def _execute_complex(self, prompt: str, history: List[Dict], analysis: Dict) -> Dict:
        """
        Execute complex queries using iterative breakdown
        This is the key innovation - don't try to do everything at once
        """
        logger.info("🔧 Breaking down complex query into focused sub-queries")
        
        # Use Gemini to break down the query intelligently
        breakdown_prompt = f"""You are a query decomposition expert. Analyze this complex query and break it into 3-5 focused, specific sub-questions that can be answered independently.

Original Query:
{prompt}

Create a JSON array of sub-questions, each with:
- "question": the specific sub-question
- "priority": 1 (high), 2 (medium), or 3 (low)
- "depends_on": null or index of question it depends on (0-based)

Return ONLY the JSON array, no other text."""
        
        try:
            breakdown_response, _ = self.orchestrator.query_gemini(breakdown_prompt, [])
            
            # Parse the sub-questions
            import re
            json_match = re.search(r'\[.*\]', breakdown_response, re.DOTALL)
            if json_match:
                sub_questions = json.loads(json_match.group())
                logger.info(f"📋 Created {len(sub_questions)} sub-questions")
            else:
                raise ValueError("Failed to parse sub-questions")
            
        except Exception as e:
            logger.warning(f"⚠️ Breakdown failed: {e}, using direct approach")
            # Fallback: just use Gemini with the full prompt
            response, metadata = self.orchestrator.query_gemini(prompt, history)
            return {
                "mode": "complex_fallback",
                "response": response,
                "metadata": metadata,
                "conductor_used": True
            }
        
        # Answer sub-questions iteratively
        answers = {}
        for i, sq in enumerate(sub_questions):
            try:
                logger.info(f"🔄 Answering sub-question {i+1}/{len(sub_questions)}: {sq['question'][:100]}...")
                
                # Build context from previous answers if needed
                context = ""
                if sq.get('depends_on') is not None:
                    dep_idx = sq['depends_on']
                    if dep_idx in answers:
                        context = f"\nContext from previous answer:\n{answers[dep_idx]}\n"
                
                full_question = f"{context}{sq['question']}"
                answer, _ = self.orchestrator.query_gemini(full_question, history)
                answers[i] = answer
                logger.info(f"✅ Sub-question {i+1} answered ({len(answer)} chars)")
                
            except Exception as sq_error:
                logger.warning(f"⚠️ Sub-question {i+1} failed: {sq_error}")
                answers[i] = f"[Could not fully answer this part: {str(sq_error)}]"
        
        # Synthesize final answer
        synthesis_prompt = f"""You are synthesizing answers to create a comprehensive response. Here are the answers to sub-questions:

Original Query: {prompt}

Sub-Question Answers:
{json.dumps(answers, indent=2)}

Please provide a comprehensive, well-structured final response that:
1. Integrates all the sub-answers coherently
2. Addresses the original query completely
3. Is organized with clear headings
4. Provides actionable recommendations"""
        
        try:
            final_response, metadata = self.orchestrator.query_gemini(synthesis_prompt, history)
            return {
                "mode": "complex_iterative",
                "response": final_response,
                "metadata": metadata,
                "conductor_used": True,
                "sub_questions_count": len(sub_questions),
                "successful_answers": len([a for a in answers.values() if not a.startswith("[Could not")])
            }
        except Exception as synth_error:
            logger.error(f"💥 Synthesis failed: {synth_error}")
            # Return raw answers if synthesis fails
            combined = "\n\n".join([f"**Part {i+1}:**\n{answer}" for i, answer in answers.items()])
            return {
                "mode": "complex_raw",
                "response": combined,
                "metadata": {"error": "Synthesis failed, showing raw answers"},
                "conductor_used": True
            }

