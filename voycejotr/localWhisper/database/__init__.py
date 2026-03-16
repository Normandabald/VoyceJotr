from .database import Base, engine, SessionLocal, get_db, create_tables, Transcription
from .repository import TranscriptionRepository

# Initialize database tables when the package is imported
create_tables()