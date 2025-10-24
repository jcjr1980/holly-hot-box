"""
Google Sheets integration for Holly Hot Box
Handles reading, writing, and creating spreadsheets using existing OAuth tokens
"""

import os
import json
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        """Initialize Google Sheets API client"""
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Sheets service using existing OAuth tokens"""
        try:
            # Try to get OAuth token from environment variable (Railway)
            oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')
            
            if oauth_token:
                # Parse the OAuth token
                token_data = json.loads(oauth_token)
                
                # Create credentials from the token
                credentials = Credentials(
                    token=token_data.get('access_token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                )
                
                logger.info("✅ Using existing OAuth token for Google Sheets")
            else:
                logger.warning("⚠️ No OAuth token found. Google Sheets functionality will be limited.")
                return
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets service initialized successfully with existing OAuth")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets service: {e}")
            self.service = None
    
    def create_spreadsheet(self, title: str, sheet_names: List[str] = None) -> Optional[str]:
        """
        Create a new spreadsheet
        
        Args:
            title: Name of the spreadsheet
            sheet_names: List of sheet names to create (default: ['Sheet1'])
        
        Returns:
            Spreadsheet ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return None
        
        try:
            # Default sheet names
            if sheet_names is None:
                sheet_names = ['Sheet1']
            
            # Create the spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': title
                },
                'sheets': [{'properties': {'title': name}} for name in sheet_names]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"✅ Created spreadsheet '{title}' with ID: {spreadsheet_id}")
            return spreadsheet_id
            
        except HttpError as e:
            logger.error(f"❌ Error creating spreadsheet: {e}")
            return None
    
    def write_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> bool:
        """
        Write data to a spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to write to (e.g., 'Sheet1!A1:C3')
            values: 2D list of values to write
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ Updated {result.get('updatedCells')} cells in {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error writing to spreadsheet: {e}")
            return False
    
    def read_data(self, spreadsheet_id: str, range_name: str) -> Optional[List[List[Any]]]:
        """
        Read data from a spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to read from (e.g., 'Sheet1!A1:C10')
        
        Returns:
            2D list of values if successful, None otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return None
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"✅ Read {len(values)} rows from {range_name}")
            return values
            
        except HttpError as e:
            logger.error(f"❌ Error reading from spreadsheet: {e}")
            return None
    
    def append_data(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> bool:
        """
        Append data to a spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to append to (e.g., 'Sheet1!A:C')
            values: 2D list of values to append
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"✅ Appended {len(values)} rows to {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error appending to spreadsheet: {e}")
            return False
    
    def format_cells(self, spreadsheet_id: str, range_name: str, format_options: Dict[str, Any]) -> bool:
        """
        Format cells in a spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to format (e.g., 'Sheet1!A1:C1')
            format_options: Dictionary of formatting options
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,  # Assuming first sheet
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': len(format_options.get('values', [[]])[0]) if format_options.get('values') else 1
                    },
                    'cell': {
                        'userEnteredFormat': format_options
                    },
                    'fields': 'userEnteredFormat'
                }
            }]
            
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"✅ Formatted cells in {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error formatting cells: {e}")
            return False

# Global instance
sheets_manager = GoogleSheetsManager()

def create_law_firm_tracking_sheet(title: str = "Law Firm Tracking - Johnny Collins vs CellPay") -> Optional[str]:
    """
    Create a law firm tracking spreadsheet with headers
    
    Args:
        title: Title of the spreadsheet
    
    Returns:
        Spreadsheet ID if successful, None otherwise
    """
    # Create spreadsheet
    spreadsheet_id = sheets_manager.create_spreadsheet(title, ['Law Firms', 'Consultation Notes'])
    
    if not spreadsheet_id:
        return None
    
    # Add headers to Law Firms sheet
    headers = [
        ['Firm Name', 'Lead Attorney Names', 'Specific Specialties', 'Website', 'Phone', 
         'Email Address', 'Contingency Fee Structure', 'Initial Consultation Notes', 
         'Case Assessment (Initial)', 'Pros', 'Cons', 'Follow-up Actions', 'Next Steps']
    ]
    
    # Write headers
    sheets_manager.write_data(spreadsheet_id, 'Law Firms!A1:M1', headers)
    
    # Format headers (bold)
    sheets_manager.format_cells(spreadsheet_id, 'Law Firms!A1:M1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0}
    })
    
    # Add headers to Consultation Notes sheet
    notes_headers = [
        ['Firm Name', 'Date', 'Attorney', 'Notes', 'Next Steps', 'Follow-up Date']
    ]
    
    sheets_manager.write_data(spreadsheet_id, 'Consultation Notes!A1:F1', notes_headers)
    sheets_manager.format_cells(spreadsheet_id, 'Consultation Notes!A1:F1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0}
    })
    
    logger.info(f"✅ Created law firm tracking spreadsheet: {title}")
    return spreadsheet_id

