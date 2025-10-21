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
        # OpenAI GPT-4o - The Conductor
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Google Gemini - Platform Strategist
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Anthropic Claude - Creative Director
        self.claude_client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
        
        # Hugging Face - Johnny's Digital Clone
        self.hf_client = InferenceClient(token=os.getenv('HUGGINGFACE_API_KEY'))
        
        # DeepSeek & Grok use REST APIs
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.grok_key = os.getenv('GROK_API_KEY')
    
    def query_openai(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query OpenAI GPT-4o"""
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return response.choices[0].message.content, {
                "tokens": response.usage.total_tokens,
                "response_time_ms": response_time,
                "model": "gpt-4o"
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"OpenAI Error: {str(e)}", {"error": str(e)}
    
    def query_gemini(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query Google Gemini"""
        try:
            start_time = time.time()
            
            # Build conversation context
            chat = self.gemini_model.start_chat(history=[])
            response = chat.send_message(prompt)
            
            response_time = int((time.time() - start_time) * 1000)
            
            return response.text, {
                "tokens": len(prompt.split()) + len(response.text.split()),
                "response_time_ms": response_time,
                "model": "gemini-2.0-flash-exp"
            }
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"Gemini Error: {str(e)}", {"error": str(e)}
    
    def query_claude(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query Anthropic Claude"""
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=messages
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return response.content[0].text, {
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "response_time_ms": response_time,
                "model": "claude-sonnet-4"
            }
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return f"Claude Error: {str(e)}", {"error": str(e)}
    
    def query_deepseek(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query DeepSeek via API"""
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], {
                    "tokens": data['usage']['total_tokens'],
                    "response_time_ms": response_time,
                    "model": "deepseek-chat"
                }
            else:
                return f"DeepSeek Error: HTTP {response.status_code}", {"error": response.text}
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return f"DeepSeek Error: {str(e)}", {"error": str(e)}
    
    def query_grok(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query xAI Grok"""
        try:
            start_time = time.time()
            
            messages = conversation_history or []
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'], {
                    "tokens": data['usage']['total_tokens'],
                    "response_time_ms": response_time,
                    "model": "grok-beta"
                }
            else:
                return f"Grok Error: HTTP {response.status_code}", {"error": response.text}
        except Exception as e:
            logger.error(f"Grok error: {e}")
            return f"Grok Error: {str(e)}", {"error": str(e)}
    
    def query_huggingface(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[str, Dict]:
        """Query Hugging Face (Johnny's Digital Clone)"""
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
        Orchestrate responses from all LLMs
        
        Modes:
        - consensus: Get responses from all LLMs and synthesize
        - fastest: Return the first response
        - best: Use OpenAI to pick the best response
        - parallel: Show all responses side-by-side
        """
        
        results = {}
        
        # Query all LLMs in parallel (simulated)
        logger.info(f"Orchestrating '{mode}' response for prompt: {prompt[:100]}...")
        
        llm_queries = {
            "openai": self.query_openai,
            "gemini": self.query_gemini,
            "claude": self.query_claude,
            "deepseek": self.query_deepseek,
            "grok": self.query_grok,
            "huggingface": self.query_huggingface
        }
        
        # Execute all queries
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
        """Build a consensus response from all LLMs"""
        # Use OpenAI to synthesize all responses
        synthesis_prompt = f"""
You are the Conductor of a multi-AI orchestra. Review these responses from different AI models and create a unified, comprehensive answer.

Original Question: {original_prompt}

Responses:
"""
        for name, data in results.items():
            synthesis_prompt += f"\n\n{name.upper()}:\n{data['response']}\n"
        
        synthesis_prompt += "\n\nProvide a synthesized response that combines the best insights from all models:"
        
        final_response, metadata = self.query_openai(synthesis_prompt)
        
        return {
            "mode": "consensus",
            "final_response": final_response,
            "individual_responses": results,
            "metadata": metadata
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
        """Use OpenAI to determine the best response"""
        evaluation_prompt = f"""
Evaluate these AI responses and select the BEST one. Return only the name of the provider (openai, gemini, claude, deepseek, grok, or huggingface).

Original Question: {original_prompt}

Responses:
"""
        for name, data in results.items():
            evaluation_prompt += f"\n\n{name}: {data['response']}\n"
        
        evaluation_prompt += "\n\nWhich provider gave the best response? Reply with ONLY the provider name:"
        
        best_provider, _ = self.query_openai(evaluation_prompt)
        best_provider = best_provider.strip().lower()
        
        if best_provider in results:
            return {
                "mode": "best",
                "provider": best_provider,
                "response": results[best_provider]['response'],
                "metadata": results[best_provider]['metadata'],
                "all_responses": results
            }
        else:
            # Fallback to OpenAI
            return {
                "mode": "best",
                "provider": "openai",
                "response": results['openai']['response'],
                "metadata": results['openai']['metadata'],
                "all_responses": results
            }

