import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart_process()

    def restart_process(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(self.command, shell=True)

    def on_any_event(self, event):
        self.restart_process()

if __name__ == "__main__":
    command = " ".join(sys.argv[1:])
    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()