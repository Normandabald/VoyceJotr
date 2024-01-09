import os
import openai
import argparse
from datetime import datetime
import calendar
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

def get_todays_note_path():
    # Get the note directory
    note_dir = f"{os.getenv('NOTE_DIRECTORY')}Obsidian Vault/"

    # Get today's date
    today = datetime.today()

    # Format month and day of the week
    month_name = today.strftime("%m-%B")
    day_of_week = calendar.day_name[today.weekday()]

    # Construct the file name and path
    file_name = f"{today:%Y-%m-%d}-{day_of_week}.md"
    path = f"{note_dir}Daily Notes/{today.year}/{month_name}/{file_name}"

    return path

def convert_audio_to_text(audio_file_path):
    logging.info(f'Transcribing audio file: {audio_file_path}')
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
    logging.info('Transcription complete')
    return transcript['text']

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-1106-preview")
    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    logging.info(f'Number of tokens: {num_tokens}')
    return num_tokens

def get_summary(prompt):
    token_count = count_tokens(prompt)
    logging.info(f'Total tokens in prompt: {token_count}')
    if token_count > 8192:
        logging.warning('Token count exceeds limit, splitting text into smaller parts.')
        # Split the text into smaller parts if it exceeds the token limit
        parts = [prompt[i:i+8000] for i in range(0, len(prompt), 8000)]
        summaries = []
        for part in parts:
            completion = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are the USS Enterprise Ship's Computer. You summarize voice logs provided by crewmembers. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) An 'Actions' section with a bullet point list of outstanding actions. 3) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness; Written from the perspective of the crewmember."},
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

def write_new_task(new_task):
    file_path = get_todays_note_path()
    with open(file_path, 'r') as file:
        lines = file.readlines()

    task_section_found = False
    task_list_end = 0

    for i, line in enumerate(lines):
        if task_section_found:
            print(i, task_section_found, line[0:5], line.startswith("- ["))
        if line.strip() == "### Tasks":
            task_section_found = True
        elif task_section_found and not line.startswith("- ["):
            task_list_end = i
            break

    if task_section_found:
        lines.insert(task_list_end, new_task + "\n")
    else:
        lines.append("\n### Tasks\n" + new_task + "\n")

    with open(file_path, 'w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    logging.info('Script started.')
    # Get todays audio files
    note_dir = f"{os.getenv('NOTE_DIRECTORY')}Obsidian Vault/"
    daily_note_path = get_todays_note_path()
    today_str = datetime.now().strftime('%Y%m%d')
    i = 1
    test_task = f"- [ ] Test task {i}"
    write_new_task(test_task)
    todays_audio_files = glob.glob(f"{note_dir}Recording {today_str}*.webm")
    print(f'Found {len(todays_audio_files)} audio files for today.')

    # Convert todays audio files to text
    transcriptions = [convert_audio_to_text(audio_file) for audio_file in todays_audio_files]
    # Combine transcriptions into a single string
    transcription_text = '\n\n'.join(transcriptions)

    # Get summary of today's transcriptions
    # summary_prompt = f"Summarize the following thoughts:\n{transcription_text}"
    # summary = get_summary(summary_prompt)

    # logging.info('Log summary complete:')
    # print(f'Summary: {summary}')
