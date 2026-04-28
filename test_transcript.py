from app.services.transcript_service import get_transcript

# Use this video — it's a short TED talk with good captions
url = "https://www.youtube.com/watch?v=arj7oStGLkU"

result = get_transcript(url)

print(f"Video ID: {result['video_id']}")
print(f"Duration: {result['duration_minutes']} minutes")
print(f"Word count: {result['word_count']}")
print(f"Segments: {result['segment_count']}")
print("\n--- First 3 segments ---")
for seg in result['segments'][:3]:
    print(f"[{seg['timestamp']}] {seg['text']}")