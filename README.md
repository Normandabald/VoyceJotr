# Voice Note Summarizer

This script can be run in the background to automatically summarise your voice note, extract tasks into a todo list and add the summary to your daily notes.

<a href="https://www.buymeacoffee.com/normandabald" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## Setup

1. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

2. Create a `config.yaml` file in the same directory as the script with the following structure:

   ```yaml
   OPENAI_API_KEY: your_openai_api_key
   NOTE_DIRECTORY: path_to_your_note_directory
   TASK_HEADER: "# Tasks"
   GPT_MODEL: gpt-4-1106-preview
   ```

   Replace `your_openai_api_key` with your OpenAI API key and `path_to_your_note_directory` with the path to the directory where your notes are stored.

3. Ensure you have the Obsidian Core Plugin `Audio Recorder` installed and that it is set to record in the `.webm` format.

<details>
  <summary>Setting up your notes for the first time?</summary>
  
  → Have a read of Dann Berg's [Daily Note guide](https://dannb.org/blog/2022/obsidian-daily-note-template/)

</details>
.

4. This app is built on the assumption that you are storing your daily notes in a folder structure:

```
- Daily Notes
  - 2024
    - 01-January
      - 2024-01-10-Wednesday
```

5. Additionally, there is an assumption that all of your audio recordings are being saved directly into the root of the vault folder with a naming convention of `Recording YYYYMMDDHHMMSS.webm`
   E.G. `Recording 20240110222028.webm`

## Usage

Run the script with the following command:

```
python3 watcher.py
```

The script will do the following:

1. Transcribe today's audio files from the note directory.
2. Summarize the transcriptions and write the summary to the daily note.
3. Extract tasks from the transcriptions and add them to the task section of the daily note.

## Note

The script assumes that the daily note is a Markdown file with a specific structure. The note should have a section for tasks, which is indicated by a header specified in the `TASK_HEADER` configuration value. The default header is "# Tasks". The tasks in this section should be in the format `- [ ] Task description`.

- [ ] Task description
- [x] This is a completed task

The script also assumes that the audio files are in the `.webm` format and are named with the pattern `Recording YYYYMMDD*.webm`, where `YYYYMMDD` is the date.
