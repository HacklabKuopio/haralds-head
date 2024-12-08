#!/bin/bash
ln -s /home/harald/haralds-head /opt/haralds-head
sudo chown harald:harald /opt/haralds-head
sudo apt update
apt remove -y python3-rpi.gpio
sudo apt install -y python3 python3-pip python3-venv make python3-rpi-lgpio
python3 -m venv /home/harald/haralds-head-env
source /home/harald/haralds-head-env/bin/activate
pip3 install -r /opt/haralds-head/requirements.txt
sudo cp /opt/haralds-head/systemd/haralds-wall.service /usr/lib/systemd/system/
sudo cp /opt/haralds-head/systemd/haralds-flask.service /usr/lib/systemd/system/
sudo systemctl enable haralds-wall
sudo systemctl enable haralds-flask
sudo systemctl start haralds-wall
sudo systemctl start haralds-flask
echo "Installation of Harald dependencies done!"