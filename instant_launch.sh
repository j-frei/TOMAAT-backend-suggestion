#!/bin/bash

python3 QueueManager.py & sleep 5s && (python3 WebService.py & python3 TaskScheduling.py)