#!/usr/bin/env python3
"""
Test script to isolate the orchestrator issue
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

def test_orchestrator():
    """Test the orchestrator with a simple prompt"""
    print("🧪 Testing LLM Orchestrator...")
    
    try:
        # Initialize orchestrator
        print("📦 Initializing orchestrator...")
        orchestrator = LLMOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test with simple prompt
        simple_prompt = "Hello, how are you today?"
        print(f"📝 Testing with prompt: '{simple_prompt}'")
        
        # Test consensus mode
        print("🔄 Testing consensus mode...")
        result = orchestrator.orchestrate_response(
            prompt=simple_prompt,
            conversation_history=[],
            mode="consensus"
        )
        
        print("✅ Orchestrator returned result:")
        print(f"Mode: {result.get('mode')}")
        print(f"Response: {result.get('response', 'No response key')}")
        print(f"Final Response: {result.get('final_response', 'No final_response key')}")
        print(f"Metadata: {result.get('metadata', 'No metadata')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_orchestrator()
    if success:
        print("\n🎉 Test passed!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
