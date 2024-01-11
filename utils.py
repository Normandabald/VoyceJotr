import logging
import tiktoken
from config_manager import Config

config = Config()

# Setup logging for utility functions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('utils')

def count_tokens(text):
    """
    Count the number of tokens in a given text for a specific GPT model.

    Parameters
    ----------
    text : str
        The text to count tokens in.

    Returns
    -------
    int
        The number of tokens.
    """
    try:
        encoding = tiktoken.encoding_for_model(config.gpt_model)
        tokens = encoding.encode(text)
        num_tokens = len(tokens)
        logger.info(f'Number of tokens in text: {num_tokens}')
        return num_tokens
    except Exception as e:
        logger.error(f"Error in counting tokens: {e}")
        raise

