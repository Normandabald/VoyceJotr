import os
import openai
import argparse
from datetime import datetime
import glob
import tiktoken
import logging
import dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
dotenv.load_dotenv()

# Set the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def convert_audio_to_text(audio_file_path):
    logging.info(f'Transcribing audio file: {audio_file_path}')
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
    logging.info('Transcription complete')
    return transcript['text']

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    logging.info(f'Number of tokens: {num_tokens}')
    return num_tokens

def get_summary(prompt):
    token_count = count_tokens(prompt)
    logging.info(f'Total tokens in prompt: {token_count}')
    if token_count > 8192:
        logging.warning(f'Token count exceeds limit, splitting text into smaller parts.')
        # Split the text into smaller parts if it exceeds the token limit
        parts = [prompt[i:i+8000] for i in range(0, len(prompt), 8000)]
        summaries = []
        for part in parts:
            completion = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are the USS Enterprise Ship's Computer. Summarize the logs provided by the crewmember. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) An 'Actions' section with a bullet point list of outstanding actions. 3) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness; Written from the perspective of the crewmember."},
                    {"role": "user", "content": part}
                ]
            )
            summaries.append(completion['choices'][0]['message']['content'])
        # Combine the summaries into a single summary
        summary = '\n\n'.join(summaries)
    else:
        logging.info('Processing text...')
        # If the text is within the token limit, process it as usual
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are the USS Enterprise Ship's Computer. Summarize the logs provided by the crewmember. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) An 'Actions' section with a bullet point list of outstanding actions. 3) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = completion['choices'][0]['message']['content']
    return summary

if __name__ == "__main__":
    logging.info('Script started.')
    # Get todays audio files
    note_dir = f"{os.getenv('NOTE_DIRECTORY')}Obsidian Vault/"
    today_str = datetime.now().strftime('%Y%m%d')
    todays_audio_files = glob.glob(f"{note_dir}Recording {today_str}*.webm")
    print(f'Found {len(todays_audio_files)} audio files for today.')

    # Convert todays audio files to text
    transcriptions = [convert_audio_to_text(audio_file) for audio_file in todays_audio_files]
    # Combine transcriptions into a single string
    transcription_text = '\n\n'.join(transcriptions)
    logging.info(f'Transcriptions:\n{transcription_text}')

    # # Get summary of today's transcriptions
    # summary_prompt = f"Summarize the following thoughts:\n{transcription_text}"
    # summary = get_summary(summary_prompt)

    logging.info('Log summary complete:')
    print(f'Summary: {summary}')
