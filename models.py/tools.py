class Tools:

    @staticmethod
    def get_summary(transcript):
        get_summary = {}
        get_summary.tool = {
            "type": "function",
            "function": {
                "name": "get_summary",
                "description": "Creates a summary of the audio log to the daily note.",
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
        }
        get_summary.messages = []
        get_summary.messages.append({
            "role": "system",
            "content": """
            You are a note summariser.
            Summarize the voice logs provided to you. 
            The response should provide a very short but detailed summary, maintaining clarity and conciseness. 
            Do not mention tasks in your summary.
            Write the summary in the first person E.G. 'I did this, I did that'.
            Use the provided tool to provide a single sentence summary of the voice log as well as a longer summary.
            """
        })
        get_summary.messages

