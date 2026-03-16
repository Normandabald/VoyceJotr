import whisper
import tempfile
import os
import time
from voycejotr.localWhisper.models import responseModel, uploadedaudio
from voycejotr.localWhisper.database.repository import TranscriptionRepository
from sqlalchemy.orm import Session
from io import BytesIO

# Constants for model names
MODEL_NAMES = ["tiny", "small", "base", "turbo"]

print("Loading Whisper model...")
# models = {name: whisper.load_model(name, device='cuda:0') for name in MODEL_NAMES}
models = {name: whisper.load_model(name) for name in MODEL_NAMES}

print("Whisper model loaded successfully")

def load_audio_model(model_name: str):
    """Load the specified Whisper model."""
    return models.get(model_name, models["base"])

def transcribe_audio(whisper_model, audio_data, language: str):
    """Transcribe audio data using the specified Whisper model."""
    return whisper_model.transcribe(audio_data, language=language)

def get_transcribe(audio, params: uploadedaudio.AudioParameters, db: Session = None):
    """
    Transcribe audio content using the whisper model.
    
    Args:
        audio: Binary audio content or an object with a file attribute
        params: Audio parameters including model and language
        db: Optional database session for storing results
        
    Returns:
        dict: Transcription result with the transcribed text
    """
    print(f"Requested model: {params.model}")
    model = load_audio_model(params.model)
    
    # Handle both file-like objects and raw binary data
    if hasattr(audio, 'file'):
        audio_content = audio.file.read()
        filename = getattr(audio, "filename", None)
    elif isinstance(audio, bytes):
        audio_content = audio
        filename = None
    else:
        return {"error": "Invalid audio input format"}
    
    start_time = time.time()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        audio_data = whisper.load_audio(temp_file_path)
        result = transcribe_audio(model, audio_data, params.language)

        elapsed_time = time.time() - start_time
        os.unlink(temp_file_path)

        # Create a response object
        response = responseModel.Response(
            text=result["text"], 
            model=params.model, 
            time=elapsed_time,
            filename=filename
        )
        
        # Save to database if session is provided
        if db is not None:
            db_transcription = TranscriptionRepository.create_transcription(
                db=db,
                text=result["text"],
                model=params.model,
                language=params.language,
                processing_time=elapsed_time,
                filename=filename
            )
            response.id = db_transcription.id
            
        return response

    except Exception as e:
        return {"error": str(e)}

def main(audio_file_path: str = './input/audio.wav'):
    print("Starting transcription process...")
    print(f"Audio file path: {audio_file_path}")
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()
    
    # Create a mock audio object with a file attribute
    class MockAudio:
        def __init__(self, data):
            self.file = BytesIO(data)
            self.filename = os.path.basename(audio_file_path)
    
    audio_obj = MockAudio(audio_data)
    result = get_transcribe(audio=audio_obj, params=uploadedaudio.AudioParameters(model="base", language="en"))    
    print('-' * 50)
    print(f"Transcription completed in {result.time:.2f} seconds")
    print('-' * 50)
    print(result.text)
    return result.text

if __name__ == "__main__":
    main()