import logging
import json
from openai import OpenAI
from voycejotr.config_manager import Config
from voycejotr.utils import count_tokens
from voycejotr.note_services import write_summary, write_new_tasks
from voycejotr.tools.tools_factory import ToolFactory

config = Config()
tool_factory = ToolFactory()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(level)s - %(message)s')
logger = logging.getLogger('summary_extractor')

def fetch_ai_response(api_client, prompt, tool_name):
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

    # Check token count and split prompt if necessary
    token_count = count_tokens(prompt)
    logger.info(f'Total tokens in prompt: {token_count}')
    tool_factory.load_tool(tool_name)
    tool, tool_message = tool_factory.get_tool_and_message(tool_name)
    messages = []
    messages.append(tool_message)
    logger.info(f'{tool_name} tool loaded. {messages}')
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
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": tool_name}}
            )
            summaries.append(completion.choices[0].message)
        response_message = '\n\n'.join(summaries)
    else:
        logger.info('Passing prompt to AI...')
        messages.append({"role": "user", "content": prompt})
        completion = api_client.chat.completions.create(
            model=config.gpt_model,
            messages=messages,
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": tool_name}}
            )
        response_message = completion.choices[0].message

    return response_message
