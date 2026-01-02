import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import webbrowser
import sys

# Configuration
REDIRECT_PORT = 8888
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/photoslibrary.readonly"

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            
            # Send a nice response to the browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization Successful!</h1><p>You can close this window and return to the terminal.</p></body></html>")
        else:
            self.send_response(400)
            self.wfile.write(b"Authorization failed.")

def get_tokens(client_id, client_secret, auth_code):
    data = urllib.parse.urlencode({
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }).encode('utf-8')

    req = urllib.request.Request(TOKEN_ENDPOINT, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"Error exchanging code for token: {e.read().decode()}")
        sys.exit(1)

def main():
    print("--- Google Photos Refresh Token Generator ---")
    print("This script helps you obtain a Refresh Token for your application.")
    print("Ensure you have created OAuth 2.0 credentials (Desktop App) in Google Cloud Console.")
    print("")

    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Secret are required.")
        return

    # 1. Construct Authorization URL
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline', # Crucial for refresh_token
        'prompt': 'consent'       # Force consent to ensure refresh_token is returned
    }
    auth_url = f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    # 2. Start Local Server to catch callback
    print(f"\nOpening browser to authorize...")
    print(f"If it doesn't open, visit this URL manually:\n{auth_url}\n")

    webbrowser.open(auth_url)

    with socketserver.TCPServer(("", REDIRECT_PORT), OAuthHandler) as httpd:
        print(f"Waiting for callback on port {REDIRECT_PORT}...")
        # Handle a single request then shutdown
        httpd.handle_request()
        if hasattr(httpd, 'auth_code'):
            auth_code = httpd.auth_code
            print("\nAuthorization code received!")
        else:
            print("\nFailed to receive authorization code.")
            return

    # 3. Exchange Code for Tokens
    print("Exchanging code for tokens...")
    tokens = get_tokens(client_id, client_secret, auth_code)

    if 'refresh_token' in tokens:
        print("\nSUCCESS! Here is your Refresh Token:")
        print("-" * 60)
        print(tokens['refresh_token'])
        print("-" * 60)
        print("Save this token, your Client ID, and Client Secret in your config file.")
    else:
        print("\nError: No refresh_token returned. Did you already authorize this app?")
        print("Try revoking access in your Google Account permissions or use 'prompt=consent' (already included).")
        print("Full response:", tokens)

if __name__ == "__main__":
    main()
