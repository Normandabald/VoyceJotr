import logging
import os
from openai import OpenAI
from config_manager import Config

config = Config()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('audio_services')

def convert_audio_to_text(api_client, audio_file_path):
    """
    Transcribe an audio file to text.

    Parameters
    ----------
    audio_file_path : str
        The path to the audio file to be transcribed.
    language : str
        The language of the audio file.

    Returns
    -------
    str
        The transcribed text.
    """


    logger.info(f'Transcribing audio file: {audio_file_path}')
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = api_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=config.language
                )
        logger.info('Transcription complete')
        return transcript.text
    except FileNotFoundError:
        logger.error(f"Audio file {audio_file_path} not found.")
        raise
    except Exception as e:
        logger.error(f"An error occurred during transcription: {e}")
        raise
