#!/usr/bin/env python3
import os
import json
import time
import base64
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from pathlib import Path
import threading
from distributor_mapping import get_major_group

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '2a57e99a627e4443b20a0ac81d92120e')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '77cbceff91cb46c6b6e60077a1e15906')
SPOTIFY_BASE = 'https://api.spotify.com/v1'
DEEZER_BASE = 'https://api.deezer.com'
PORT = int(os.getenv('PORT', 3000))
PUBLIC_DIR = Path(__file__).parent / 'public'

_spotify_token = {'value': None, 'expires_at': 0}


class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'api': 'deezer+spotify'}).encode())
            return

        if self.path == '/':
            self.path = '/index.html'

        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/search-single':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
                song = data.get('song', {})
                result = search_song(song)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return

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

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def translate_path(self, path):
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
    return search_deezer(song)


def get_spotify_token():
    """Return a cached Spotify client-credentials token, refreshing when expired."""
    if _spotify_token['value'] and time.time() < _spotify_token['expires_at'] - 60:
        return _spotify_token['value']
    credentials = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers={
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data='grant_type=client_credentials',
        timeout=10,
    )
    if response.status_code != 200:
        return None
    data = response.json()
    _spotify_token['value'] = data['access_token']
    _spotify_token['expires_at'] = time.time() + data['expires_in']
    return _spotify_token['value']


def fetch_spotify_label(isrc):
    """Fetch label info from Spotify by ISRC. Returns (label_name, major_group, release_date)."""
    try:
        token = get_spotify_token()
        if not token:
            return None, None, None

        headers = {'Authorization': f'Bearer {token}'}

        search_resp = requests.get(
            f'{SPOTIFY_BASE}/search',
            headers=headers,
            params={'q': f'isrc:{isrc}', 'type': 'track', 'limit': 1},
            timeout=10,
        )
        if search_resp.status_code != 200:
            return None, None, None

        tracks = search_resp.json().get('tracks', {}).get('items', [])
        if not tracks:
            return None, None, None

        track = tracks[0]
        album = track.get('album', {})
        album_id = album.get('id')
        release_date = album.get('release_date')

        if not album_id:
            return None, None, release_date

        album_resp = requests.get(
            f'{SPOTIFY_BASE}/albums/{album_id}',
            headers=headers,
            timeout=10,
        )
        if album_resp.status_code != 200:
            return None, None, release_date

        album_data = album_resp.json()
        label_name = album_data.get('label')
        if not release_date:
            release_date = album_data.get('release_date')

        if not label_name:
            return None, None, release_date

        # Also extract copyright text — it often names the parent major group
        # e.g. "7CULT/B1 Recordings GmbH, a Sony Music Entertainment Company"
        copyright_text = ' '.join(
            c.get('text', '') for c in album_data.get('copyrights', [])
        )

        major_group = get_major_group(label_name, copyright_text)
        return label_name, major_group, release_date

    except Exception:
        return None, None, None


def search_deezer(song):
    """Search using Deezer API (free, no auth) then enrich with Spotify label data."""
    try:
        query = f"{song['title']} {song['artist']}"
        search_resp = requests.get(
            f'{DEEZER_BASE}/search',
            params={'q': query, 'limit': 5},
            timeout=10,
        )

        if search_resp.status_code != 200:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': f'Search failed: {search_resp.status_code}',
            }

        results = search_resp.json().get('data', [])
        if not results:
            return {
                'input': f"{song['title']} - {song['artist']}",
                'found': False,
                'error': 'Song not found in Deezer',
            }

        track = results[0]
        isrc = track.get('isrc')

        labels = None
        distributor = None
        release_date = None

        if isrc:
            labels, distributor, release_date = fetch_spotify_label(isrc)

        if not release_date:
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
            'isrc': isrc,
            'releaseDate': release_date,
            'labels': labels,
            'distributor': distributor,
            'api': 'deezer+spotify',
            'preview': track.get('preview_url'),
        }

    except Exception as e:
        return {
            'input': f"{song['title']} - {song['artist']}",
            'found': False,
            'error': f'Error: {str(e)}',
        }


def run_server():
    os.chdir(PUBLIC_DIR)
    server = HTTPServer(('0.0.0.0', PORT), APIHandler)
    print(f"ISRC Lookup running on http://0.0.0.0:{PORT}")
    print(f"Powered by Deezer API + Spotify Label Finder")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
