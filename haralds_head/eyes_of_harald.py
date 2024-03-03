#!/usr/bin/env python3
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

import threading
import random
import math
import time
import sys
import logging

LEFT_EYE_PIN = 15
RIGHT_EYE_PIN = 18

threads = []

logger = logging.getLogger('haralds-eyes')


class HaraldsEye(threading.Thread):
    def __init__(self, pin, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.pin = pin
        self.eye_lights_up = False
        self.blink_counter = 0
        self.eyes_sync = False

    def run(self):
        while True:
            if self.blink_counter > 0:
                GPIO.output(self.pin, self.eye_lights_up)
                self.blink_counter -= 1
                # uniform blink
                time.sleep(0.5)
            else:
                GPIO.output(self.pin, False)
                # random blink
                if self.eyes_sync:
                    logger.debug(f"SYNC {self.pin}")
                    time.sleep(10 - time.localtime().tm_sec % 10)
                    self.eyes_sync = False
                else:
                    time.sleep(math.fabs(random.gauss(0.0, 1.0)))
            self.eye_lights_up = not self.eye_lights_up

    def alert(self):
        self.blink_counter = 7
        self.eye_lights_up = True

    def sync(self):
        self.eyes_sync = True


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LEFT_EYE_PIN, GPIO.OUT)
    GPIO.setup(RIGHT_EYE_PIN, GPIO.OUT)

    left_eye_thread = HaraldsEye(LEFT_EYE_PIN)
    left_eye_thread.start()

    right_eye_thread = HaraldsEye(RIGHT_EYE_PIN)
    right_eye_thread.start()

    threads.append(left_eye_thread)
    threads.append(right_eye_thread)


def blink():
    logger.info("blink")
    if math.fabs(random.gauss(0.0, 1.0)) > 1:
        for thread in threads:
            thread.sync()

    for thread in threads:
        thread.alert()


if __name__ == '__main__':
    logging.basicConfig(
            level=logging.INFO)

    setup()
    while True:
        blink()
        time.sleep(10)

    GPIO.cleanup()
