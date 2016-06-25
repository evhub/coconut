import time
import sys
import os
from .command import code_exts
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CompilerHandler(FileSystemEventHandler):

    def __init__(self,cli,write, package, run, force):
        self.cli = cli
        self.write = write
        self.package = package
        self.run = run
        self.force = force

    def on_modified(self,event):
        path = event.src_path
        filename,extention = os.path.splitext(path)
        if extention in code_exts:
            self.cli.compile_path(path,self.write,self.package,self.run,self.force)

def realWatch(cli,source, write, package, run, force):
    event_handler = CompilerHandler(cli,write,package,run,force)
    observer = Observer()
    observer.schedule(event_handler,source,recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    sys.exit(0)