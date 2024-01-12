# Voice Note Summariser

The Voice Note Summariser is an automated tool designed to streamline your note-taking and task management. It transcribes, summarises, and integrates your voice notes into daily notes within Obsidian, and extracts tasks for easy tracking.

Get those pesky thoughts out of your head and into your notes!

Did this tool help you? Consider [supporting me](https://www.buymeacoffee.com/normandabald)!

<a href="https://www.buymeacoffee.com/normandabald" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## Features

- **Automatic Transcription**: Converts voice recordings to text.
- **Summarisation**: Generates concise summaries of transcribed text.
- **Task Extraction**: Identifies and lists tasks from your voice notes.
- **Integration with Daily Notes**: Seamlessly adds summaries and tasks to your existing note structure.

## Setup Instructions

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Create a `config.yaml` in the script directory and replace the values with your own.
   An example is available in [config.example.yaml](config.example.yaml).

```yaml
OPENAI_API_KEY: your_openai_api_key
NOTE_DIRECTORY: C:\Files\Documents\obsidian\Obisidian Vault\
TASK_HEADER: "# Tasks"
GPT_MODEL: gpt-4-1106-preview
LANGUAGE: en
```

3. **Obsidian Setup**:
   Enable the Audio Recorder core-plugin in Obsidian and set to `.webm` format.

> [!TIP]
> Need some inspiration for daily notes?
> Dann Berg's [Daily Note guide](https://dannb.org/blog/2022/obsidian-daily-note-template/).

4. **Folder Structure**:
   Organize daily notes as follows:
   ```
   - Daily Notes
      - 2024
         - 01-January
            - 2024-01-10-Wednesday.md
   ```

Save audio recordings in the root directory with the format `Recording YYYYMMDDHHMMSS.webm` into the root of your Obsidian Directory.
This happens by default, make sure you are hitting record with your daily note open.

## Usage

1. Run the background watchdog script:

```bash
python3 watcher.py
```

2. With your daily note open, hit record and waffle way.
3. When you are done, hit stop and the script will do the rest.

The script will:

4. Transcribe voice notes each time a new file is created.
5. Summarize the content and integrate it directly into the daily note.
6. Identify and list tasks in the specified task section.

## Support

If this tool enhances your productivity, consider [supporting me](<(https://www.buymeacoffee.com/normandabald)>)!
