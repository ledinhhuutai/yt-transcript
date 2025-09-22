def save_transcript(transcript, filename="transcript.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for entry in transcript:
            f.write(f"{entry['start']:.2f}s - {entry['text']}\n")
    print(f"Transcript đã lưu vào {filename}")