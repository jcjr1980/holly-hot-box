#!/usr/bin/env python3
"""
Test script to directly call the chat API and see raw responses
"""
import requests
import json

# Test with the complex lawsuit query
test_query = """Based on my Cellpay lawsuit situation, can you: 1) Identify the key legal issues, 2) Find Miami law firms that handle contract disputes on contingency, 3) Assess what makes my case attractive to contingency lawyers?"""

url = "https://hollyhotbox.com/send-message/"

# You'll need to get a valid session cookie first by logging in
# For now, let's just see what error we get

payload = {
    "message": test_query,
    "mode": "consensus",
    "session_id": None
}

headers = {
    "Content-Type": "application/json",
}

print("🔄 Sending request to Holly Hot Box API...")
print(f"Query: {test_query[:100]}...")
print(f"Mode: consensus\n")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📊 Content-Type: {response.headers.get('content-type')}")
    print(f"📊 Response Length: {len(response.text)} chars\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ ERROR {response.status_code}")
        print("Raw response:")
        print(response.text[:1000])  # First 1000 chars
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print("\n📋 Error Details:")
            print(json.dumps(error_data, indent=2))
        except:
            print("\n⚠️ Response is not JSON (likely HTML error page)")
            
except requests.exceptions.Timeout:
    print("⏰ Request timed out after 60 seconds")
except Exception as e:
    print(f"💥 Exception: {type(e).__name__}: {str(e)}")

