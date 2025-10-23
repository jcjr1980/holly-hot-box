"""
Holly Hot Box - Query Conductor
Intelligently breaks down complex queries and orchestrates LLM collaboration
Similar to MCP (Model Context Protocol) but optimized for multi-LLM coordination
"""
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class QueryConductor:
    """
    The Conductor - Breaks down complex queries and orchestrates LLM responses
    
    Like a symphony conductor, it:
    1. Analyzes the query complexity
    2. Breaks it into manageable sub-tasks
    3. Assigns the best LLM for each sub-task
    4. Coordinates responses
    5. Synthesizes final answer
    """
    
    def __init__(self, orchestrator):
        """Initialize with reference to LLM orchestrator"""
        self.orchestrator = orchestrator
        
    def analyze_query_complexity(self, prompt: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Analyze the query to determine complexity and required approach
        
        Returns:
        {
            'complexity': 'simple' | 'moderate' | 'complex' | 'multi_faceted',
            'estimated_tokens': int,
            'requires_breakdown': bool,
            'recommended_strategy': str,
            'sub_tasks': List[Dict] if complex
        }
        """
        token_estimate = len(prompt.split()) * 1.3  # Rough token estimate
        
        # Check for complexity indicators
        has_multiple_questions = prompt.count('?') > 1
        has_long_context = len(prompt.split()) > 200  # Lowered from 500 to 200 words
        # Check for file references - be extra sensitive to legal documents and case files
        has_file_references = (
            conversation_history and len(conversation_history) > 0 or
            any(word in prompt.lower() for word in ['file', 'document', 'upload', 'attached', 'case files', 'summary', 'uploaded', 'files'])
        )
        has_list_request = any(word in prompt.lower() for word in ['list', 'enumerate', 'identify all', 'find all'])
        has_analysis_request = any(word in prompt.lower() for word in ['analyze', 'evaluate', 'assess', 'compare', 'review', 'examine'])
        has_research_request = any(word in prompt.lower() for word in ['research', 'find firms', 'locate', 'search for', 'finding', 'help me by finding'])
        # Additional: Check if query has multiple distinct parts (numbered lists, "then", "also", etc.)
        has_multiple_parts = any(indicator in prompt.lower() for indicator in ['1)', '2)', 'then', 'also', 'additionally', 'based on'])
        
        complexity_score = sum([
            has_multiple_questions * 3,  # Increased weight for multiple questions
            has_long_context * 4,  # Increased weight for long context
            has_file_references * 4,  # Much higher weight for file-heavy queries
            has_list_request * 2,  # Increased weight for list requests
            has_analysis_request * 3,  # Increased weight for analysis requests
            has_research_request * 4,  # Increased weight for research requests
            has_multiple_parts * 3  # Increased weight for multi-part queries
        ])
        
        # Log complexity analysis for debugging
        logger.info(f"🔍 Complexity Analysis: score={complexity_score}, questions={has_multiple_questions}, long={has_long_context}, list={has_list_request}, analyze={has_analysis_request}, research={has_research_request}")
        
        # Determine complexity level - VERY AGGRESSIVE THRESHOLDS for lawsuit analysis
        if complexity_score >= 4:  # Much more aggressive - break down sooner
            complexity = 'multi_faceted'
            requires_breakdown = True
        elif complexity_score >= 2:  # Even moderate queries get breakdown for complex legal work
            complexity = 'complex'
            requires_breakdown = True
        elif complexity_score >= 1:
            complexity = 'moderate'
            requires_breakdown = False
        else:
            complexity = 'simple'
            requires_breakdown = False
        
        # Recommend strategy based on complexity
        if complexity == 'multi_faceted':
            strategy = 'orchestrated_breakdown'
        elif complexity == 'complex':
            strategy = 'power_duo'  # Gemini + DeepSeek
        elif complexity == 'moderate':
            strategy = 'gemini_only'
        else:
            strategy = 'fastest'
        
        return {
            'complexity': complexity,
            'estimated_tokens': int(token_estimate),
            'requires_breakdown': requires_breakdown,
            'recommended_strategy': strategy,
            'complexity_score': complexity_score,
            'indicators': {
                'multiple_questions': has_multiple_questions,
                'long_context': has_long_context,
                'file_references': has_file_references,
                'list_request': has_list_request,
                'analysis_request': has_analysis_request,
                'research_request': has_research_request
            }
        }
    
    def break_down_query(self, prompt: str, conversation_history: List[Dict] = None) -> List[Dict]:
        """
        Use Gemini to intelligently break down a complex query into sub-tasks
        
        Returns list of sub-tasks:
        [
            {
                'task': 'description',
                'priority': 1-5,
                'best_llm': 'gemini' | 'claude' | 'deepseek' | 'openai',
                'depends_on': [task_indices],
                'prompt': 'specific prompt for this task'
            }
        ]
        """
        logger.info(f"Breaking down complex query: {prompt[:100]}...")
        
        breakdown_prompt = f"""You are the Query Conductor - an expert at analyzing complex questions and breaking them into manageable sub-tasks.

ORIGINAL QUERY:
{prompt}

TASK: Break this query into 3-7 specific sub-tasks that can be tackled sequentially or in parallel.

For each sub-task, specify:
1. **Task Description**: What needs to be done
2. **Priority**: 1 (critical) to 5 (nice to have)
3. **Best LLM**: Which AI is best suited:
   - gemini: General intelligence, reasoning, synthesis
   - claude: Legal/contract analysis, writing, creative tasks
   - deepseek: Deep analytical reasoning, cost-effective thinking
   - openai: Quick responses, general tasks
4. **Dependencies**: Which tasks must complete first (if any)
5. **Specific Prompt**: The exact question to ask that LLM

Return ONLY valid JSON in this format:
{{
  "sub_tasks": [
    {{
      "task": "Task description",
      "priority": 1,
      "best_llm": "gemini",
      "depends_on": [],
      "prompt": "Specific question for this task"
    }}
  ],
  "execution_strategy": "sequential" or "parallel",
  "estimated_time": "estimated completion time"
}}

JSON Response:"""
        
        try:
            # Use Gemini to break down the query
            response, metadata = self.orchestrator.query_gemini(breakdown_prompt)
            
            # Try to parse JSON from response
            # Handle cases where Gemini adds markdown formatting
            json_str = response.strip()
            if json_str.startswith('```'):
                # Remove markdown code blocks
                json_str = json_str.split('```')[1]
                if json_str.startswith('json'):
                    json_str = json_str[4:]
            
            breakdown_data = json.loads(json_str.strip())
            
            logger.info(f"Successfully broke down query into {len(breakdown_data['sub_tasks'])} sub-tasks")
            return breakdown_data
            
        except Exception as e:
            logger.error(f"Failed to break down query: {e}")
            # Fallback: Create a simple breakdown
            return {
                'sub_tasks': [
                    {
                        'task': 'Full query processing',
                        'priority': 1,
                        'best_llm': 'gemini',
                        'depends_on': [],
                        'prompt': prompt
                    }
                ],
                'execution_strategy': 'sequential',
                'estimated_time': '1-2 minutes',
                'fallback': True
            }
    
    def execute_orchestrated_breakdown(
        self,
        prompt: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Execute a complex query using intelligent breakdown and orchestration
        
        This is the MCP-like approach:
        1. Analyze query complexity
        2. Break down into sub-tasks
        3. Execute sub-tasks with best-suited LLMs
        4. Synthesize final response
        """
        logger.info("🎭 CONDUCTOR: Starting orchestrated breakdown...")
        
        # Step 1: Analyze complexity
        analysis = self.analyze_query_complexity(prompt, conversation_history)
        logger.info(f"📊 Complexity: {analysis['complexity']} (score: {analysis['complexity_score']})")
        
        # Step 2: If simple enough, just use recommended strategy
        if not analysis['requires_breakdown']:
            logger.info(f"✅ Using simple strategy: {analysis['recommended_strategy']}")
            return self.orchestrator.orchestrate_response(
                prompt,
                conversation_history,
                mode=analysis['recommended_strategy']
            )
        
        # Step 3: Break down complex query
        logger.info("🔧 Breaking down complex query...")
        breakdown = self.break_down_query(prompt, conversation_history)
        
        if breakdown.get('fallback'):
            logger.warning("⚠️ Breakdown failed, using power_duo fallback")
            return self.orchestrator.orchestrate_response(
                prompt,
                conversation_history,
                mode='power_duo'
            )
        
        # Step 4: Execute sub-tasks
        sub_task_results = []
        execution_strategy = breakdown.get('execution_strategy', 'sequential')
        
        logger.info(f"🚀 Executing {len(breakdown['sub_tasks'])} sub-tasks ({execution_strategy})")
        
        for idx, sub_task in enumerate(breakdown['sub_tasks']):
            logger.info(f"📝 Task {idx+1}/{len(breakdown['sub_tasks'])}: {sub_task['task'][:60]}...")
            
            # Get the best LLM for this task
            llm_name = sub_task.get('best_llm', 'gemini')
            task_prompt = sub_task.get('prompt', sub_task['task'])
            
            # Execute with the recommended LLM
            try:
                if llm_name == 'gemini':
                    response, metadata = self.orchestrator.query_gemini(task_prompt, conversation_history)
                elif llm_name == 'claude':
                    response, metadata = self.orchestrator.query_claude(task_prompt, conversation_history)
                elif llm_name == 'deepseek':
                    response, metadata = self.orchestrator.query_deepseek(task_prompt, conversation_history)
                elif llm_name == 'openai':
                    response, metadata = self.orchestrator.query_openai(task_prompt, conversation_history)
                else:
                    response, metadata = self.orchestrator.query_gemini(task_prompt, conversation_history)
                
                sub_task_results.append({
                    'task': sub_task['task'],
                    'llm_used': llm_name,
                    'response': response,
                    'metadata': metadata,
                    'priority': sub_task.get('priority', 3)
                })
                
                logger.info(f"✅ Task {idx+1} completed by {llm_name}")
                
            except Exception as e:
                logger.error(f"❌ Task {idx+1} failed: {e}")
                sub_task_results.append({
                    'task': sub_task['task'],
                    'llm_used': llm_name,
                    'response': f"Error: {str(e)}",
                    'metadata': {'error': str(e)},
                    'priority': sub_task.get('priority', 3)
                })
        
        # Step 5: Synthesize final response using Gemini
        logger.info("🎯 Synthesizing final response...")
        
        synthesis_prompt = f"""You are the Query Conductor - synthesizing results from multiple specialized AI analyses.

ORIGINAL QUESTION:
{prompt}

SUB-TASK RESULTS:
"""
        for idx, result in enumerate(sub_task_results):
            synthesis_prompt += f"\n\n**Task {idx+1}** ({result['llm_used'].upper()}): {result['task']}\n"
            synthesis_prompt += f"Response: {result['response']}\n"
        
        synthesis_prompt += """

TASK: Create a comprehensive, well-organized final response that:
1. Directly answers the original question
2. Integrates insights from all sub-task results
3. Organizes information logically
4. Provides actionable recommendations
5. Is clear and easy to understand

Final Response:"""
        
        try:
            final_response, final_metadata = self.orchestrator.query_gemini(synthesis_prompt)
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Fallback: Simple concatenation
            final_response = "# Analysis Results\n\n"
            for idx, result in enumerate(sub_task_results):
                final_response += f"## {result['task']}\n{result['response']}\n\n"
            final_metadata = {'error': 'synthesis_failed', 'fallback': 'concat'}
        
        logger.info("✅ CONDUCTOR: Orchestration complete!")
        
        return {
            'mode': 'orchestrated_breakdown',
            'complexity_analysis': analysis,
            'breakdown': breakdown,
            'sub_task_results': sub_task_results,
            'final_response': final_response,
            'metadata': final_metadata,
            'conductor_used': True
        }
    
    def conduct_query(
        self,
        prompt: str,
        conversation_history: List[Dict] = None,
        force_mode: Optional[str] = None
    ) -> Dict:
        """
        Main entry point - intelligently conduct the query
        
        Args:
            prompt: The user's question/request
            conversation_history: Previous conversation context
            force_mode: Override automatic mode selection (optional)
        
        Returns:
            Response dict with final_response and metadata
        """
        # If mode is forced, use it
        if force_mode:
            logger.info(f"🎯 Using forced mode: {force_mode}")
            return self.orchestrator.orchestrate_response(
                prompt,
                conversation_history,
                mode=force_mode
            )
        
        # Otherwise, analyze and decide
        analysis = self.analyze_query_complexity(prompt, conversation_history)
        
        if analysis['requires_breakdown']:
            logger.info("🎭 Complex query detected - using orchestrated breakdown")
            return self.execute_orchestrated_breakdown(prompt, conversation_history)
        else:
            logger.info(f"✅ Using recommended strategy: {analysis['recommended_strategy']}")
            return self.orchestrator.orchestrate_response(
                prompt,
                conversation_history,
                mode=analysis['recommended_strategy']
            )

