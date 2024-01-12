import logging
import json
from echonote.config_manager import Config
from openai import OpenAI
from utils import count_tokens
from note_services import write_summary, write_new_tasks

config = Config()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(essage)s')
logger = logging.getLogger('summary_extractor')

def fetch_ai_response(api_client, prompt, tool):
    """
    Query the AI for a response to a prompt.

    Parameters
    ----------
    prompt : str
        The text to be summarized.
    audio_filename : str
        The name of the audio file to be linked to in the daily note.

    Returns
    -------
    str
        The summary text.
    """

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


    tool_messages = {
        "write_summary": {
            "role": "system",
            "content": """
            You are a note summariser.
            Summarize the voice logs provided to you. 
            The response should provide a very short but detailed summary, maintaining clarity and conciseness. 
            Do not mention tasks in your summary.
            Write the summary in the first person E.G. 'I did this, I did that'.
            You are not the enterprise computer and the user is not a crew member.
            """
        },
        "write_new_task": {
            "role": "system",
            "content": """
            You are a task extractor.
            Extract tasks from the voice logs provided to you.
            You have access to a tool that can write new tasks to the daily note if the message mentions any but only if they are in valid markdown format.
            The response must include a list of tasks in valid markdown format E.G. '[`- [ ] Task 1`, `- [ ] Task 2`]'.
            You will be marked down if tasks are not in valid markdown format.
            """
        }
    }

    messages = [tool_messages[tool]]

    # Check token count and split prompt if necessary
    token_count = count_tokens(prompt)
    logger.info(f'Total tokens in prompt: {token_count}')

    if token_count > 8192:
        logger.warning('Token count exceeds limit, splitting text into smaller parts.')
        parts = [prompt[i:i+8000] for i in range(0, len(prompt), 8000)]
        summaries = []
        logger.info('Passing split prompts to AI...')
        for part in parts:
            messages.append({"role": "user", "content": part})
            completion = api_client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": tool}}
            )
            summaries.append(completion.choices[0].message)
        response_message = '\n\n'.join(summaries)
    else:
        logger.info('Passing prompt to AI...')
        messages.append({"role": "user", "content": prompt})
        completion = api_client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": tool}}
            )
        response_message = completion.choices[0].message

    return response_message
