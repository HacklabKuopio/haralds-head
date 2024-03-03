#!/usr/bin/env python3
from bluepy.btle import Scanner, DefaultDelegate, BTLEDisconnectError
import requests
import time
import threading
import logging

HARALDS_FLASK_SERVER = "http://10.42.0.1:5000"


class HaraldsLEScanner(threading.Thread):

    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.scanner = Scanner().withDelegate(ScanDelegate())

    def run(self):
        while True:
            print("running thread.....")
            try:
                devices = self.scanner.scan(15.0)
                self.store_scanlog(devices)
            except BTLEDisconnectError as err:
                logging.error(f"{err}")
            time.sleep(1)

    def store_scanlog(self, devices):
        with open('scanlog.txt', 'a') as f:
            for dev in devices:
                logging.info(f"device {dev.getScanData()}")
                name = dev.getValue(dev.COMPLETE_LOCAL_NAME) or dev.getValue(dev.SHORT_LOCAL_NAME)
                if name:
                    data = '{"name": "' + f"{name}" + '", ' + \
                            '"mac": "'  + f"{dev.addr}" + '", ' + \
                            '"rssi": "' + f"{dev.rssi}" + '"}\n' 
                    f.write(data)
                    try:
                        requests.post(
                             HARALDS_FLASK_SERVER + "/haralds-scan", 
                             json=data, 
                             timeout=5.0)
                    except Exception as err:
                        logging.warning(f"{err}")


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


if __name__ == '__main__':

    scanner = HaraldsLEScanner()
    scanner.start()
    scanner.join()


