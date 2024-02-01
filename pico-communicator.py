import machine
from machine import Pin, SPI
import ntptime
import time
from time import sleep
import network
import socket
import urequests
import ssl
import gc
import json
import urequests as requests
import ujson
import framebuf
import utime


led = machine.Pin("LED", machine.Pin.OUT)
led.on()
sleep(1)
led.off()
sleep(1)
led.on()

ssid = 'Disobey-X99'
password = 'hacklab8'

#if needed, overwrite default time server
ntptime.host = "pool.ntp.org"
gmt_hours_modifier = 2 * 3600 # hours * seconds

#from picozero import pico_temp_sensor, pico_led
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Scan for available networks
    #print(wlan.scan())
    
    # Set wifi channel
    #wlan.config(channel=11)
    try:
        wlan.connect(ssid, password)
        while wlan.isconnected() == False:
            print('Waiting for connection...')
            sleep(1)
            wifi_status_code = wlan.status()
            print("Wifi status: ", wifi_status_code)
            sleep(1)
        print(wlan.ifconfig())
    
        return wlan
    except OSError as error:
        print(f'error is {error}')
        sleep(30)
        connect()

def sync_time():
    try:
      #print("Local time before synchronization：%s" %str(time.localtime()))
      #make sure to have internet connection
      ntptime.settime()

    except Exception as error:
      print("Error syncing time: ", error)

def send_json(url, data=None):
    print("Sending json")
    #"https://api.porssisahko.net/v1/price.json?date=",current_date,"&hour=",current_hour)
    #"https://api.porssisahko.net/v1/latest-prices.json")

    post_data = ujson.dumps({"name": "Secure-Bluetooth", "mac": "deadbeef:0000"})
    res = requests.post(url, headers = {'content-type': 'application/json'}, data = post_data)
    text = res.text
    print("Response: ", text)
    return text

    #request_url = "https://api.porssisahko.net/v1/price.json?date="+current_date+"&hour="+current_hour
    #print(request_url)
    #try:
    #    request = urequests.get(request_url)
    #    response = request.text
    #    print(response)
    #    json_data = json.loads(response)
    #    price = json_data["price"]
    #    #print(price)
    #    print("{:02d}.{:02d}.{} {:02d}:{:02d}".format(current_time[2], current_time[1], current_time[0], current_time[3], current_time[4]))
    #    print("Hinta nyt: {0:.2f} snt/kWh".format(price))
    #    return price
    #except Exception as e:
    #    print(e)
    
def main():
    try:
        wlan = connect()
        ip = wlan.ifconfig()[0]
        print("Current IP: ", ip)
        
        #sync_time()

        while True:
            send_json("http://10.42.0.30:5000/new")
            #wlan.disconnect()
            #print("Disconnected wlan")
            sleep(30)
            gc.collect()

    except KeyboardInterrupt:
        machine.reset()

if __name__=='__main__':
    main()
