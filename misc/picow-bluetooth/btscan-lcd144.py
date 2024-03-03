from machine import Pin,SPI,PWM
import framebuf
import time
import bluetooth
import binascii

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

_IRQ_SCAN_RESULT = const(5)
devices = []

def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, connectable, rssi, adv_data = data
        address = binascii.hexlify(addr).decode()
        # ttl (time-to-live) is how long the device stays on the list (minimum sec)
        if rssi > -25:
            device_ttl = 10
        elif rssi > -75:
            device_ttl = 5
        elif rssi > -100:
            device_ttl = 3
        else:
            device_ttl = 1

        device = [item for item in devices if item['address'] == address]
        if len(device) == 0:
            devices.append({'address': address, 'rssi': rssi, 'ttl': device_ttl})
        else:
            # update its ttl value
            device[0]['ttl'] = device_ttl
            # TODO: clean this hack
            for index, dev in enumerate(devices):
                if dev['address'] == device[0]['address']:
                    del devices[index]
                    devices.append(device[0])


class LCD_1inch44(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 128
        self.height = 128

        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)

        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()


        self.WHITE  =   0xFFFF
        self.BLACK  =  0x0000
        self.GREEN  =  0x001F
        self.RED    =  0xF800
        self.BLUE   = 0x06E0
        self.GBLUE  = 0X07FF
        self.PINK   = 0xFFE0

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36);
        self.write_data(0x70);

        self.write_cmd(0x3A);
        self.write_data(0x05);

         #ST7735R Frame Rate
        self.write_cmd(0xB1);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB2);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB3);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB4); #Column inversion
        self.write_data(0x07);

        #ST7735R Power Sequence
        self.write_cmd(0xC0);
        self.write_data(0xA2);
        self.write_data(0x02);
        self.write_data(0x84);
        self.write_cmd(0xC1);
        self.write_data(0xC5);

        self.write_cmd(0xC2);
        self.write_data(0x0A);
        self.write_data(0x00);

        self.write_cmd(0xC3);
        self.write_data(0x8A);
        self.write_data(0x2A);
        self.write_cmd(0xC4);
        self.write_data(0x8A);
        self.write_data(0xEE);

        self.write_cmd(0xC5); #VCOM
        self.write_data(0x0E);

        #ST7735R Gamma Sequence
        self.write_cmd(0xe0);
        self.write_data(0x0f);
        self.write_data(0x1a);
        self.write_data(0x0f);
        self.write_data(0x18);
        self.write_data(0x2f);
        self.write_data(0x28);
        self.write_data(0x20);
        self.write_data(0x22);
        self.write_data(0x1f);
        self.write_data(0x1b);
        self.write_data(0x23);
        self.write_data(0x37);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x02);
        self.write_data(0x10);

        self.write_cmd(0xe1);
        self.write_data(0x0f);
        self.write_data(0x1b);
        self.write_data(0x0f);
        self.write_data(0x17);
        self.write_data(0x33);
        self.write_data(0x2c);
        self.write_data(0x29);
        self.write_data(0x2e);
        self.write_data(0x30);
        self.write_data(0x30);
        self.write_data(0x39);
        self.write_data(0x3f);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x03);
        self.write_data(0x10);

        self.write_cmd(0xF0); #Enable test command
        self.write_data(0x01);

        self.write_cmd(0xF6); #Disable ram power save mode
        self.write_data(0x00);
            #sleep out
        self.write_cmd(0x11);
        #Turn on the LCD display
        self.write_cmd(0x29);

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x00)
        self.write_data(0x80)

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x02)
        self.write_data(0x00)
        self.write_data(0x82)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)


if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    LCD = LCD_1inch44()
    LCD.fill(LCD.BLACK)
    LCD.show()

    # key0 = Pin(15,Pin.IN,Pin.PULL_UP)
    # key1 = Pin(17,Pin.IN,Pin.PULL_UP)
    # key2 = Pin(2 ,Pin.IN,Pin.PULL_UP)
    # key3 = Pin(3 ,Pin.IN,Pin.PULL_UP)

    ble = bluetooth.BLE()
    ble.active('active')
    ble.irq(bt_irq)
    ble.gap_scan(0, 1000)

    while (1):
        time.sleep(1)
        LCD.fill(LCD.BLACK)
        LCD.text("Bluetooth scan", 8, 8, LCD.GBLUE)
        LCD.hline(2, 19, 126, LCD.BLUE)

        # sort by rssi
        devs = sorted(devices, key=lambda item:item['rssi'], reverse=True)
        y = 24
        for device in devs:
            addr = device['address']
            rssi = device['rssi']
            LCD.text(addr[0:4] + " " + str(rssi), 2, y, LCD.WHITE)
            # LCD.text(" " + str(rssi),10,y,LCD.WHITE)
            # color bars by signal strength
            if rssi > -55: color = LCD.BLUE
            elif rssi > -85: color = LCD.GREEN
            else: color = LCD.RED
            LCD.fill_rect(70, y, 100 + rssi, 8, color)
            y += 10

            # decrease ttl and remove device from items if ttl==0
            device['ttl'] -= 1
            if device['ttl'] <= 0:
                for index, _dev in enumerate(devices):
                    if _dev['address'] == device['address']:
                        del devices[index]

        LCD.show()

