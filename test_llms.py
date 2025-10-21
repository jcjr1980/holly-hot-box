#!/usr/bin/env python3
"""
Test script to verify all LLMs are working individually
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')
django.setup()

from brain_chat.llm_orchestrator import LLMOrchestrator

def test_individual_llms():
    """Test each LLM individually"""
    print("🧪 TESTING ALL LLMs INDIVIDUALLY")
    print("=" * 50)
    
    orchestrator = LLMOrchestrator()
    test_prompt = "Hello! Please respond with just 'LLM_NAME is working' to confirm you're functioning."
    
    # Test each LLM
    llms_to_test = [
        ("Gemini", orchestrator.query_gemini),
        ("DeepSeek", orchestrator.query_deepseek),
        ("Claude", orchestrator.query_claude),
        ("OpenAI", orchestrator.query_openai),
        ("Grok", orchestrator.query_grok),
        ("HuggingFace", orchestrator.query_huggingface)
    ]
    
    results = {}
    
    for llm_name, query_func in llms_to_test:
        print(f"\n🔍 Testing {llm_name}...")
        try:
            response, metadata = query_func(test_prompt)
            
            if response and not response.startswith('Error:'):
                print(f"✅ {llm_name}: WORKING")
                print(f"   Response: {response[:100]}...")
                print(f"   Metadata: {metadata}")
                results[llm_name] = "WORKING"
            else:
                print(f"❌ {llm_name}: FAILED")
                print(f"   Error: {response}")
                results[llm_name] = "FAILED"
                
        except Exception as e:
            print(f"❌ {llm_name}: EXCEPTION")
            print(f"   Exception: {str(e)}")
            results[llm_name] = "EXCEPTION"
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    working_count = 0
    for llm_name, status in results.items():
        status_icon = "✅" if status == "WORKING" else "❌"
        print(f"{status_icon} {llm_name}: {status}")
        if status == "WORKING":
            working_count += 1
    
    print(f"\n🎯 WORKING LLMs: {working_count}/{len(results)}")
    
    if working_count == len(results):
        print("🎉 ALL LLMs ARE WORKING!")
    elif working_count > 0:
        print("⚠️  SOME LLMs ARE WORKING")
    else:
        print("🚨 NO LLMs ARE WORKING - CHECK API KEYS")

if __name__ == "__main__":
    test_individual_llms()
