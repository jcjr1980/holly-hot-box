#!/usr/bin/env python3
"""
Test Google Sheets integration for Holly Hot Box
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/johnny/Projects/holly_hot_box')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')
django.setup()

from brain_chat.google_sheets_utils import sheets_manager, create_law_firm_tracking_sheet, get_spreadsheet_url

def test_google_sheets():
    """Test Google Sheets functionality"""
    print("🧪 Testing Google Sheets Integration...")
    
    # Test 1: Initialize service
    print("\n1️⃣ Testing service initialization...")
    if sheets_manager.service:
        print("✅ Google Sheets service initialized successfully")
    else:
        print("❌ Failed to initialize Google Sheets service")
        return False
    
    # Test 2: Create a test spreadsheet
    print("\n2️⃣ Testing spreadsheet creation...")
    test_title = "Test Law Firm Tracking - Holly Hot Box"
    spreadsheet_id = create_law_firm_tracking_sheet(test_title)
    
    if spreadsheet_id:
        print(f"✅ Created test spreadsheet with ID: {spreadsheet_id}")
        spreadsheet_url = get_spreadsheet_url(spreadsheet_id)
        print(f"📋 Spreadsheet URL: {spreadsheet_url}")
        
        # Test 3: Add sample data
        print("\n3️⃣ Testing data addition...")
        sample_firm = {
            'name': 'Test Law Firm',
            'attorneys': 'John Doe, Jane Smith',
            'specialties': 'Business Litigation, Contract Law',
            'website': 'https://testlawfirm.com',
            'phone': '(305) 555-0123',
            'email': 'contact@testlawfirm.com',
            'fee_structure': '33% contingency',
            'consultation_notes': 'Initial consultation completed',
            'case_assessment': 'Strong case, high potential',
            'pros': 'Experienced, responsive, good reputation',
            'cons': 'Higher fees, busy schedule',
            'follow_up_actions': 'Send case summary',
            'next_steps': 'Schedule follow-up meeting'
        }
        
        from brain_chat.google_sheets_utils import add_law_firm_to_sheet
        success = add_law_firm_to_sheet(spreadsheet_id, sample_firm)
        
        if success:
            print("✅ Successfully added sample law firm data")
        else:
            print("❌ Failed to add sample data")
            return False
        
        print(f"\n🎉 All tests passed! Check your spreadsheet: {spreadsheet_url}")
        return True
    else:
        print("❌ Failed to create test spreadsheet")
        return False

if __name__ == "__main__":
    success = test_google_sheets()
    if success:
        print("\n✅ Google Sheets integration is working perfectly!")
    else:
        print("\n❌ Google Sheets integration needs attention")
