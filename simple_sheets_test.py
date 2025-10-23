#!/usr/bin/env python3
"""
Simple test of Google Sheets integration without Django
"""

import os
import sys

# Add the brain_chat directory to Python path
sys.path.append('/Users/johnny/Projects/holly_hot_box/brain_chat')

from google_sheets_utils import sheets_manager, create_law_firm_tracking_sheet, get_spreadsheet_url

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
