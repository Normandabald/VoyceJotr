from pydantic import BaseModel, Field

class AudioParameters(BaseModel):
    model: str = Field(default="base", description="Model name for transcription")
    language: str = Field(default="en", description="Language for transcription")