#!/bin/bash

python3 QueueManager.py 2>/dev/null & sleep 5s && (python3 WebService.py 2>/dev/null & python3 TaskScheduling.py 2>/dev/null)