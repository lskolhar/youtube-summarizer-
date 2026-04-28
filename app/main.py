from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.transcript_service import get_transcript

# Create the FastAPI app
app = FastAPI(
    title="YT Summarizer API",
    description="AI-powered YouTube video summarizer and chat assistant",
    version="0.1.0"
)

# CORS middleware — this allows your React frontend to call this API
# Without this, browsers will block the requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production you'd put your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# This is the shape of data the user sends to us
class TranscriptRequest(BaseModel):
    url: str


# ── ROUTES ──

@app.get("/health")
def health_check():
    """
    Simple endpoint to verify the server is running.
    Hit this first to make sure everything is working.
    """
    return {"status": "ok", "message": "YT Summarizer API is running"}


@app.post("/transcript")
async def fetch_transcript(request: TranscriptRequest):
    """
    Takes a YouTube URL, returns the full transcript with timestamps.
    
    Example request body:
    { "url": "https://www.youtube.com/watch?v=arj7oStGLkU" }
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        result = get_transcript(request.url)
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        # Bad URL format
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Transcript not available, disabled, etc.
        raise HTTPException(status_code=422, detail=str(e))