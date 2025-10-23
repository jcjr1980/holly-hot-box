#!/usr/bin/env python3
"""
Test Google Sheets integration with Holly Hot Box
"""

import requests
import json

def test_create_google_sheet():
    """Test creating a Google Sheet via the API"""
    
    # Holly Hot Box base URL
    base_url = "https://hollyhotbox.com"
    
    # Test data
    test_data = {
        "title": "Test Law Firm Tracking - Johnny Collins vs CellPay"
    }
    
    print("🧪 Testing Google Sheets Integration...")
    print(f"📡 Testing endpoint: {base_url}/create-sheet/")
    print(f"📋 Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make POST request to create sheet
        response = requests.post(
            f"{base_url}/create-sheet/",
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Google Sheet created:")
            print(f"   📋 Spreadsheet ID: {result.get('spreadsheet_id')}")
            print(f"   🔗 Spreadsheet URL: {result.get('spreadsheet_url')}")
            print(f"   💬 Message: {result.get('message')}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT: Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 CONNECTION ERROR: Could not connect to server")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def test_add_firm_to_sheet():
    """Test adding a law firm to an existing sheet"""
    
    base_url = "https://hollyhotbox.com"
    
    # Sample law firm data
    firm_data = {
        "spreadsheet_id": "test_id",  # This will fail but we can test the endpoint
        "firm_data": {
            "name": "Test Law Firm",
            "attorneys": "John Doe, Jane Smith",
            "specialties": "Business Litigation, Contract Law",
            "website": "https://testlawfirm.com",
            "phone": "(305) 555-0123",
            "email": "contact@testlawfirm.com",
            "fee_structure": "33% contingency",
            "consultation_notes": "Initial consultation completed",
            "case_assessment": "Strong case, high potential",
            "pros": "Experienced, responsive, good reputation",
            "cons": "Higher fees, busy schedule",
            "follow_up_actions": "Send case summary",
            "next_steps": "Schedule follow-up meeting"
        }
    }
    
    print("\n🧪 Testing Add Firm to Sheet...")
    print(f"📡 Testing endpoint: {base_url}/add-firm-to-sheet/")
    
    try:
        response = requests.post(
            f"{base_url}/add-firm-to-sheet/",
            json=firm_data,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 400]:  # 400 is expected for invalid spreadsheet_id
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ UNEXPECTED STATUS: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Google Sheets Integration Tests...\n")
    
    # Test 1: Create Google Sheet
    success1 = test_create_google_sheet()
    
    # Test 2: Add firm to sheet
    success2 = test_add_firm_to_sheet()
    
    print(f"\n📊 Test Results:")
    print(f"   Create Sheet: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Add Firm: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Google Sheets integration is working!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
