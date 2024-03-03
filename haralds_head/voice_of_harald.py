#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023, 2024 Kuopio Hacklab
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
import sys
import time
import os
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


HARALDS_GREETING_FILE = "/opt/haralds-head/haralds-greeting.txt"

logger = logging.getLogger('haralds-greeting')

last_phrase = None


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, callback):
        self.filename = filename
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.filename:
            with open(self.filename, 'r') as file:
                data = file.read()
            self.callback(data)


filename = HARALDS_GREETING_FILE
observer = Observer()

def callback(text):
    global last_phrase
    if text != last_phrase:
        logger.info(f"say {text}")
        os.system(f"echo '{text}' | festival --tts")
    last_phrase = text

event_handler = FileChangeHandler(filename, callback)
observer.schedule(event_handler, path='/opt/haralds-head/', recursive=False)


if __name__ == "__main__":

    observer.start()

    logging.basicConfig(
        #filename='/opt/haralds-head/wall.log',
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S"
    )

    while True:
        try:
            time.sleep(10)
        except Exception as err:
            logger.warning(err)

    observer.stop()
    observer.join()

