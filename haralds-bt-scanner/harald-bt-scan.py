#!/usr/bin/env python3
import bluetooth
from bluetooth.ble import DiscoveryService
from optparse import OptionParser
import requests
import time
import threading
import logging
import re

HARALDS_FLASK_SERVER = "http://192.168.10.1:5000"

logger = logging.getLogger("btscan")


class HaraldsBTScanner(object):
    def __init__(self, timeout):
        self.classic_scanner = HaraldsBTScanner.ClassicScanner(timeout)
        self.ble_scanner = HaraldsBTScanner.BLEScanner(timeout)

    def start(self):
        logger.info("Starting Harald Scanner")
        # scanning concurrently does not discover all devices...
        while True:
            self.classic_scanner.scan()
            #self.classic_scanner.join()

            self.ble_scanner.scan()
            #self.ble_scanner.join()


    class ClassicScanner(threading.Thread):
        def __init__(self, timeout, *args):
            threading.Thread.__init__(self)
            self.timeout = timeout

        def scan(self):
            logger.info("\x1b[34;20mScanning classic...\x1b[0m")
            try:
                devices = bluetooth.discover_devices(duration=self.timeout, lookup_names=True)
                for addr, name in devices:
                    # RSSI is not directly available for classic Bluetooth in PyBluez
                    logger.info(f"Classic - Name: {name}, MAC: {addr}")
                    HaraldsBTScanner.store_scanlog({"name": name, "addr": addr})
            except Exception as e:
                logger.warn(f"Error retrieving classic Bluetooth device info: {e}")
                time.sleep(2)


    class BLEScanner(threading.Thread):
        def __init__(self, timeout, *args):
            threading.Thread.__init__(self)
            self.timeout = timeout
            self.service = DiscoveryService()

        def scan(self):
            logger.info("\x1b[34;20mScanning BLE...\x1b[0m")
            try:
                devices = self.service.discover(self.timeout)
                for addr, name in devices.items():
                    if name:
                        logger.info(f"BLE - Name: {name}, mac: {addr}")
                        HaraldsBTScanner.store_scanlog({"name": name, "addr": addr})
            except Exception as e:
                logger.warn(f"Error retrieving ble Bluetooth device info: {e}")
                time.sleep(2)


    @staticmethod
    def store_scanlog(dev):
        name = dev['name']
        if name:
            data = '{"name": "' + f"{name}" + '", ' + \
                    '"mac": "'  + f"{dev['addr']}" + '"}\n'

            # save to local txt file
            with open('scanlog.txt', 'a') as f:
                f.write(data)

            # send out the data to remote server, but ignore
            # any devices with strange emojis or other simple hacking attempts
            if not re.match("^[a-zA-Z0-9 _-–’]*$", name):
                logger.warning(f"IGNORE device {name}")
            else:
                logger.debug(f"POST device {name}")
                try:
                    requests.post(
                            HARALDS_FLASK_SERVER + "/haralds-scan",
                            json=data,
                            timeout=5.0)
                except Exception as err:
                    logger.warning(f"{err}")


if __name__ == '__main__':
    # options
    parser = OptionParser()
    parser.add_option(
        "-t", "--timeout", dest="timeout", action="store", default=10)
    parser.add_option(
        "-d", "--debug", dest="debug", action="store_true", default=False)

    (options, args) = parser.parse_args()

    logging.basicConfig(
        #filename='/dev/null',
        encoding="utf-8",
        level=logging.DEBUG if options.debug else logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S")

    scanner = HaraldsBTScanner(int(options.timeout))
    scanner.start()
