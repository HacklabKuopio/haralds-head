#!/usr/bin/env bash
source /home/harald/haralds-head-env/bin/activate
cd /opt/haralds-head && \
PYTHONPATH=/opt/haralds-head python3 -m haralds_head.wall_of_harald
