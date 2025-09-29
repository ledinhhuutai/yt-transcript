# Cập nhật Laravel Configuration cho transcript.inonappstudio.com

## 1. Cập nhật file .env

```env
# YouTube Transcript API Configuration
YOUTUBE_TRANSCRIPT_API_URL=https://transcript.inonappstudio.com
YOUTUBE_TRANSCRIPT_API_TIMEOUT=30
```

## 2. Cập nhật Service Class (nếu có)

```php
// app/Services/YouTubeTranscriptService.php
class YouTubeTranscriptService
{
    private $apiUrl;

    public function __construct()
    {
        $this->apiUrl = config('services.youtube_transcript.url', 'https://transcript.inonappstudio.com');
    }

    public function getTranscript($videoUrl)
    {
        $response = Http::timeout(30)->get($this->apiUrl . '/transcript', [
            'url' => $videoUrl
        ]);

        return $response->json();
    }
}
```

## 3. Cập nhật config/services.php

```php
'youtube_transcript' => [
    'url' => env('YOUTUBE_TRANSCRIPT_API_URL', 'https://transcript.inonappstudio.com'),
    'timeout' => env('YOUTUBE_TRANSCRIPT_API_TIMEOUT', 30),
],
```

## 4. Test API từ Laravel

```php
// Test trong Controller hoặc Tinker
use Illuminate\Support\Facades\Http;

$response = Http::get('https://transcript.inonappstudio.com/transcript', [
    'url' => 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
]);

dd($response->json());
```

## 5. Test với cURL

```bash
curl "https://transcript.inonappstudio.com/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```