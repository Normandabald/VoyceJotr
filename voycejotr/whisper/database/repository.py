from sqlalchemy.orm import Session
from .database import Transcription

class TranscriptionRepository:
    """
    Repository class for handling database operations for transcriptions.
    This provides an abstraction layer that makes it easier to switch database implementations.
    """
    
    @staticmethod
    def create_transcription(db: Session, text: str, model: str, language: str, 
                            processing_time: float, filename: str = None) -> Transcription:
        """
        Create a new transcription record in the database
        """
        db_transcription = Transcription(
            text=text,
            model=model,
            language=language,
            processing_time=processing_time,
            filename=filename
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        return db_transcription
    
    @staticmethod
    def get_transcription(db: Session, transcription_id: int) -> Transcription:
        """
        Get a transcription by ID
        """
        return db.query(Transcription).filter(Transcription.id == transcription_id).first()
    
    @staticmethod
    def get_all_transcriptions(db: Session, skip: int = 0, limit: int = 100):
        """
        Get all transcriptions with pagination
        """
        return db.query(Transcription).order_by(Transcription.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_transcriptions(db: Session, search_term: str, skip: int = 0, limit: int = 100):
        """
        Search transcriptions by content
        """
        # Handle wildcard * as a special case
        if search_term == '*':
            return db.query(Transcription).order_by(Transcription.created_at.desc()).offset(skip).limit(limit).all()
        
        # For regular searches, use the contains function
        return db.query(Transcription).filter(
            Transcription.text.contains(search_term)
        ).order_by(Transcription.created_at.desc()).offset(skip).limit(limit).all()