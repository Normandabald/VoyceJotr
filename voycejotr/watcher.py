from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging
import threading
from openai import OpenAI, OpenAIError
from voycejotr.main import process_voice_note
from voycejotr.config_manager import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('watcher')

config = Config()

try:
    client = OpenAI(api_key=config.api_key)
except OpenAIError as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    exit(1)

class NewRecordingHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processed_files = set()
        self.lock = threading.Lock()
    
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.m4a'):
            return
        with self.lock:
            if event.src_path in self.processed_files:
                return
            self.processed_files.add(event.src_path)
        
        def delayed_process():
            logger.info(f"New recording detected: {event.src_path}")
            process_voice_note(client, event.src_path)

        # Delay processing to allow file to be fully written.
        timer = threading.Timer(1.0, delayed_process)
        timer.start()

if __name__ == "__main__":
    logger.info("Starting watcher...")
    event_handler = NewRecordingHandler()
    observer = Observer()
    observer.schedule(event_handler, path=config.note_directory, recursive=True)
    observer.start()
    logger.info("Ready!")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()