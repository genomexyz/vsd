import numpy as np
from datetime import datetime, timedelta
import time
import sys
import serial

#setting
dev_file = 'endpoint1'

ser = serial.Serial(dev_file)

while True:
    line = ser.readline()
    print(line)