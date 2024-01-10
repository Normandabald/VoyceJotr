import os
import json
import re
from datetime import datetime
import calendar
import glob
import logging
import yaml
import tiktoken
from openai import OpenAI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger()


class Config:
    def __init__(self):


        with open("config.yaml", 'r') as stream:
            try:
                config_values = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.api_key = config_values["OPENAI_API_KEY"]
        self.note_directory = config_values["NOTE_DIRECTORY"]
        self.task_header = config_values["TASK_HEADER"] or "### Tasks"
        self.gpt_model = config_values["GPT_MODEL"] or "gpt-4-1106-preview"

    def validate(self):
        if not self.api_key or not self.note_directory:
            raise ValueError("Required environment variables are not set")

config = Config()
config.validate()

# Set the API key
client = OpenAI(api_key=config.api_key)

def get_todays_note_path():

    # Get today's date
    today = datetime.today()

    # Format month and day of the week
    month_name = today.strftime("%m-%B")
    day_of_week = calendar.day_name[today.weekday()]

    # Construct the file name and path
    file_name = f"{today:%Y-%m-%d}-{day_of_week}.md"
    path = f"{config.note_directory}Daily Notes/{today.year}/{month_name}/{file_name}"

    return path

def convert_audio_to_text(audio_file_path):
    logger.info(f'Transcribing audio file: {audio_file_path}')
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
    logger.info('Transcription complete')
    return transcript.text

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(config.gpt_model)
    tokens = encoding.encode(text)
    num_tokens = len(tokens)
    logger.info(f'Number of tokens: {num_tokens}')
    return num_tokens

def get_summary(prompt, audio_filename):
    """
    Summarise voice notes and extract tasks to be added to the daily note.

    Parameters
    ----------
    prompt : str
        The text to be summarised.
    audio_filename : str
        The name of the audio file to be linked to in the daily note.

    Returns
    -------
    str
        The summary text.
    """

    # Define the tools that are available to the AI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_summary",
                "description": "Writes a summary of the audio log to the daily note.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string"
                        }
                    },
                    "required": ["summary"]
                }
            }
        },
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


    messages =  [
        {"role": "system", "content": "You are the USS Enterprise Ship's Computer. Summarize the voice logs provided by the crewmember. The response should include three parts: 1) A 'TL;DR' section with bullet points summarizing key events and takeaways. 2) A 'Summary' section providing a detailed, in-depth paragraph, maintaining clarity and conciseness. You have the ability to write new markdown tasks to the daily note if the crewmember mentions any: Tasks must be in valid markdown format E.G. '- [ ] Task 1'"},
    ]

    # Check if the prompt exceeds the token limit and split it into smaller parts if necessary
    token_count = count_tokens(prompt)
    logger.info(f'Total tokens in prompt: {token_count}')

    if token_count > 8192:
        logger.warning('Token count exceeds limit, splitting text into smaller parts.')
        parts = [prompt[i:i+8000] for i in range(0, len(prompt), 8000)]
        summaries = []
        for part in parts:
            messages.append({"role": "user", "content": part})
            completion = client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            tools=tools,
            tool_choice="write_summary"
            )
            summaries.append(completion.choices[0].message)
        summary_message = '\n\n'.join(summaries)

    else:

        logger.info('Processing text...')
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "write_summary"}}
            )
        summary_message = completion.choices[0].message


    if summary_message.tool_calls:
        note_summary = json.loads(summary_message.tool_calls[0].function.arguments)["summary"]
        write_summary(note_summary, audio_filename)

    # Pass the note through again to check if there are any tasks to extract
    completion = client.chat.completions.create(
        model=config.gpt_model,
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "write_new_task"}}
        )
    tasks_message = completion.choices[0].message
    if tasks_message.tool_calls:
        note_tasks = json.loads(tasks_message.tool_calls[0].function.arguments)["tasks"]
        write_new_tasks(note_tasks)

    return tasks_message


def write_new_tasks(tasks: list):
    """
    Write new tasks to the daily note.

    Parameters
    ----------
    tasks : list
        A list of tasks to be added to the daily note.
    """

    try:
        file_path = get_todays_note_path()
        with open(file_path, 'r') as file:
            lines = file.readlines()

        task_section_found = False
        task_list_end = None

        # Search through the daily note for the task section
        for i, line in enumerate(lines):
            if line.strip() == config.task_header:
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
            lines.append(f"\n{config.task_header}\n")
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

def write_summary(summary: str, audio_filename: str):
    """
    Write the summary of a voice note below the audio link in the daily note.

    Parameters
    ----------
    summary : str
        The summary text.
    audio_filename : str
        The name of the audio file to be linked to in the daily note.
    """

    try:
        file_path = get_todays_note_path()
        with open(file_path, 'r') as file:
            lines = file.readlines()

        audio_link_found = False
        audio_link_end = None

        # Search through the daily note for the audio link
        for i, line in enumerate(lines):
            if line.strip() == f"![[{audio_filename}]]":
                audio_link_found = True
                audio_link_end = i + 1
                break

        if audio_link_found:
            timestamp = datetime.now().strftime('%H:%M')
            lines.insert(audio_link_end, f"> \"{summary}\" - {timestamp}" + "\n")

        with open(file_path, 'w') as file:
            file.writelines(lines)
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def process_voice_note(audio_file_path):
    # Convert the audio file to text
    transcription = convert_audio_to_text(audio_file_path)

    # Get summary of the transcription
    audio_filename = os.path.basename(audio_file_path)
    summary_prompt = f"Voice note transcription:\n{transcription}"
    summary = get_summary(summary_prompt, audio_filename)

    logger.info('Task complete.')

if __name__ == "__main__":
    logger.info('Script started.')

    # Get todays audio files
    today_str = datetime.now().strftime('%Y%m%d')
    todays_audio_files = glob.glob(f"{config.note_directory}Recording {today_str}*.webm")

    # Process todays audio files
    for audio_file in todays_audio_files:
        process_voice_note(audio_file)

    logger.info('Task complete.')
