from flask import Flask, render_template, request, jsonify
from mastodon import Mastodon
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import json
import os
import time
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Load Mastodon access token
with open('token.secret', 'r') as f:
    access_token = f.read().strip()

def get_mastodon():
    """Initialize Mastodon client"""
    return Mastodon(
        access_token=access_token,
        api_base_url=config['mastodon_api_base_url']
    )

# Initialize YouTube API
def init_youtube_api():
    """Initialize YouTube API using OAuth credentials"""
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    credentials = None
    TOKEN_FILE = 'token.json'
    
    # Check if we have a saved token
    if os.path.exists(TOKEN_FILE):
        credentials = UserCredentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, perform OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('youtube_credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Save the token for future runs
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())
    
    return googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

# Create or get playlist
def create_or_get_playlist(youtube, playlist_name="TuesdayTracks"):
    """Create a new playlist or get existing one"""
    # Check for existing playlists
    request = youtube.playlists().list(
        part='snippet',
        mine=True,
        maxResults=25
    )
    
    while request:
        response = request.execute()
        for item in response.get('items', []):
            if item['snippet']['title'] == playlist_name:
                return item['id']
        
        if 'nextPageToken' in response:
            request = youtube.playlists().list(
                part='snippet',
                mine=True,
                pageToken=response['nextPageToken'],
                maxResults=25
            )
        else:
            break
    
    # Create new playlist if not found
    request = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': playlist_name,
                'description': 'Tuesday Tracks from Mastodon'
            },
            'status': {
                'privacyStatus': 'private'
            }
        }
    )
    response = request.execute()
    playlist_id = response['id']
    time.sleep(2)  # Give YouTube API time to propagate the new playlist
    return playlist_id

# Get all videos currently in playlist
def get_playlist_videos(youtube, playlist_id):
    """Get all video IDs currently in the playlist"""
    video_ids = set()
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    
    try:
        while request:
            response = request.execute()
            for item in response.get('items', []):
                video_ids.add(item['snippet']['resourceId']['videoId'])
            
            if 'nextPageToken' in response:
                request = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    pageToken=response['nextPageToken'],
                    maxResults=50
                )
            else:
                break
    except HttpError as e:
        if e.resp.status == 404:
            print(f"Playlist not found or still initializing. Returning empty list.")
        else:
            print(f"Error fetching playlist videos: {e}")
    
    return video_ids

# Add song to playlist (if not already there)
def add_to_playlist(youtube, playlist_id, video_id, existing_videos):
    """Add a video to playlist if it's not already there"""
    if video_id in existing_videos:
        return False
    
    try:
        request = youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        response = request.execute()
        existing_videos.add(video_id)
        return True
    except Exception as e:
        print(f"Error adding video {video_id}: {e}")
        return False

# Extract video ID from YouTube URL
def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    ydl = YoutubeDL({'quiet': True, 'no_warnings': True})
    try:
        info = ydl.extract_info(url, download=False)
        return info['id']
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    """Create playlist and process hashtag"""
    try:
        data = request.json
        playlist_name = data.get('playlistName', 'TuesdayTracks')
        hashtag = data.get('hashtag', 'TuesdayTracks')
        
        # Initialize YouTube API
        youtube = init_youtube_api()
        
        # Create or get playlist
        playlist_id = create_or_get_playlist(youtube, playlist_name)
        existing_videos = get_playlist_videos(youtube, playlist_id)
        
        # Get timeline from Mastodon
        mastodon = get_mastodon()
        timeline = mastodon.timeline_hashtag(hashtag)
        
        added_count = 0
        skipped_count = 0
        
        for status in timeline:
            card = status.get("card")
            if card and "url" in card:
                url = card["url"]
                if "youtube.com" in url or "youtu.be" in url:
                    video_id = extract_video_id(url)
                    if video_id:
                        if add_to_playlist(youtube, playlist_id, video_id, existing_videos):
                            added_count += 1
                        else:
                            skipped_count += 1
        
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        return jsonify({
            'success': True,
            'playlistId': playlist_id,
            'playlistUrl': playlist_url,
            'playlistName': playlist_name,
            'addedCount': added_count,
            'skippedCount': skipped_count
        })
    except Exception as e:
        error_message = str(e)
        print(f"Error in create_playlist: {error_message}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_message
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
