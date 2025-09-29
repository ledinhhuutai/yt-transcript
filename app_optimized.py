from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
from urllib.parse import urlparse, parse_qs
from yt_transcript.fetch import get_transcript
import gc
import os

app = Flask(__name__)
CORS(app)

# Tối ưu cho VPS yếu
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
        "message": "YouTube Transcript API - Optimized for Low Resource VPS",
        "status": "running",
        "endpoints": {
            "/transcript": "GET/POST - Get YouTube video transcript"
        }
    })

@app.route("/transcript", methods=["GET", "POST"])
def get_transcript_endpoint():
    """
    Get transcript for a YouTube video - Optimized version
    """
    try:
        # Handle both GET and POST requests
        if request.method == "GET":
            url = request.args.get("url")
            video_id = request.args.get("video_id")
            languages = request.args.get('languages', 'en,vi').split(',')
        else:  # POST
            data = request.get_json() or {}
            url = data.get("url")
            video_id = data.get("video_id")
            languages = data.get('languages', ['en', 'vi'])
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
                "error": "Missing or invalid YouTube URL/video ID"
            }), 400
        
        # Get transcript using optimized function
        result = get_transcript(video_id, languages)
        
        # Force garbage collection để giải phóng memory
        gc.collect()
        
        return jsonify(result)
        
    except Exception as e:
        # Force garbage collection khi có lỗi
        gc.collect()
        
        error_message = str(e).lower()
        if "could not retrieve a transcript" in error_message:
            return jsonify({
                "success": False,
                "error": "No transcript available",
                "message": "This video doesn't have transcripts in the requested languages"
            }), 404
        elif "video unavailable" in error_message or "private" in error_message:
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
    # Cấu hình tối ưu cho VPS yếu
    print("Starting YouTube Transcript API server (Optimized for Low Resource VPS)...")
    print("Server will be available at: http://localhost:5001")
    
    # Chạy với threaded=False để tiết kiệm RAM
    app.run(
        host="0.0.0.0", 
        port=5001, 
        debug=False,  # Tắt debug mode để tiết kiệm tài nguyên
        threaded=False,  # Tắt threading để tiết kiệm RAM
        processes=1  # Chỉ chạy 1 process
    )