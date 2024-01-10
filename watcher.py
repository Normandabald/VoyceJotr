from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import summariser
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger()

class NewRecordingHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.webm'):
            return
        logger.info(f"New recording detected: {event.src_path}")
        summariser.process_voice_note(event.src_path)

if __name__ == "__main__":
    logger.info("Starting watcher")
    event_handler = NewRecordingHandler()
    observer = Observer()
    observer.schedule(event_handler, path=summariser.config.note_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()