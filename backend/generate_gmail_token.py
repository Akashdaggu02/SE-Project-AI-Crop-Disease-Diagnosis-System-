import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Please install required packages first:")
    print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    """Shows basic usage of the Gmail API.
    Log in via browser and print the Refresh Token.
    """
    creds = None
    
    if not os.path.exists('credentials.json'):
        print("\n\n=== ERROR: credentials.json NOT FOUND ===")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project & enable 'Gmail API'")
        print("3. Configure OAuth Consent Screen (External, Add Test Users)")
        print("4. Go to Credentials -> Create Credentials -> OAuth client ID")
        print("5. Choose 'Desktop app' -> Create")
        print("6. Download JSON and rename it to 'credentials.json' in this directory")
        sys.exit(1)

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print("\n\n" + "="*50)
    print("SUCCESS! 🎉 Here are your credentials for Render:")
    print("="*50)
    print(f"\nGMAIL_CLIENT_ID='{creds.client_id}'")
    print(f"GMAIL_CLIENT_SECRET='{creds.client_secret}'")
    print(f"GMAIL_REFRESH_TOKEN='{creds.refresh_token}'")
    print("\nCopy these 3 variables into your Render Environment Configuration!")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
