# YouTube Transcript API

A Flask-based API that extracts transcripts from YouTube videos for integration with Laravel applications.

## Features

- Extract transcripts from YouTube videos
- Support for various YouTube URL formats
- CORS enabled for cross-origin requests
- RESTful API with JSON responses
- Comprehensive error handling

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Start the Server
```bash
python app.py
```

The server will run on `http://localhost:5001`

### API Endpoints

#### GET /
Returns API documentation

#### GET/POST /transcript
Extract transcript from a YouTube video

**Parameters:**
- `url`: YouTube video URL
- `video_id`: YouTube video ID (alternative to url)

**Example Requests:**
```bash
# GET request
curl "http://localhost:5001/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# POST request
curl -X POST http://localhost:5001/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Response Format:**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "transcript": [
    {
      "start": 1.36,
      "duration": 1.68,
      "text": "[♪♪♪]"
    }
  ],
  "full_text": "Complete transcript text...",
  "total_entries": 156
}
```

## Laravel Integration

```php
use Illuminate\Support\Facades\Http;

$response = Http::get('http://localhost:5001/transcript', [
    'url' => 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
]);

$data = $response->json();
if ($data['success']) {
    $transcript = $data['transcript'];
    $fullText = $data['full_text'];
}
```

## Dependencies

- Flask
- Flask-CORS
- youtube-transcript-api

## License

MIT License