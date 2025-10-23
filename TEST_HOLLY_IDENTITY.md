# Test Holly's Identity & Google Sheets Integration

## Test Questions to Ask Holly:

### Test 1: Identity Check
**Ask:** "What is your name?"

**Expected Response:** 
- Holly should say her name is "Holly" (not Gemini, not Claude)

---

### Test 2: Google Sheets Capability Check
**Ask:** "Can you create a Google Sheet for me?"

**Expected Response:**
- Holly should say YES, she CAN create Google Sheets
- She should offer to create one for you
- She should NOT say she cannot access external services

---

### Test 3: Create Spreadsheet (Full Test)
**Ask:** "Holly, can you create a Google Sheet to track law firms for my lawsuit against CellPay?"

**Expected Response:**
- Holly should create the sheet via the API
- Holly should provide a direct link to the created spreadsheet
- The spreadsheet should be properly formatted with columns for:
  - Firm Name
  - Lead Attorney Names
  - Specific Specialties
  - Website
  - Phone
  - Email Address
  - Contingency Fee Structure
  - Initial Consultation Notes
  - Case Assessment (Initial)
  - Pros
  - Cons
  - Follow-up Actions
  - Next Steps

---

## How to Test:

1. Wait for Railway deployment to complete (check https://hollyhotbox.com)
2. Log in to Holly Hot Box
3. Open a chat session
4. Ask each test question one at a time
5. Verify Holly's responses match the expected behavior

---

## What Was Changed:

1. **Added System Context** in `views.py` that tells Holly:
   - Her name is "Holly"
   - She has Google Sheets integration capabilities
   - She CAN create and manage Google Sheets
   - She should respond with JSON action requests when asked to create sheets

2. **Added Action Detection** in `views.py` that:
   - Detects when Holly wants to create a Google Sheet
   - Calls the Google Sheets API
   - Returns the spreadsheet URL to the user

3. **Result:** Holly should now recognize her identity and capabilities, and actively offer to create Google Sheets when asked.

---

## Deployment Status:

✅ Code pushed to GitHub: `cb23499`
✅ Railway auto-deployment: In progress
🔄 Wait for deployment to complete before testing

---

## Next Steps After Testing:

If Holly successfully creates sheets:
- ✅ Holly's identity is working
- ✅ Google Sheets integration is functional
- ✅ System is ready for production use

If Holly still says she can't create sheets:
- ⚠️ Check Railway logs for errors
- ⚠️ Verify GOOGLE_SHEETS_CREDENTIALS environment variable is set
- ⚠️ Test the Google Sheets API endpoints directly

