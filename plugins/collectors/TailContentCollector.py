__author__ = 'lwz'

import os
import sys
import logging

from watchdog.events import FileSystemEventHandler
from pygtail import Pygtail


class TailContentCollector(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, offset_dir, onchange):
        """
        construct the needed function...
        """
        self.offset_dir = offset_dir
        self.onchange = onchange

    def on_moved(self, event):
        super(TailContentCollector, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(TailContentCollector, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(TailContentCollector, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(TailContentCollector, self).on_modified(event)

        # what = 'directory' if event.is_directory else 'file'
        # logging.info("Modified %s: %s", what, event.src_path)
        # split_path = None
        if sys.platform == "win32":
            split_path = "\\"
        else:
            split_path = "/"
        log_file = event.src_path.split(split_path)

        # prepare offset file directory
        if not os.path.exists(self.offset_dir):
            os.makedirs(self.offset_dir)
        offset_file = "%s/%s.os" % (self.offset_dir, log_file[-1])
        # offset file must separate with monitor directory, and is local variable...
        tailor = Pygtail(event.src_path, offset_file, paranoid=True)
        # must use gbk encoding...
        appended = tailor.read()
        if appended:
            decodeLog = appended.decode("gbk")
            logging.info("sending: %s", decodeLog)
            # execute callback function...
            self.onchange(decodeLog)
        else:
            logging.info("empty content: %s", event.src_path)

