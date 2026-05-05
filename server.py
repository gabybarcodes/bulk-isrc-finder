1#!/usr/bin/env python3
import os
import json
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from pathlib import Path
import threading

# Configuration
API_KEY = os.getenv('SOUNDCHARTS_API_KEY', '7572e7631869825b')
APP_ID = os.getenv('SOUNDCHARTS_APP_ID', 'GBARROETA-API_72B0C865')
SOUNDCHARTS_BASE = 'https://api.soundcharts.com'
CUSTOMER_API_BASE = 'https://customer.api.soundcharts.com'
DEEZER_BASE = 'https://api.deezer.com'
PORT = int(os.getenv('PORT', 3000))
PUBLIC_DIR = Path(__file__).parent / 'public'
DEFAULT_API = os.getenv('DEFAULT_API', 'deezer')  # deezer or soundcharts

class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Health check
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'api': 'deezer'
            }).encode())
            return
        
        # Serve static files
        if self.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/bulk-search':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                data = json.loads(body)
                songs = data.get('songs', [])
                
                results = []
                for song in songs:
                    result = search_song(song)
                    results.append(result)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'results': results}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        
        # 404
        self.send_response(404)
        self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def translate_path(self, path):
        # Serve from public directory
        path = urlparse(path).path
        if path.startswith('/'):
            path = path[1:]
        full_path = PUBLIC_DIR / path
        
        if full_path.is_file():
            return str(full_path)
        elif full_path.is_dir():
            return str(full_path / 'index.html')
        return str(full_path)

def search_song(song):
    """Search for a song on Deezer API and return ISRC"""
    return search_deezer(song)

def search_deezer(song):
    """Search using Deezer API (free, no auth required)"""
    try:
        query = f"{song['title']} {song['artist']}"
        search_url = f"{DEEZER_BASE}/search"
        params = {'q': query, 'limit': 5}
        
        search_response = requests.get(search_url, params=params, timeout=10)
        
        if search_response.status_code != 200:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': f'Search failed: {search_response.status_code}'
            }
        
        search_data = search_response.json()
        results = search_data.get('data', [])
        
        if not results:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': 'Song not found in Deezer'
            }
        
        # Return first matching result
        track = results[0]
        
        # Try to get additional metadata from Soundcharts if available
        labels = None
        distributor = None
        soundcharts_release_date = None
        
        if API_KEY and APP_ID:
            try:
                isrc = track.get('isrc')
                if isrc:
                    labels, distributor, soundcharts_release_date = fetch_soundcharts_metadata(isrc)
            except Exception as e:
                pass  # Silently fail if Soundcharts lookup doesn't work
        
        # Get release date from album if available
        release_date = soundcharts_release_date
        if not release_date:
            # Try to get from album
            album = track.get('album', {})
            if isinstance(album, dict):
                release_date = album.get('release_date')
            if not release_date:
                release_date = track.get('release_date')
        
        return {
            'input': f"{song['title']} - {song['artist']}",
            'found': True,
            'title': track.get('title', song['title']),
            'artist': track.get('artist', {}).get('name', song['artist']),
            'isrc': track.get('isrc'),
            'releaseDate': release_date,
            'labels': labels,
            'distributor': distributor,
            'api': 'deezer',
            'preview': track.get('preview_url')
        }
    
    except Exception as e:
        return {
            'input': f"{song['title']} - {song['artist']}",
            'found': False,
            'error': f'Deezer error: {str(e)}'
        }

def fetch_soundcharts_metadata(isrc):
    """Fetch metadata from Soundcharts API by ISRC - returns (labels, distributor, releaseDate)"""
    if not API_KEY or not APP_ID:
        return None, None, None
    
    try:
        headers = {
            'x-app-id': APP_ID,
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Get song by ISRC
        isrc_url = f"{CUSTOMER_API_BASE}/api/v2.25/song/by-isrc/{isrc}"
        response = requests.get(isrc_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, None, None
        
        song_data = response.json().get('object')
        if not song_data:
            return None, None, None
        
        # Extract labels
        labels = None
        labels_list = song_data.get('labels', [])
        if labels_list:
            labels = ', '.join([label.get('name', '') for label in labels_list if label.get('name')])
            if not labels:
                labels = None
        
        # Extract distributor
        distributor = song_data.get('distributor')
        
        # Extract and format release date
        release_date = None
        release_date_str = song_data.get('releaseDate')
        if release_date_str:
            try:
                # Parse ISO format and return just the date
                release_date = release_date_str.split('T')[0]
            except:
                release_date = release_date_str
        
        return labels, distributor, release_date
    
    except Exception as e:
        # Silently fail
        return None, None, None

def search_soundcharts(song):
    """Search using Soundcharts API (requires API key)"""
    try:
        query = f"{song['title']} {song['artist']}"
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Search for song
        search_url = f"{SOUNDCHARTS_BASE}/api/v2/song/search/{quote(query)}"
        search_response = requests.get(search_url, headers=headers, timeout=10)
        
        if search_response.status_code != 200:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': f'Search failed: {search_response.status_code}'
            }
        
        search_results = search_response.json().get('data', [])
        
        if not search_results:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': 'Song not found in Soundcharts'
            }
        
        first_result = search_results[0]
        
        # Try to get metadata with ISRC
        try:
            metadata_url = f"{SOUNDCHARTS_BASE}/api/v2.25/song/{first_result['id']}"
            metadata_response = requests.get(metadata_url, headers=headers, timeout=10)
            
            if metadata_response.status_code == 200:
                metadata = metadata_response.json().get('data', first_result)
            else:
                metadata = first_result
        except:
            metadata = first_result
        
        return {
            'input': f"{song['title']} - {song['artist']}",
            'found': True,
            'title': metadata.get('title', first_result.get('title')),
            'artist': metadata.get('artist', {}).get('name', song['artist']) if isinstance(metadata.get('artist'), dict) else song['artist'],
            'isrc': metadata.get('isrc'),
            'releaseDate': metadata.get('release_date'),
            'api': 'soundcharts'
        }
    
    except Exception as e:
        return {
            'input': f"{song['title']} - {song['artist']}",
            'found': False,
            'error': f'Soundcharts error: {str(e)}'
        }

def run_server():
    os.chdir(PUBLIC_DIR)
    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    print(f"🎵 ISRC Lookup with Label Finder running on http://0.0.0.0:{PORT}")
    print(f"✓ Powered by Deezer API + Soundcharts Label Finder")
    print(f"📡 Accessible from other devices on your network!")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
