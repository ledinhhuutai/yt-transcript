from yt_transcript.fetch import get_transcript
from yt_transcript.utils import save_transcript

def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url

if __name__ == "__main__":
    url = input("Nhập link YouTube: ")
    video_id = extract_video_id(url)
    transcript = get_transcript(video_id)
    
    if transcript:
        save_transcript(transcript)
    else:
        print("Không lấy được transcript.")
