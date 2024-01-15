import logging
import re
from datetime import datetime
from voycejotr.config_manager import Config

config = Config()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('note_services')

def get_todays_note_path():
    """
    Generate a file path for today's note based on the current date.
    """
    today = datetime.today()
    month_name = today.strftime("%m-%B")
    file_name = f"{today:%Y-%m-%d}-{today.strftime('%A')}.md"
    path = f"{config.note_directory}Daily Notes/{today.year}/{today.strftime('%m-%B')}/{file_name}"
    return path


def write_new_tasks(tasks: list):
    """
    Write new tasks to the daily note.

    Parameters
    ----------
    tasks : list
        A list of tasks to be added to the daily note.
    """
    # Define the regular expression for a valid task
    task_regex = re.compile(r"- \[[ xX]\] .+")

    # Validate the tasks
    for task in tasks:
        if not task_regex.match(task):
            logger.error(f"Invalid task format: {task}")
            raise ValueError(f"Invalid task format: {task}")

    logger.info("Writing new tasks to list")
    file_path = get_todays_note_path()
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        task_section_found = False
        task_list_end = None

        # Search through the daily note for the task section
        for i, line in enumerate(lines):
            if line.strip() == config.task_header:
                task_section_found = True
                task_list_end = i + 1
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
        
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

def write_summary(summary: str, short_summary: str, audio_filename: str):
    """
    Write the summary of a voice note below the audio link in the daily note.

    Parameters
    ----------
    summary : str
        The summary text.
    audio_filename : str
        The name of the audio file to be linked to in the daily note.
    """
    logger.info("Writing summary to daily note")
    file_path = get_todays_note_path()
    try:
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
            lines.insert(audio_link_end, f">[!Tip]- {timestamp}: {short_summary}\n> \"{summary}\"" + "\n")

        with open(file_path, 'w') as file:
            file.writelines(lines)

    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
