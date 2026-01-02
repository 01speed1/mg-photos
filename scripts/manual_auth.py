import urllib.parse
import urllib.request
import json
import sys

# Configuration
# NOTE: This must match exactly what was sent in the auth request, 
# even if we don't actually run a server on this port.
REDIRECT_URI = "http://localhost:8888" 
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
# Intentamos con el scope restringido a datos creados por la app.
# Si esto funciona, tendremos que crear el álbum DESDE la app.
SCOPE = "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"

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
    print("--- Google Photos Refresh Token Generator (Manual Mode) ---")
    print("This script helps you obtain a Refresh Token for your application.")
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
        'access_type': 'offline',
        'prompt': 'consent'
    }
    auth_url = f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    print(f"\n1. Open this URL in your browser:\n")
    print(f"{auth_url}\n")
    print("!!! IMPORTANTE !!!")
    print("Debes marcar TODAS las casillas de permisos en la pantalla de Google.")
    print("Si no seleccionas 'Ver y administrar tu biblioteca de Google Fotos', NO funcionará.")
    print("!!! IMPORTANTE !!!\n")
    print("2. Authorize the app.")
    print("3. You will be redirected to a 'localhost' page that might fail to load.")
    print("4. COPY the entire URL from your browser's address bar (even if it shows an error).")
    print("   It should look like: http://localhost:8888/?code=4/0A...")
    
    redirect_url = input("\nPaste the full redirected URL here: ").strip()

    # Extract code from URL
    try:
        parsed = urllib.parse.urlparse(redirect_url)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'code' not in qs:
            # Maybe they pasted just the code?
            if redirect_url.startswith("4/"):
                auth_code = redirect_url
            else:
                print("Error: Could not find 'code' parameter in the URL.")
                return
        else:
            auth_code = qs['code'][0]
    except Exception:
        # Fallback if they pasted just the code
        auth_code = redirect_url

    print(f"\nUsing code: {auth_code[:10]}...")

    # 3. Exchange Code for Tokens
    print("Exchanging code for tokens...")
    tokens = get_tokens(client_id, client_secret, auth_code)

    if 'refresh_token' in tokens:
        print("\nSUCCESS! Here are your tokens:")
        print("-" * 60)
        print(f"REFRESH TOKEN (Save this in config.json):\n{tokens['refresh_token']}")
        print("-" * 60)
        print(f"ACCESS TOKEN (Valid for 1 hour, use for testing curl):\n{tokens['access_token']}")
        print("-" * 60)
    else:
        print("\nError: No refresh_token returned.")
        print("Full response:", tokens)

if __name__ == "__main__":
    main()
