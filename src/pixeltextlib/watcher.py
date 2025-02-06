import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

_logger = logging.getLogger(__name__)

class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, core, config):
        super().__init__()
        self.core = core
        self.config = config
        self.valid_extensions = config.get('valid_extensions')

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        if any(filepath.lower().endswith(ext) for ext in self.valid_extensions):
            _logger.info(f"File created: {filepath}")
            self.core.index_image(filepath)

    def on_deleted(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        if any(filepath.lower().endswith(ext) for ext in self.valid_extensions):
            _logger.info(f"File deleted: {filepath}")
            self.core.remove_image_from_index(filepath)

    def on_modified(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        if any(filepath.lower().endswith(ext) for ext in self.valid_extensions):
            _logger.info(f"File modified: {filepath}")
            self.core.index_image(filepath)  # Re-index on modification

class DirectoryWatcher:
    def __init__(self, core, config):
        self.core = core
        self.config = config
        self.watch_directories = config.get('watch_directories')
        self.event_handler = ImageEventHandler(core, config)
        self.observer = Observer()

    def run(self):
        for directory in self.watch_directories:
            if not os.path.exists(directory):
                _logger.warning(f"Directory {directory} does not exist. Skipping.")
                continue
            self.observer.schedule(self.event_handler, directory, recursive=True)
            _logger.info(f"Watching directory: {directory}")
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        _logger.info("Directory watcher stopped.")
