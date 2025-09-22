from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id, languages=['en', 'vi', 'zh', 'es', 'fr', 'de', 'ja', 'ko']):
    """
    Fetch transcript for a given YouTube video ID with language fallback
    """
    try:
        # Try to get transcript in preferred languages order
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=languages)
        return transcript
    except Exception as e:
        # If specific languages fail, try to get any available transcript
        try:
            # Get list of available transcripts
            transcript_list = YouTubeTranscriptApi().list(video_id)
            
            # Try to get the first available transcript
            for transcript_info in transcript_list:
                try:
                    transcript = transcript_info.fetch()
                    return transcript
                except:
                    continue
            
            # If no transcript found, raise the original error
            raise Exception(f"Could not retrieve transcript: {str(e)}")
        except Exception as fallback_error:
            raise Exception(f"Could not retrieve transcript: {str(e)}")
