from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
import re
import os
import json
import time
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
                    "languages": "Comma-separated language codes (optional, defaults to 'en,vi,zh,es,fr,de,ja,ko')",
                    "language": "Single language code to force output in that language (e.g., 'en')",
                    "force": "Force translation to the requested language if original not available (default: true when 'language' provided)"
                },
                "examples": {
                    "GET": "/transcript?url=https://www.youtube.com/watch?v=VIDEO_ID&language=en&force=true",
                    "POST": '{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "language": "en", "force": true}'
                },
                "supported_languages": ["en", "vi", "zh", "es", "fr", "de", "ja", "ko", "and many more"]
            }
        },
        "examples": {
            "GET": "/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "POST": "Send JSON with 'url' or 'video_id' field"
        }
    })

# Simple file-based cache configuration
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
DEFAULT_CACHE_TTL_SECONDS = int(os.environ.get('TRANSCRIPT_CACHE_TTL', '86400'))  # default 24h
os.makedirs(CACHE_DIR, exist_ok=True)

def _sanitize_langs(langs):
    try:
        return [str(l).strip() for l in langs if str(l).strip()]
    except Exception:
        return []

def build_cache_key(video_id, target_language, languages, force_translate):
    langs_part = '-'.join(_sanitize_langs(languages)) if languages else ''
    tgt_part = target_language or ''
    force_part = '1' if force_translate else '0'
    return f"{video_id}|{tgt_part}|{langs_part}|{force_part}".replace('/', '_')

def load_cached_response(key, ttl_seconds=DEFAULT_CACHE_TTL_SECONDS):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    try:
        age = time.time() - os.path.getmtime(path)
        if age > ttl_seconds:
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def save_cached_response(key, payload):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
    except Exception:
        pass

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
            language = request.args.get('language')
            force_param = request.args.get('force')
            no_cache_param = request.args.get('no_cache')
            cache_ttl_param = request.args.get('cache_ttl')
            # Parse languages, support single-item 'languages' as target when force=true
            languages_arg = request.args.get('languages', 'en,vi,zh,es,fr,de,ja,ko')
            parsed_languages = [language] if language else languages_arg.split(',')
            # Force translate if 'language' provided (default true) OR single 'languages' provided with force=true
            force_translate = (
                (language is not None and (force_param is None or str(force_param).lower() in ['true','1','yes'])) or
                (language is None and len(parsed_languages) == 1 and (force_param is not None and str(force_param).lower() in ['true','1','yes']))
            )
            languages = parsed_languages
            no_cache = bool(no_cache_param) and str(no_cache_param).lower() in ['true','1','yes']
            ttl_seconds = int(cache_ttl_param) if (cache_ttl_param and str(cache_ttl_param).isdigit()) else DEFAULT_CACHE_TTL_SECONDS
        else:  # POST
            data = request.get_json() or {}
            url = data.get("url")
            video_id = data.get("video_id")
            language = data.get('language')
            languages_value = data.get('languages', ['en', 'vi', 'zh', 'es', 'fr', 'de', 'ja', 'ko'])
            if isinstance(languages_value, str):
                languages_value = languages_value.split(',')
            languages = [language] if language else languages_value
            force_param = data.get('force', None)
            force_translate = (
                (language is not None and (force_param is None or bool(force_param))) or
                (language is None and isinstance(languages, list) and len(languages) == 1 and bool(force_param))
            )
            no_cache = bool(data.get('no_cache', False))
            ttl_seconds = int(data.get('cache_ttl', DEFAULT_CACHE_TTL_SECONDS))
        
        target_language = language if language else (languages[0] if isinstance(languages, list) and len(languages) == 1 else None)
        
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
        
        # Try cache first
        cache_key = build_cache_key(video_id, target_language, languages, force_translate)
        if not no_cache:
            cached = load_cached_response(cache_key, ttl_seconds)
            if cached:
                return jsonify(cached)
        
        # Get transcript with language preferences
        transcript_data = get_transcript(video_id, languages)
        
        # Format transcript for easier consumption, with optional forced translation
        formatted_transcript = []
        full_text = ""
        translator = None
        if force_translate and target_language:
            try:
                translator = GoogleTranslator(source='auto', target=target_language)
            except Exception:
                translator = None
        
        for entry in transcript_data:
            original_text = entry.text.strip()
            translated_text = original_text
            if translator:
                try:
                    translated_text = translator.translate(original_text)
                except Exception:
                    translated_text = original_text
            
            formatted_entry = {
                "start": round(entry.start, 2),
                "duration": round(entry.duration, 2),
                "text": translated_text
            }
            formatted_transcript.append(formatted_entry)
            full_text += translated_text + " "
        
        response_payload = {
            "success": True,
            "video_id": video_id,
            "transcript": formatted_transcript,
            "full_text": full_text.strip(),
            "total_entries": len(formatted_transcript)
        }
        if target_language:
            response_payload["requested_language"] = target_language
            response_payload["forced"] = bool(force_translate)
        
        # Save to cache
        if not no_cache:
            save_cached_response(cache_key, response_payload)
        
        return jsonify(response_payload)
        
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