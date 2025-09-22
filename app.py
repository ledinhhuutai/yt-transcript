from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse, parse_qs
from yt_transcript.fetch import get_transcript

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_video_id(url_or_id: str) -> str:
    """
    Extract video ID from YouTube URL or return the ID if it's already a video ID
    """
    # If it's already a video ID (11 characters, alphanumeric and some special chars)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # Try parsing as URL and extracting v parameter
    try:
        parsed_url = urlparse(url_or_id)
        if parsed_url.query:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
    except:
        pass
    
    return None

@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint with API documentation
    """
    return jsonify({
        "message": "YouTube Transcript API",
        "endpoints": {
            "/transcript": {
                "methods": ["GET", "POST"],
                "description": "Get YouTube video transcript with automatic language detection",
                "parameters": {
                    "url": "YouTube video URL (optional if video_id provided)",
                    "video_id": "YouTube video ID (optional if url provided)",
                    "languages": "Comma-separated language codes (optional, defaults to 'en,vi,zh,es,fr,de,ja,ko')"
                },
                "examples": {
                    "GET": "/transcript?url=https://www.youtube.com/watch?v=VIDEO_ID&languages=en,vi",
                    "POST": '{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "languages": ["en", "vi"]}'
                },
                "supported_languages": ["en", "vi", "zh", "es", "fr", "de", "ja", "ko", "and many more"]
            }
        },
        "examples": {
            "GET": "/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "POST": "Send JSON with 'url' or 'video_id' field"
        }
    })

@app.route("/transcript", methods=["GET", "POST"])
def get_transcript_endpoint():
    """
    Get transcript for a YouTube video
    Accepts both GET and POST requests
    """
    try:
        # Handle both GET and POST requests
        if request.method == "GET":
            url = request.args.get("url")
            video_id = request.args.get("video_id")
            languages = request.args.get('languages', 'en,vi,zh,es,fr,de,ja,ko').split(',')
        else:  # POST
            data = request.get_json() or {}
            url = data.get("url")
            video_id = data.get("video_id")
            languages = data.get('languages', ['en', 'vi', 'zh', 'es', 'fr', 'de', 'ja', 'ko'])
            if isinstance(languages, str):
                languages = languages.split(',')
        
        # Determine video ID
        if url:
            video_id = extract_video_id(url)
        elif video_id:
            video_id = extract_video_id(video_id)
        
        if not video_id:
            return jsonify({
                "success": False,
                "error": "Missing or invalid YouTube URL/video ID",
                "message": "Please provide a valid YouTube URL or video ID"
            }), 400
        
        # Get transcript with language preferences
        transcript_data = get_transcript(video_id, languages)
        
        # Format transcript for easier consumption
        formatted_transcript = []
        full_text = ""
        
        for entry in transcript_data:
            formatted_entry = {
                "start": round(entry.start, 2),
                "duration": round(entry.duration, 2),
                "text": entry.text.strip()
            }
            formatted_transcript.append(formatted_entry)
            full_text += entry.text.strip() + " "
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "transcript": formatted_transcript,
            "full_text": full_text.strip(),
            "total_entries": len(formatted_transcript)
        })
        
    except Exception as e:
        error_message = str(e)
        
        # Provide more specific error messages
        if "No transcript found" in error_message:
            return jsonify({
                "success": False,
                "error": "No transcript available",
                "message": "This video doesn't have a transcript available or subtitles are disabled"
            }), 404
        elif "Video unavailable" in error_message:
            return jsonify({
                "success": False,
                "error": "Video unavailable",
                "message": "The video is private, deleted, or doesn't exist"
            }), 404
        else:
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": error_message
            }), 500

if __name__ == "__main__":
    print("Starting YouTube Transcript API server...")
    print("Server will be available at: http://localhost:5001")
    print("API Documentation: http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)