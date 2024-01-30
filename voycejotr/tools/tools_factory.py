import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(level)s - %(message)s')
logger = logging.getLogger('summary_extractor')

class ToolFactory:
    def __init__(self):
        self.tools = {}
        self.tool_messages = {}

    def load_tool(self, tool):
        """
        Load a tool from a JSON file.

        Parameters
        ----------
        tool_file : str
            The path to the JSON file containing the tool definition.
        """
        tool_file = f"voycejotr/tools/{tool}.json"
        logger.info(f"Loading tool from {tool_file} ...")
        with open(tool_file, 'r') as f:
            tool_data = json.load(f)
            name = tool_data['name']
            self.tools[name] = tool_data['tool']
            self.tool_messages[name] = {"role": "system", "content": tool_data['message']}

    def get_tool_and_message(self, name):
        """
        Get a tool and its message by name.

        Parameters
        ----------
        name : str
            The name of the tool.

        Returns
        -------
        dict, dict
            The tool dictionary and the tool message.
        """
        return self.tools[name], self.tool_messages[name]