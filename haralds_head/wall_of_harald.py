#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
SCAN_LOG_FILE = SCAN_LOG_DIRECTORY + "/disobey-scanlog.txt"

ITEMS_TO_SHOW = 4

logger = logging.getLogger('haralds-mind')

seen_devices = []
blacklist = []

greetings = [
    "wow so many devices",
    "come here"
]



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


# class DynamicTextEffect(Print):
#     def __init__(self, screen, filename, **kwargs):
#         super(DynamicTextEffect, self).__init__(screen, StaticRenderer(images=[""]), **kwargs)
#         self._filename = filename
#         self._last_text = ""
#         self._update_text()

#     def _update_text(self, text=None):
#         logger.info("XXXX")
#         if text is None:
#             with open(self._filename, 'r') as file:
#                 text = file.read()
#         if text != self._last_text:
#             self._last_text = text
#             self._renderer = StaticRenderer(images=[text])
#             self._clear = True


def read_devices():
    pass



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
        # self._label = Label("", height=screen.height, width=screen.width))
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
            with open(self._filename, 'r') as file:
                text = file.read()

        _text = ""

        results = HaraldsJsonReader.read_fake_json()['results']

        unique_results = {each['name'] : each for each in results}.values()

        # names = [d.get('name', None) for d in unique_results]
        #    logger.debug(f"new device {dev['name']}")

        # [k for (k, v) in d.items() if 'him' in v]

        for device in unique_results:
            if not any(x == device['name'] for x in blacklist):
                name = device['name'].strip()
                _text += f"{device['mac'][:5]}\t{name}\n"

        text = _text

        # blink eyes
        blink()

        # say greeting
        names = [d.get('name', None) for d in unique_results]
        names2 = []
        for name in names:
            if not name.startswith('5AEA'):
                names2.append(name)

        greeting = f"hello {choice(names2)}"
        logger.debug(f"say {greeting}")
        # voice does not apparently work from systemd service
        #os.system(f"echo hello {greeting} | festival --tts")
        with open('/opt/haralds-head/haralds-greeting.txt', 'w') as file:
            file.write(greeting + '\n')

        if text != self._last_text:
            self._last_text = text
            self._label.text = text
            self._label.reset()



# class DemoFrame(Frame):

#     def __init__(self, screen):
#         super(DemoFrame, self).__init__(screen,
#                                         screen.height // 2,
#                                         screen.width // 2,
#                                         has_border=True,
#                                         name="Wall")

#         figlet_text = FigletText("Uusi laite", font="ogre")
#         layout0 = Layout([1], fill_frame=False)
#         self.add_layout(layout0)
#         layout0.add_widget(Label(figlet_text, align="^", height=5))

#         layout = Layout([1, 1], fill_frame=True)
#         self.add_layout(layout)

#         # text1 = pyfiglet.figlet_format("Text 1", font="slant")
#         # text2 = pyfiglet.figlet_format("Text 2", font="slant")
#         # text3 = pyfiglet.figlet_format("Text 3", font="slant")

#         column_text1 = "Device 1"
#         column_text2 = "ad:dr"

#         layout.add_widget(Label(column_text1), 0)
#         layout.add_widget(Label(column_text2), 1)

#         self.fix()

#     def update(self, frame_no):
#         # WIP
#         logger.debug("frame update")
#         super(DemoFrame, self).update(frame_no)


class HaraldsMind(object):

    def __init__(self):
        logger.info("Harald's Mind startup")

        # signal.signal(signal.SIGIO, self.scan_file_handler)
        # fd = os.open(SCAN_LOG_DIRECTORY,  os.O_RDONLY)
        # fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        # fcntl.fcntl(fd, fcntl.F_NOTIFY,
        #             fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

        self.screen = None
        # start-up read
        # self.scan_file_handler(0, 0)

        # if len(self.scan_items) == 0:
        #     self.scan_items = [{"name": "Scanning...", "mac": "", "rssi": "0"}]


    def scan_file_handler(self, signum, frame):
        logger.debug("scan log file changed")
        self.scan_items = HaraldsJsonReader.read_fake_json()['results']
        logger.debug(f"Items: {len(self.scan_items)}")
        #logger.debug(self.screen)
        if self.screen is not None:
            self.screen.force_update()
            self.screen.refresh()


    def harald(self, screen):
        global dynamic_text
        global dynamic_text_frame
        scenes = []

        effects = []

        # background = ColourImageFile(screen, "/opt/haralds-head/assets/background2.gif", screen.height, screen.width, -1, uni=False, dither=False),

        effects = [
            Print(
                screen,
                ColourImageFile(screen, "/opt/haralds-head/assets/background2.gif", screen.height, uni=False, dither=False),
                #ColourImageFile(screen, "background.gif", screen.height, uni=False, dither=False),
                # ColourImageFile(screen, "Vintage_Ornamental_Illustration_inverted8.png", screen.height, uni=False, dither=False),
                # ImageFile("Vintage_Ornamental_Illustration_inverted2.png", screen.height, colours=screen.colours),
                # ImageFile("Vintage_Ornamental_Illustration_ClipArtPlace.webp", screen.height, colours=screen.colours),
                # Rainbow(screen, ImageFile("Vintage_Ornamental_Illustration_inverted2.png", screen.height, colours=screen.colours)),
                # Plasma(screen, ImageFile("Vintage_Ornamental_Illustration_inverted2.png", screen.height, colours=screen.colours), colours=_256_palette),
                0,
                1,
                transparent=False,
                speed=1,
            ),
        ]

        # left column scan items
#        for i in range(0, min(ITEMS_TO_SHOW, len(self.scan_items))):
#            _msg = FigletText(f"{self.scan_items[-(i+1)]['name']}", "ogre")
#            effects.append(
#                Print(screen,
#                        _msg,
#                        12 + 5 * i - 1,
#                        x=(screen.width - _msg.max_width) // 4,
#                        colour=Screen.COLOUR_GREEN,
#                        stop_frame=80,
#                        speed=1))
#
#        # right column scan items
#        # for i in range(0, 5):
#        for i in range(0, min(ITEMS_TO_SHOW, len(self.scan_items))):
#            _msg = FigletText(f"{self.scan_items[-(i+1)]['mac'][:5]}", "stampate")
#            # _msg = FigletText(f"aa:bb:cc:00:11:22:33:44", "stampate")
#            effects.append(
#                Print(screen,
#                        _msg,
#                        12 + 6 * i - 1,
#                        x=(screen.width - _msg.max_width) // 4 + (screen.width // 3),
#                        colour=Screen.COLOUR_GREEN,
#                        stop_frame=80,
#                        speed=1))

        # "title"
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

        # effects.append(DemoFrame(screen))

        # effects.append(background)

        # dynamic_text = DynamicTextEffect(screen, filename, x=10, y=10)


        dynamic_text_frame = DynamicTextFrame(screen, filename)
        effects.append(dynamic_text_frame)

        # scenes.append(Scene([background, dynamic_frame], -1))



        # scenes.append(Scene([background]))

        # scenes[0].add_effect(dynamic_text)

        scenes.append(Scene(effects))


        # self.screen = screen
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
        filename='/home/harald/mind.log',
        encoding="utf-8",
        level=logging.DEBUG,
        format="%(asctime)s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S"
    )

    eyes_setup()
    haralds_mind = HaraldsMind()

    while True:
        try:
            Screen.wrapper(haralds_mind.harald, catch_interrupt=not options.debug)
            # Screen.wrapper(haralds_mind.harald, arguments=[filename])
            sys.exit(0)
        except ResizeScreenError:
            pass
        finally:
            observer.stop()
            observer.join()

