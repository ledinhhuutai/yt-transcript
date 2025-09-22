from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str):
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        return transcript
    except Exception as e:
        print(f"Lỗi khi lấy transcript: {e}")
        return []
