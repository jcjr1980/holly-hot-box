#!/usr/bin/env python
"""
Quick test script to verify API keys work correctly
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("API KEY VERIFICATION TEST")
print("=" * 60)

# Test OpenAI
print("\n1. Testing OpenAI...")
try:
    import openai
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"   ✓ API key found (length: {len(openai_key)})")
        client = openai.OpenAI(api_key=openai_key)
        print("   ✓ Client initialized successfully")
    else:
        print("   ✗ API key not found")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {str(e)}")

# Test Claude
print("\n2. Testing Claude...")
try:
    import anthropic
    claude_key = os.getenv('CLAUDE_API_KEY')
    if claude_key:
        print(f"   ✓ API key found (length: {len(claude_key)})")
        client = anthropic.Anthropic(api_key=claude_key)
        print("   ✓ Client initialized successfully")
    else:
        print("   ✗ API key not found")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {str(e)}")

# Test Gemini
print("\n3. Testing Gemini...")
try:
    import google.generativeai as genai
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"   ✓ API key found (length: {len(gemini_key)})")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("   ✓ Model initialized successfully")
    else:
        print("   ✗ API key not found")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

