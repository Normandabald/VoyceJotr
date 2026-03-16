from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import Optional, List
from transcribe import get_transcribe
from pydantic import BaseModel
from models import uploadedaudio, responseModel
from database import get_db, TranscriptionRepository
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/transcribe", response_model=responseModel.Response)
async def transcribe_audio(
    audio: UploadFile = File(...),
    model: Optional[str] = None,  # Optional model name
    language: Optional[str] = None,  # Optional language
    db: Session = Depends(get_db)  # Database dependency
):
    print(f"inputs: {model}")
    # Create an instance of AudioParameters with optional values
    params = uploadedaudio.AudioParameters(model=model or "base", language=language or "en")
    
    try:
        # Pass the database session to save the transcription
        return get_transcribe(audio, params, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcriptions", response_model=List[responseModel.Response])
async def get_transcriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all transcriptions with pagination.
    """
    transcriptions = TranscriptionRepository.get_all_transcriptions(db, skip=skip, limit=limit)
    return [
        responseModel.Response(
            id=t.id,
            text=t.text,
            model=t.model,
            time=t.processing_time,
            filename=t.filename
        ) for t in transcriptions
    ]

@app.get("/transcriptions/{transcription_id}", response_model=responseModel.Response)
async def get_transcription(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific transcription by ID.
    """
    transcription = TranscriptionRepository.get_transcription(db, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return responseModel.Response(
        id=transcription.id,
        text=transcription.text,
        model=transcription.model,
        time=transcription.processing_time,
        filename=transcription.filename
    )

@app.get("/search", response_model=List[responseModel.Response])
async def search_transcriptions(
    q: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search transcriptions by content.
    """
    transcriptions = TranscriptionRepository.search_transcriptions(db, search_term=q, skip=skip, limit=limit)
    return [
        responseModel.Response(
            id=t.id,
            text=t.text,
            model=t.model,
            time=t.processing_time,
            filename=t.filename
        ) for t in transcriptions
    ]
