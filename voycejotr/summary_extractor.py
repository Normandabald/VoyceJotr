import logging
import json
from openai import OpenAI
from voycejotr.config_manager import Config
from voycejotr.utils import count_tokens
from voycejotr.note_services import write_summary, write_new_tasks

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
                        },
                        "short_summary": {
                            "type": "string"
                        }
                    },
                    "required": ["summary", "short_summary"]
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
You are a voice note summariser.
Do not mention tasks in your summary.
Write the summary in the first person E.G. 'I did this, I did that'.
The tool you have access to will write the summary to the daily note as a foldout. The short_summary parameter will be used as the foldout title and should encapsulate the summary in a few words.
the summary parameter will be used as the foldout content and should provide a short but detailed summary, maintaining clarity and conciseness and keeping details relevant to the voice log.

here is an example of what I expect:
---
voice note transcription: Today, I entered into a series of delicate negotiations with a delegation from the Romulan Empire. The discussions were intense and multifaceted, requiring a deep understanding of both our cultures and a careful navigation of interstellar diplomacy. I spent considerable time examining their proposals, which were intricate and required a thoughtful response. Our team deliberated extensively, considering the implications of each aspect of the negotiation.
In my dialogue with the Romulan envoy, I endeavored to represent the interests of the Federation with both firmness and diplomatic tact. It was a challenging balancing act, maintaining our principles while being open to compromise. After several hours of discussion, we reached a preliminary agreement. This agreement, while not yet final, is a promising step towards a more peaceful and cooperative relationship with the Romulans.
I have planned a subsequent meeting to iron out the finer points and solidify this accord. It is my hope that these efforts will contribute significantly to the stability and security of this sector of space, benefiting both the Federation and the Romulan Empire.
Short_summary: Reflecting on Diplomatic Negotiations
Summary: Today, I engaged in intricate diplomatic negotiations with the Romulan envoy. I navigated through complex discussions, striving for peace and mutual understanding. I analyzed their proposals, deliberated on our stance, and articulated our position with clarity. The session concluded with a tentative agreement, marking a significant step towards fostering better relations. I'm scheduling a follow-up meeting to finalize the details. This progress, although challenging, is vital for the stability of the sector.
---
Do not include the '---' in your response.
Do not include the 'Short_summary:' or 'Summary:' in your response.
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
