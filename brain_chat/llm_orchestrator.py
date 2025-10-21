"""
Holly Hot Box - Multi-LLM Orchestrator
Combines all LLMs to provide the best collaborative response
"""
import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
import openai
import google.generativeai as genai
import anthropic
from huggingface_hub import InferenceClient
import requests

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """Orchestrates multiple LLMs to work together"""
    
    def __init__(self):
        """Initialize all LLM clients"""
        try:
            # OpenAI GPT-5 Nano - Cost-Effective GPT-5 Variant
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            logger.error(f"OpenAI init error: {e}")
            self.openai_client = None
        
        try:
            # Google Gemini Tier 3 - PRIMARY STRATEGIST (Premium Access!)
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            # Use stable Gemini model instead of experimental to prevent hanging
            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 8192,  # Tier 3 allows more tokens
                }
            )
        except Exception as e:
            logger.error(f"Gemini init error: {e}")
            self.gemini_model = None
        
        try:
            # Anthropic Claude - Creative Director
            self.claude_client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        except Exception as e:
            logger.error(f"Claude init error: {e}")
            self.claude_client = None
        
        # Hugging Face - Johnny's Digital Clone
        # Temporarily disabled due to API compatibility issues
        self.hf_client = None
        # try:
        #     self.hf_client = InferenceClient(token=os.getenv('HUGGINGFACE_API_KEY'))
        # except Exception as e:
        #     logger.error(f"HuggingFace init error: {e}")
        #     self.hf_client = None
        
        # DeepSeek Reasoner - DEEP THINKING at ultra-low cost! 
        # DeepSeek-V3.2 Reasoner is incredibly cost-effective
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        
        # Grok uses REST API
        self.grok_key = os.getenv('GROK_API_KEY')
    
    def query_openai(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query OpenAI GPT-5 Nano - Cost-effective GPT-5 variant"""
        if not self.openai_client:
            return "OpenAI is temporarily unavailable", {"error": "Client not initialized"}
        
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-5-nano",  # Using GPT-5 Nano for cost efficiency
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return response.choices[0].message.content, {
                "tokens": response.usage.total_tokens,
                "response_time_ms": response_time,
                "model": "gpt-5-nano"
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"OpenAI Error: {str(e)}", {"error": str(e)}
    
    def query_gemini(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query Google Gemini Tier 3 - PREMIUM ACCESS with Advanced Thinking"""
        if not self.gemini_model:
            return "Gemini is temporarily unavailable", {"error": "Client not initialized"}
        
        try:
            start_time = time.time()
            
            # Enhanced prompt to leverage Gemini's thinking capabilities
            enhanced_prompt = f"""You are Gemini 2.0 Flash Thinking - Google's most advanced AI with deep reasoning capabilities.

{prompt}

Please provide a comprehensive, well-reasoned response leveraging your advanced thinking and analysis capabilities."""
            
            # Build conversation context with history
            history = []
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    history.append({
                        'role': 'user' if msg['role'] == 'user' else 'model',
                        'parts': [msg['content']]
                    })
            
            # Add timeout to prevent hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Gemini API call timed out")
            
            # Set 30 second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                chat = self.gemini_model.start_chat(history=history)
                response = chat.send_message(enhanced_prompt)
                signal.alarm(0)  # Cancel timeout
                
                response_time = int((time.time() - start_time) * 1000)
                
                return response.text, {
                    "tokens": len(prompt.split()) + len(response.text.split()),
                    "response_time_ms": response_time,
                    "model": "gemini-1.5-flash (Tier 3 Premium)",
                    "tier": "premium_tier_3"
                }
            except TimeoutError:
                signal.alarm(0)  # Cancel timeout
                logger.error("Gemini API call timed out after 30 seconds")
                return "Gemini Error: API call timed out", {"error": "timeout"}
                
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"Gemini Error: {str(e)}", {"error": str(e)}
    
    def query_claude(self, prompt: str, conversation_history: List[Dict] = None, preferred_model: str = "haiku") -> Tuple[str, Dict]:
        """Query Anthropic Claude - Haiku 4.5 default with Sonnet 4.5 and Opus 4.1 available"""
        if not self.claude_client:
            return "Claude is temporarily unavailable", {"error": "Client not initialized"}
        
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            # Model selection based on preference or intelligent fallback
            model_map = {
                "haiku": "claude-haiku-4.5-20250514",      # Default: Fast & cost-effective
                "sonnet": "claude-sonnet-4.5-20250514",    # Balanced: Higher intelligence
                "opus": "claude-opus-4.1-20250514"          # Premium: Maximum power
            }
            
            # Try preferred model first, then fallback
            models_to_try = [model_map.get(preferred_model, model_map["haiku"])]
            
            # Add fallbacks if primary fails
            if preferred_model != "haiku":
                models_to_try.append(model_map["haiku"])
            
            for model in models_to_try:
                try:
                    response = self.claude_client.messages.create(
                        model=model,
                        max_tokens=4000,
                        messages=messages
                    )
                    
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Determine friendly name
                    model_name = "Claude Haiku 4.5" if "haiku" in model else \
                                "Claude Sonnet 4.5" if "sonnet" in model else \
                                "Claude Opus 4.1"
                    
                    return response.content[0].text, {
                        "tokens": response.usage.input_tokens + response.usage.output_tokens,
                        "response_time_ms": response_time,
                        "model": model_name,
                        "model_tier": "fast" if "haiku" in model else "balanced" if "sonnet" in model else "premium"
                    }
                except Exception as model_error:
                    logger.debug(f"Claude model {model} failed, trying next: {model_error}")
                    continue
            
            # If all models failed
            return "Claude Error: All model variants unavailable", {"error": "All Claude models failed"}
            
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return f"Claude Error: {str(e)}", {"error": str(e)}
    
    def query_deepseek(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query DeepSeek-Reasoner - DEEP THINKING MODE (Ultra Cost-Effective!)"""
        try:
            start_time = time.time()
            
            # Enhanced prompt for reasoning mode
            reasoning_prompt = f"""You are DeepSeek-Reasoner (DeepSeek-V3.2-Exp) - a world-class deep thinking AI.

Your specialty is analytical reasoning, step-by-step problem solving, and cost-effective intelligence.

Task: {prompt}

Please think deeply and provide a well-reasoned, analytical response."""
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": reasoning_prompt})
            
            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-reasoner",  # Using reasoning mode!
                    "messages": messages,
                    "temperature": 1.0,  # Reasoning models work best at higher temp
                    "max_tokens": 8000  # More tokens for deep reasoning
                },
                timeout=45  # Reduced timeout to prevent hanging
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                
                # DeepSeek-Reasoner returns reasoning_content and content
                reasoning_tokens = data['usage'].get('reasoning_tokens', 0)
                total_tokens = data['usage']['total_tokens']
                
                # Get the final answer (not the reasoning process)
                content = data['choices'][0]['message']['content']
                
                return content, {
                    "tokens": total_tokens,
                    "reasoning_tokens": reasoning_tokens,
                    "response_time_ms": response_time,
                    "model": "deepseek-reasoner (V3.2 Deep Think)",
                    "cost_tier": "ultra_low",
                    "thinking_mode": "active"
                }
            else:
                return f"DeepSeek Error: HTTP {response.status_code}", {"error": response.text}
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return f"DeepSeek Error: {str(e)}", {"error": str(e)}
    
    def query_grok(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query xAI Grok - Try SuperGrok first, fall back to regular Grok"""
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            # Try SuperGrok first (premium tier)
            models_to_try = ["grok-2-1212", "grok-2", "grok-beta"]  # SuperGrok variants, then fallback
            
            for model in models_to_try:
                try:
                    response = requests.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.grok_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": messages,
                            "temperature": 0.7,
                            "max_tokens": 4000
                        },
                        timeout=30
                    )
                    
                    response_time = int((time.time() - start_time) * 1000)
                    
                    if response.status_code == 200:
                        data = response.json()
                        model_used = "SuperGrok" if model in ["grok-2-1212", "grok-2"] else "Grok"
                        return data['choices'][0]['message']['content'], {
                            "tokens": data['usage']['total_tokens'],
                            "response_time_ms": response_time,
                            "model": f"{model_used} ({model})"
                        }
                except Exception as model_error:
                    logger.debug(f"Model {model} failed, trying next: {model_error}")
                    continue
            
            # If all models failed
            return "Grok Error: All model variants unavailable", {"error": "All Grok models failed"}
            
        except Exception as e:
            logger.error(f"Grok error: {e}")
            return f"Grok Error: {str(e)}", {"error": str(e)}
    
    def query_huggingface(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query Hugging Face (Johnny's Digital Clone)"""
        if not self.hf_client:
            return "Hugging Face is temporarily unavailable", {"error": "Client not initialized"}
        
        try:
            start_time = time.time()
            
            # Use Meta-Llama-3 for the digital clone
            response = self.hf_client.text_generation(
                prompt,
                model="meta-llama/Meta-Llama-3-8B-Instruct",
                max_new_tokens=500,
                temperature=0.7
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return response, {
                "tokens": len(prompt.split()) + len(response.split()),
                "response_time_ms": response_time,
                "model": "Meta-Llama-3-8B-Instruct"
            }
        except Exception as e:
            logger.error(f"Hugging Face error: {e}")
            return f"Hugging Face Error: {str(e)}", {"error": str(e)}
    
    def orchestrate_response(
        self,
        prompt: str,
        conversation_history: List[Dict] = None,
        mode: str = "consensus"
    ) -> Dict:
        """
        Orchestrate responses from all LLMs - LED BY GEMINI TIER 3
        
        Modes:
        - consensus: Get responses from all LLMs and synthesize (Gemini-led)
        - fastest: Return the first response
        - best: Use Gemini Tier 3 to pick the best response
        - parallel: Show all responses side-by-side
        - gemini_only: Use ONLY Gemini Tier 3 for premium response
        - deepseek_only: Use ONLY DeepSeek Reasoner for cost-effective deep thinking
        - power_duo: Use Gemini + DeepSeek together for ultimate reasoning
        """
        
        results = {}
        
        # Single LLM modes for focused responses
        if mode == "gemini_only":
            logger.info(f"Using GEMINI TIER 3 ONLY for prompt: {prompt[:100]}...")
            response, metadata = self.query_gemini(prompt, conversation_history)
            return {
                "mode": "gemini_only",
                "response": response,
                "metadata": metadata,
                "provider": "gemini"
            }
        
        if mode == "deepseek_only":
            logger.info(f"Using DEEPSEEK REASONER ONLY for prompt: {prompt[:100]}...")
            response, metadata = self.query_deepseek(prompt, conversation_history)
            return {
                "mode": "deepseek_only",
                "response": response,
                "metadata": metadata,
                "provider": "deepseek"
            }
        
        if mode == "power_duo":
            logger.info(f"Using GEMINI + DEEPSEEK POWER DUO for prompt: {prompt[:100]}...")
            # Get both responses
            gemini_response, gemini_meta = self.query_gemini(prompt, conversation_history)
            deepseek_response, deepseek_meta = self.query_deepseek(prompt, conversation_history)
            
            # Use Gemini to synthesize both
            synthesis_prompt = f"""
You are Gemini 2.0 Flash Thinking - synthesizing insights from two powerful thinking models.

Original Question: {original_prompt}

YOUR ANALYSIS (Gemini Tier 3):
{gemini_response}

DEEPSEEK REASONER ANALYSIS (Ultra Cost-Effective Deep Thinking):
{deepseek_response}

Provide a final synthesized answer that combines the best of both analyses:"""
            
            final_response, final_meta = self.query_gemini(synthesis_prompt)
            
            return {
                "mode": "power_duo",
                "final_response": final_response,
                "gemini_response": gemini_response,
                "deepseek_response": deepseek_response,
                "metadata": final_meta,
                "synthesis": "gemini_tier_3"
            }
        
        # Query all LLMs - prioritize Gemini & DeepSeek first (power duo!)
        logger.info(f"Orchestrating '{mode}' response for prompt: {prompt[:100]}...")
        
        llm_queries = {
            "gemini": self.query_gemini,      # #1 - Gemini Tier 3 Premium
            "deepseek": self.query_deepseek,  # #2 - DeepSeek Reasoner (ultra cost-effective)
            "claude": self.query_claude,
            "openai": self.query_openai,
            "grok": self.query_grok,
            "huggingface": self.query_huggingface
        }
        
        # Execute all queries with individual timeouts
        for name, query_func in llm_queries.items():
            try:
                response, metadata = query_func(prompt, conversation_history)
                results[name] = {
                    "response": response,
                    "metadata": metadata
                }
            except Exception as e:
                logger.error(f"Error querying {name}: {e}")
                results[name] = {
                    "response": f"Error: {str(e)}",
                    "metadata": {"error": str(e)}
                }
        
        # If all LLMs failed, return a simple fallback
        successful_responses = [r for r in results.values() if not r['response'].startswith('Error:')]
        if not successful_responses:
            return {
                "mode": mode,
                "response": "All AI models are currently unavailable. Please try again later.",
                "metadata": {"error": "all_models_failed"},
                "provider": "fallback"
            }
        
        # Process based on mode
        if mode == "consensus":
            return self._build_consensus(results, prompt)
        elif mode == "fastest":
            return self._get_fastest(results)
        elif mode == "best":
            return self._get_best(results, prompt)
        else:  # parallel
            return {"mode": "parallel", "results": results}
    
    def _build_consensus(self, results: Dict, original_prompt: str) -> Dict:
        """Build a consensus response from all LLMs - Led by Gemini Tier 3"""
        # Use Gemini Tier 3 (Premium) as PRIMARY synthesizer due to advanced thinking
        # Give Gemini's response DOUBLE WEIGHT in synthesis
        synthesis_prompt = f"""
You are Google Gemini 2.0 Flash Thinking - the PRIMARY STRATEGIST leading a team of AI models.

Your role is to synthesize the best insights from all AI responses into a single, comprehensive answer.

⭐ PRIORITY: Your own analysis and insights should be weighted HEAVILY as you have the most advanced reasoning.

Original Question: {original_prompt}

TEAM RESPONSES:
"""
        # Highlight Gemini & DeepSeek responses with special emphasis
        for name, data in results.items():
            if name == 'gemini':
                synthesis_prompt += f"\n\n🌟 YOUR ANALYSIS (GEMINI TIER 3 - PRIMARY WEIGHT):\n{data['response']}\n"
            elif name == 'deepseek':
                synthesis_prompt += f"\n\n💎 DEEPSEEK REASONER ANALYSIS (DEEP THINKING - HIGH WEIGHT):\n{data['response']}\n"
            else:
                synthesis_prompt += f"\n\n{name.upper()}:\n{data['response']}\n"
        
        synthesis_prompt += """

INSTRUCTIONS:
1. Lead with YOUR insights and analysis (Gemini Tier 3)
2. Give HEAVY WEIGHT to DeepSeek Reasoner's deep analytical thinking
3. Integrate valuable points from other models
4. Provide a comprehensive, well-reasoned final answer
5. Leverage your advanced thinking capabilities to go deeper than the others

Final synthesized response:"""
        
        # Use Gemini to synthesize (instead of OpenAI)
        try:
            final_response, metadata = self.query_gemini(synthesis_prompt)
        except Exception as e:
            logger.error(f"Gemini synthesis failed: {e}")
            # Fallback to simple concatenation if Gemini fails
            final_response = "Consensus from multiple AI models:\n\n"
            for name, data in results.items():
                if data['response'] and not data['response'].startswith('Error:'):
                    final_response += f"**{name.upper()}:** {data['response'][:500]}...\n\n"
            metadata = {"error": "gemini_synthesis_failed", "fallback": "simple_concat"}
        
        return {
            "mode": "consensus",
            "final_response": final_response,
            "individual_responses": results,
            "metadata": metadata,
            "primary_synthesizer": "gemini_tier_3"
        }
    
    def _get_fastest(self, results: Dict) -> Dict:
        """Return the fastest response"""
        fastest = min(
            results.items(),
            key=lambda x: x[1]['metadata'].get('response_time_ms', float('inf'))
        )
        
        return {
            "mode": "fastest",
            "provider": fastest[0],
            "response": fastest[1]['response'],
            "metadata": fastest[1]['metadata']
        }
    
    def _get_best(self, results: Dict, original_prompt: str) -> Dict:
        """Use Gemini Tier 3 to determine the best response (most advanced reasoning)"""
        evaluation_prompt = f"""
You are Gemini 2.0 Flash Thinking - the most advanced AI evaluator.

Analyze these AI responses and determine which ONE is the BEST based on:
- Accuracy and correctness
- Depth of reasoning
- Practical usefulness
- Completeness

⭐ Be objective - if YOUR response (gemini) is best, say so. If another model did better, acknowledge it.

Original Question: {original_prompt}

RESPONSES TO EVALUATE:
"""
        for name, data in results.items():
            evaluation_prompt += f"\n\n{name.upper()}:\n{data['response']}\n"
        
        evaluation_prompt += """

Reply with ONLY the provider name (openai, gemini, claude, deepseek, grok, or huggingface) - nothing else:"""
        
        # Use Gemini to evaluate (more advanced reasoning)
        best_provider, _ = self.query_gemini(evaluation_prompt)
        best_provider = best_provider.strip().lower()
        
        # Clean up response (in case Gemini added explanation)
        for provider in ['openai', 'gemini', 'claude', 'deepseek', 'grok', 'huggingface']:
            if provider in best_provider:
                best_provider = provider
                break
        
        if best_provider in results:
            return {
                "mode": "best",
                "provider": best_provider,
                "response": results[best_provider]['response'],
                "metadata": results[best_provider]['metadata'],
                "all_responses": results,
                "evaluated_by": "gemini_tier_3"
            }
        else:
            # Fallback to Gemini (our premium model)
            return {
                "mode": "best",
                "provider": "gemini",
                "response": results['gemini']['response'],
                "metadata": results['gemini']['metadata'],
                "all_responses": results,
                "evaluated_by": "gemini_tier_3"
            }

