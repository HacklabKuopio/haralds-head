Harald's Head
=============

Harald's Head is a collection of scripts and LEDs and speaker, that together scan for Bluetooth devices and display
found device names on a sort of "wall of shame". The purpose of the project is to raise awareness of Bluetooth security.
The project gets its name from King Harald by whom Bluetooth protocol itself got its name.

## Setup

You may use one or two devices, such as Raspberry Pi. Install the project root into `/opt/haralds-head`.
You can `cd` into the base directory, where you can run the `Makefile` commands, and use Python interpreter,
or you can set `export PYTHONPATH=/opt/haralds-head` in your `.bashrc` to setup a development environment.

Make sure you have the `harald` user set up and that is has read and write access to the base directory!


### Wall of Harald & Flask of Harald

This setup is for the main RPi with HDMI screen attached.

The main haralds-head top directory should be installed or symlinked to /opt. Some paths are hardcoded to work that way.
Remember to build and activate the Python3 venv. If you choose any other location than `/home/harald` then you
need to reflect that change in the `bin` scripts. Note: The following install commands will fail if your system's time isn't correct.

    sudo apt install python3 python3-pip python3-venv
    python3 -m venv /home/harald/haralds-head-env
    source /home/harald/haralds-head-env/bin/activate
    pip3 install -r /opt/haralds-head/requirements.txt

NOTE: If you run this on other than Raspberry Pi device, you need to uninstall `RPi.GPIO` package and use Mock.GPIO.

    pip3 uninstall RPi.GPIO


Wall of Harald is the UI that looks best when run on a tty display. The systemd script starts it on tty1.
Remember to switch to TTY1 with ctrl-alt-F1 if you use the systemd service!

The wall works also in graphical environments, but unless your terminal has fullscreen mode without any title bar,
the graphics will not scale properly. The background is fitted for full HD 1920x1980 display.

You can add devices to `blacklist.txt`, by their name, to ignore from the display.

Copy the systemd wall script and enable it to display Harald's Wall on tty1 at boot.
The Flask server receives json data of the scanned devices and stores it into a txt file.
For Flask, there is also a systemd script that you can copy into place to automatically start Flask on boot.

    cd /opt/haralds-head
    make systemd

or

    sudo cp /opt/haralds-head/systemd/haralds-wall.service /usr/lib/systemd/system/
    sudo systemctl enable haralds-wall

    sudo cp /opt/haralds-head/systemd/haralds-flask.service /usr/lib/systemd/system/
    sudo systemctl enable haralds-flask

Either way, you can then start the services or reboot.

    sudo systemctl start haralds-wall
    sudo systemctl start haralds-flask


For development, you should run the wall in debug state so that it accepts ctrl-c exit key command.

    cd /opt/haralds-head
    make wall_debug

or

    python -m haralds_head.wall_of_harald --debug


### Eyes of Harald

Connect LEDs to GPIO pins 15 and 18 (BCM numbering). The "Wall" program flashes the eyes whenever it notices a change in the scanlog file.
You can debug the eyes independently, by entering the project root and running

    cd /opt/haralds-head
    make eyes

or

    python3 -m haralds_head.eyes_of_harald


### Voice of Harald

Harald speaks with `festival` text-to-speech software. Connect speakers to the Raspberry Pi where the Wall is running
and start the voice manually.

    cd /opt/haralds-head
    make voice

or

    python3 -m haralds_head.voice_of_harald


### Harald's BT Scanner

Start the bt-scanner code manually. This can run on the same or another device than the display. There may be also multiple scanners.
Remember to change the Flask server address and port in the script file!

    cd /opt/haralds-head/haralds-bt-scanner/
    sudo pip3 install -r requirements.txt
    sudo python3 harald-bt-scan.py

NOTE: if the bluetooth Python library from pip doesn't work, try the one from your distro's repos.

    sudo pip3 uninstall pybluez2
    sudo apt install python3-bluez

If the bluetooth device gets "jammed" from lots of starting & stopping, soft cycle it down.

    sudo hciconfig hci0 down
    sudo hciconfig hci0 up

