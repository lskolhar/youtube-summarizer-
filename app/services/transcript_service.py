from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re


def extract_video_id(url: str) -> str:
    """
    YouTube URLs come in several formats. This function extracts
    just the video ID (the 11-character code) from any of them.
    
    Examples:
      https://www.youtube.com/watch?v=dQw4w9WgXcQ  ->  dQw4w9WgXcQ
      https://youtu.be/dQw4w9WgXcQ                 ->  dQw4w9WgXcQ
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # standard and shortened URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # embedded URLs
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def format_timestamp(seconds: float) -> str:
    """
    Converts raw seconds (like 125.4) into a readable timestamp (2:05).
    YouTube URLs use raw seconds, but humans want MM:SS format.
    """
    seconds = int(seconds)
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def get_transcript(url: str) -> dict:
    """
    Main function. Takes a YouTube URL, returns a dictionary with:
    - video_id: the YouTube video ID
    - full_text: the entire transcript as one big string
    - segments: list of {text, start, timestamp} objects
    - word_count: total number of words
    - duration_minutes: approximate video duration
    """
    
    # Step 1: Extract the video ID from the URL
    video_id = extract_video_id(url)
    
    # Step 2: Try to fetch the transcript
    api = YouTubeTranscriptApi()
    try:
        # First try English captions
        fetched = api.list(video_id).find_transcript(['en']).fetch()
        transcript_list = [{"text": s.text, "start": s.start} for s in fetched]
    
    except NoTranscriptFound:
        try:
            # If no English captions, try auto-generated ones
            fetched = api.fetch(video_id)
            transcript_list = [{"text": s.text, "start": s.start} for s in fetched]
        except Exception as e:
            raise Exception(f"No transcript available for this video: {str(e)}")
    
    except TranscriptsDisabled:
        raise Exception("Transcripts are disabled for this video. Whisper fallback needed.")
    
    # Step 3: Process each segment
    segments = []
    for item in transcript_list:
        segments.append({
            "text": item["text"].strip(),
            "start": item["start"],           # raw seconds (e.g. 125.4)
            "timestamp": format_timestamp(item["start"]),  # human readable (2:05)
            "youtube_link_seconds": int(item["start"])     # for building clickable links
        })
    
    # Step 4: Build the full transcript text
    full_text = " ".join([seg["text"] for seg in segments])
    
    # Step 5: Calculate stats
    word_count = len(full_text.split())
    duration_minutes = round(segments[-1]["start"] / 60) if segments else 0
    
    return {
        "video_id": video_id,
        "full_text": full_text,
        "segments": segments,
        "word_count": word_count,
        "duration_minutes": duration_minutes,
        "segment_count": len(segments)
    }