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
from asciimatics.effects import BannerText, Print, Scroll, Background
from asciimatics.renderers import ColourImageFile, FigletText, ImageFile, Fire, Plasma, Rainbow, StaticRenderer
from asciimatics.scene import Scene
from asciimatics.screen import Screen, ManagedScreen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.widgets import Frame, Layout, Label
from iteration_utilities import unique_everseen
from optparse import OptionParser
from random import choice
import pyfiglet
import sys
import time
import fcntl
import os
import signal
import logging
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from haralds_head.scanlog_reader import HaraldsJsonReader
from haralds_head.eyes_of_harald import setup as eyes_setup
from haralds_head.eyes_of_harald import blink


SCAN_LOG_DIRECTORY = "/opt/haralds-head/scans"
SCAN_LOG_FILE = SCAN_LOG_DIRECTORY + "/haralds-scanlog.txt"

ITEMS_TO_SHOW = 4

logger = logging.getLogger('haralds-wall')

seen_devices = []
blacklist = []

dynamic_text = None
dynamic_text_frame = None


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, callback):
        self.filename = filename
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.filename:
            with open(self.filename, 'r') as file:
                data = file.read()
            self.callback(data)


class DynamicTextFrame(Frame):
    def __init__(self, screen, filename):
        super(DynamicTextFrame, self).__init__(
            screen,
            screen.height // 2 - 2,
            screen.width // 3,
            y=8,
            x=100,
            has_border=False,
            can_scroll=False,
            name="DynamicText"
        )
        self._filename = filename
        self._last_text = ""
        self._label = Label("", height=screen.height)
        layout = Layout([50], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._label)
        self.fix()
        self.set_theme("monochrome")
        self._update_text()

    def _update_text(self, text=None):

        blacklist = []
        with open('/opt/haralds-head/blacklist.txt', 'r') as file:
            for d in file.readlines():
                blacklist.append(d.strip())

        if text is None:
            try:
                with open(self._filename, 'r') as file:
                    text = file.read()
            except Exception as err:
                logger.warning(err)

        _text = ""

        results = HaraldsJsonReader.read_scanlog_json()['results']

        unique_results = {each['name'] : each for each in results}.values()

        for device in unique_results:
            if not any(x == device['name'] for x in blacklist):
                name = device['name'].strip()
                _text += f"{device['mac'][:5]}\t{name}\n"

        text = _text

        # blink eyes
        blink()

        # say greeting via text file that voice_of_harald listens to
        names = [d.get('name', None) for d in unique_results]
        if len(names):
            greeting = f"hello {choice(names)}"
            logger.debug(f"say {greeting}")
            # voice does not apparently work from systemd service
            #os.system(f"echo hello {greeting} | festival --tts")
            with open('/opt/haralds-head/haralds-greeting.txt', 'w') as file:
                file.write(greeting + '\n')
        else:
            text = 'Waiting for scan results...'

        if text != self._last_text:
            self._last_text = text
            self._label.text = text
            self._label.reset()


class HaraldsMind(object):

    def __init__(self):
        logger.info("Harald's Mind startup")
        self.screen = None


    def scan_file_handler(self, signum, frame):
        logger.debug("scan log file changed")
        self.scan_items = HaraldsJsonReader.read_scanlog_json()['results']
        logger.debug(f"Items: {len(self.scan_items)}")
        if self.screen is not None:
            self.screen.force_update()
            self.screen.refresh()


    def harald(self, screen):
        global dynamic_text
        global dynamic_text_frame
        scenes = []

        effects = [
            Print(
                screen,
                ColourImageFile(screen, "/opt/haralds-head/assets/background2.gif", screen.height, uni=False, dither=False),
                0,
                1,
                transparent=False,
                speed=1,
            ),
        ]

        msg = FigletText("WALL of HARALD", "crazy")
        effects.append(
            Print(screen,
                    msg,
                    (screen.height // 2) + 8,
                    x=(screen.width - msg.max_width) // 2 + 1,
                        colour=Screen.COLOUR_BLACK,
                    stop_frame=25,
                    speed=1))
        effects.append(
            Print(screen,
                    Rainbow(screen, msg),
                    (screen.height // 2) + 8,
                    x=(screen.width - msg.max_width) // 2,
                    colour=Screen.COLOUR_BLACK,
                    stop_frame=25,
                    speed=1))

        dynamic_text_frame = DynamicTextFrame(screen, filename)
        effects.append(dynamic_text_frame)
        scenes.append(Scene(effects))

        logger.debug("play scenes")
        screen.play(scenes, stop_on_resize=True)


filename = SCAN_LOG_FILE
observer = Observer()

def callback(text):
    # global dynamic_text
    global dynamic_text_frame
    dynamic_text_frame._update_text(text)

event_handler = FileChangeHandler(filename, callback)
observer.schedule(event_handler, path=SCAN_LOG_DIRECTORY, recursive=False)
observer.start()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-d", "--debug", dest="debug", action="store_true", default=False)

    (options, args) = parser.parse_args()

    logging.basicConfig(
        filename='/opt/haralds-head/wall.log',
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S"
    )

    eyes_setup()
    haralds_mind = HaraldsMind()

    while True:
        try:
            Screen.wrapper(haralds_mind.harald, catch_interrupt=not options.debug)
            sys.exit(0)
        except ResizeScreenError:
            pass
        finally:
            observer.stop()
            observer.join()
