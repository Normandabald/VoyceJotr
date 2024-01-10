import os
import json
import re
from datetime import datetime
import calendar
import glob
import logging
import dotenv
import tiktoken
from openai import OpenAI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger()

# Load environment variables
dotenv.load_dotenv()

# Set the API key

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    logger.info(f'Transcribing audio file: {audio_file_path}')
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
    logger.info('Transcription complete')
    return transcript.text

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-1106-preview")
    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    logger.info(f'Number of tokens: {num_tokens}')
    return num_tokens

def get_summary(prompt):

    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_new_task",
                "description": "Write new tasks to the daily note.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["tasks"]
                }
            }
        }
    ]

    token_count = count_tokens(prompt)
    logger.info(f'Total tokens in prompt: {token_count}')
    if token_count > 8192:
        logger.warning('Token count exceeds limit, splitting text into smaller parts.')
        # Split the text into smaller parts if it exceeds the token limit
        parts = [prompt[i:i+8000] for i in range(0, len(prompt), 8000)]
        summaries = []
        for part in parts:
            completion = client.chat.completions.create(model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are the USS Enterprise Ship's Computer. Summarize the voice logs provided by the crewmember. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness. You have the ability to write new markdown tasks to the daily note if the crewmember mentions any: Tasks must be in valid markdown format E.G. '- [ ] Task 1'"},
                {"role": "user", "content": part}
            ])
            summaries.append(completion.choices[0].message)
        # Combine the summaries into a single summary
        summary = '\n\n'.join(summaries)
    else:
        logger.info('Processing text...')
        # If the text is within the token limit, process it as usual
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are the USS Enterprise Ship's Computer. Summarize the voice logs provided by the crewmember. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness. You have the ability to write new markdown tasks to the daily note if the crewmember mentions any: Tasks must be in valid markdown format E.G. '- [ ] Task 1'"},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="auto"
            )
        summary = completion.choices[0].message

    # Check if there are any tool calls
    if completion.choices[0].message.tool_calls:
        # Extract the tasks from the arguments field
        tasks = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)["tasks"]
        # Call the write_new_tasks function with the tasks
        write_new_tasks(tasks)

    return summary

def write_new_tasks(tasks: list):
    # Check if tasks are in valid markdown format
    # for task in tasks:
    #     if not re.match(r'- \[\] .+', task):
    #         print(f"Invalid task format: {task}")
    #         return
    try:
        file_path = get_todays_note_path()
        with open(file_path, 'r') as file:
            lines = file.readlines()

        task_section_found = False
        task_list_end = None

        for i, line in enumerate(lines):
            if line.strip() == "### Tasks":
                task_section_found = True
            elif task_section_found and line.startswith("- ["):
                task_list_end = i + 1
            elif task_section_found and not line.startswith("- ["):
                break

        if task_list_end is not None:
            for task in tasks:
                lines.insert(task_list_end, task + "\n")
                task_list_end += 1
        else:
            lines.append("\n### Tasks\n")
            for task in tasks:
                lines.append(task + "\n")

        with open(file_path, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        print(f"An error occurred: {e}")

        with open(file_path, 'w') as file:
            file.writelines(lines)
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logger.info('Script started.')

    # Get todays audio files
    note_dir = f"{os.getenv('NOTE_DIRECTORY')}Obsidian Vault/"
    today_str = datetime.now().strftime('%Y%m%d')
    todays_audio_files = glob.glob(f"{note_dir}Recording {today_str}*.webm")
    logger.info(f'Found {len(todays_audio_files)} audio files for today.')

    # Convert todays audio files to text
    transcriptions = [convert_audio_to_text(audio_file) for audio_file in todays_audio_files]
    # Combine transcriptions into a single string
    transcription_text = '\n\n'.join(transcriptions)

    # Get summary of today's transcriptions
    summary_prompt = f"Summarize the following thoughts:\n{transcription_text}"
    summary = get_summary(summary_prompt)

    logger.info('Log summary complete:')
    logger.info(f'Summary: {summary}')
