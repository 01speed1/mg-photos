import urllib.request
import urllib.parse
import json
import sys

# Configuration
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
ALBUMS_ENDPOINT = "https://photoslibrary.googleapis.com/v1/albums"

def get_access_token(client_id, client_secret, refresh_token):
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')

    req = urllib.request.Request(TOKEN_ENDPOINT, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            resp_json = json.loads(response.read())
            return resp_json['access_token']
    except urllib.error.HTTPError as e:
        print(f"Error refreshing token: {e.read().decode()}")
        sys.exit(1)

def list_albums(access_token):
    req = urllib.request.Request(ALBUMS_ENDPOINT)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get('albums', [])
    except urllib.error.HTTPError as e:
        print(f"Error listing albums: {e.read().decode()}")
        sys.exit(1)

def main():
    print("--- Google Photos Album Lister ---")
    
    # Try to load from config.json if it exists, otherwise ask
    client_id = ""
    client_secret = ""
    refresh_token = ""
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            client_id = config.get('client_id', '')
            client_secret = config.get('client_secret', '')
            refresh_token = config.get('refresh_token', '')
            print("Loaded credentials from config.json")
    except FileNotFoundError:
        pass

    if not client_id:
        client_id = input("Enter Client ID: ").strip()
    if not client_secret:
        client_secret = input("Enter Client Secret: ").strip()
    if not refresh_token:
        refresh_token = input("Enter Refresh Token: ").strip()

    print("\nGetting access token...")
    access_token = get_access_token(client_id, client_secret, refresh_token)
    
    print("Fetching albums...")
    albums = list_albums(access_token)
    
    print("\nAvailable Albums:")
    print("-" * 60)
    for album in albums:
        print(f"Title: {album.get('title')}")
        print(f"ID:    {album.get('id')}")
        print("-" * 60)

if __name__ == "__main__":
    main()