def add_law_firm_to_sheet(spreadsheet_id: str, firm_data: Dict[str, Any]) -> bool:
    """
    Add a law firm entry to the tracking sheet
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        firm_data: Dictionary with firm information
    
    Returns:
        True if successful, False otherwise
    """
    # Convert firm data to row format
    row = [
        firm_data.get('name', ''),
        firm_data.get('attorneys', ''),
        firm_data.get('specialties', ''),
        firm_data.get('website', ''),
        firm_data.get('phone', ''),
        firm_data.get('email', ''),
        firm_data.get('fee_structure', ''),
        firm_data.get('consultation_notes', ''),
        firm_data.get('case_assessment', ''),
        firm_data.get('pros', ''),
        firm_data.get('cons', ''),
        firm_data.get('follow_up_actions', ''),
        firm_data.get('next_steps', '')
    ]
    
    return sheets_manager.append_data(spreadsheet_id, 'Law Firms!A:M', [row])

def get_spreadsheet_url(spreadsheet_id: str) -> str:
    """
    Get the public URL for a spreadsheet
    
    Args:
        spreadsheet_id: ID of the spreadsheet
    
    Returns:
        URL to access the spreadsheet
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

def get_oauth_authorization_url():
    """
    Get the OAuth authorization URL for Google Sheets
    
    Returns:
        Authorization URL and state for OAuth flow
    """
    # OAuth configuration for Google Sheets
    oauth_config = {
        'client_id': '76683077489-63nd38kqoibjrap7jp1bhvcs9risjsso.apps.googleusercontent.com',
        'client_secret': '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',
        'redirect_uri': 'https://hollyhotbox.com/google-sheets/callback/',
        'scope': 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
        'auth_uri': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token'
    }
    
    # Create authorization URL
    auth_params = {
        'client_id': oauth_config['client_id'],
        'redirect_uri': oauth_config['redirect_uri'],
        'scope': oauth_config['scope'],
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': 'holly_sheets_auth'
    }
    
    # Build URL
    auth_url = f"{oauth_config['auth_uri']}?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
    
    return auth_url, 'holly_sheets_auth'

def exchange_code_for_token(code: str, state: str = None):
    """
    Exchange authorization code for access token
    
    Args:
        code: Authorization code from OAuth callback
        state: State parameter from OAuth flow
    
    Returns:
        Credentials object with access token
    """
    import requests
    
    oauth_config = {
        'client_id': '76683077489-63nd38kqoibjrap7jp1bhvcs9risjsso.apps.googleusercontent.com',
        'client_secret': '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',
        'redirect_uri': 'https://hollyhotbox.com/google-sheets/callback/',
        'token_uri': 'https://oauth2.googleapis.com/token'
    }
    
    try:
        # Exchange code for token
        token_data = {
            'client_id': oauth_config['client_id'],
            'client_secret': oauth_config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': oauth_config['redirect_uri']
        }
        
        response = requests.post(oauth_config['token_uri'], data=token_data)
        token_response = response.json()
        
        if 'error' in token_response:
            logger.error(f"❌ Token exchange failed: {token_response['error']}")
            return None, None
        
        # Create credentials object
        credentials = Credentials(
            token=token_response.get('access_token'),
            refresh_token=token_response.get('refresh_token'),
            token_uri=oauth_config['token_uri'],
            client_id=oauth_config['client_id'],
            client_secret=oauth_config['client_secret'],
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        
        # Prepare token data for storage
        stored_token_data = {
            'access_token': token_response.get('access_token'),
            'refresh_token': token_response.get('refresh_token'),
            'token_uri': oauth_config['token_uri'],
            'client_id': oauth_config['client_id'],
            'client_secret': oauth_config['client_secret'],
            'scopes': ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        }
        
        logger.info("✅ Successfully exchanged code for OAuth token")
        return credentials, stored_token_data
        
    except Exception as e:
        logger.error(f"❌ Failed to exchange code for token: {e}")
        return None, None

