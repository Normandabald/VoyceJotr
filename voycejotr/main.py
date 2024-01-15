import logging
import glob
import os
import json
from datetime import datetime
from openai import OpenAI
from voycejotr.config_manager import Config
from voycejotr.audio_services import convert_audio_to_text
from voycejotr.summary_extractor import fetch_ai_response
from voycejotr.note_services import write_new_tasks, write_summary

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main_application')

def process_voice_note(api_client, audio_file_path):
    """
    Process a single voice note: transcribe, summarize, and manage tasks.

    Parameters
    ----------
    api_client : OpenAI
        The OpenAI client for making API requests.
    audio_file_path : str
        The path to the audio file.
    """
    try:
        # Convert the audio file to text
        transcription = convert_audio_to_text(api_client, audio_file_path)
        audio_filename = os.path.basename(audio_file_path)
        # Get summary of the transcription and write to daily note
        summary_prompt = f"Voice note transcription:\n{transcription}"
        tools = ["write_summary", "write_new_task"]
        for tool in tools:
            ai_response = fetch_ai_response(api_client, prompt=summary_prompt, tool=tool)
            if ai_response.tool_calls:
                arguments = json.loads(ai_response.tool_calls[0].function.arguments)
                if "summary" in arguments:
                    write_summary(arguments["summary"], arguments["short_summary"], audio_filename)
                elif "tasks" in arguments:
                    write_new_tasks(arguments["tasks"])
        

        # Handle other summary and task management logic
        # ...

        logger.info('Voice note processing complete.')

    except Exception as e:
        logger.error(f"Error in processing voice note: {e}")

if __name__ == "__main__":
    logger.info('Script started in manual mode. All audio files from today will be processed.')

    config = Config()
    client = OpenAI(api_key=config.api_key)

    # Get today's audio files
    today_str = datetime.now().strftime('%Y%m%d')
    todays_audio_files = glob.glob(f"{config.note_directory}Recording {today_str}*.webm")


    # Process today's audio files
    for audio_file in todays_audio_files:
        logger.info(f"Processing audio file: {audio_file}")
        process_voice_note(client, audio_file)

    logger.info('All tasks complete.')
