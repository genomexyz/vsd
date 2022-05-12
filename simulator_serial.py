import numpy as np
from datetime import datetime, timedelta
import time
import sys
import serial

#>>> ord(b'\xfc')
#252
#>>> ord(b'\xfd')
#253
#>>> ord(b'\xfa')
#250
#>>> ord(b'\xfe')
#254
#\xfb = 251
#ending data \xfb and newline (\n)

#setting
file_sample = 'sample.bin'
all_delimiter = [b'\xfa', b'\xfc', b'\xfd', b'\xfe', b'*', b'\xfb']
all_delimiter = [b'\xfc', b'\xfd', b'\xfe', b'*']
begone_delimiter = [b'\r', b'\n'] #\r\n

#redirect output to dev pipe
#f = open('endpoint1', 'w')
#sys.stdout = f
ser = serial.Serial('endpoint2')

single_file_open = open(file_sample, 'rb')
ori_bin = single_file_open.read()
ori_bin_mod = ori_bin
for ii in range(len(begone_delimiter)):
    ori_bin_mod = ori_bin_mod.replace(begone_delimiter[ii], b'')
ori_bin_mod.replace(b'\xfa', b'*')
ori_bin_mod.replace(b'\xfb', b'*')
    
kontainer_val = ''
delim = []
sampel_x = []
sampel_y = []
sampel_z = []
sampel_t = []
for ii in range(len(ori_bin_mod)):
    single_byte = ori_bin_mod[ii:ii+1]
    #print(single_byte)
    try:
        idx_delim = all_delimiter.index(single_byte)
        delim.append(all_delimiter[idx_delim])
        if len(delim) >= 2:
            val = int(kontainer_val)
            delim1 = delim[-2]
            delim2 = delim[-1]
            #print('cek delim', single_byte, delim)
            if delim1 ==  b'*' and delim2 == b'\xfc':
                sampel_x.append(val)
            elif delim1 ==  b'\xfc' and delim2 == b'\xfd':
                sampel_y.append(val)
            elif delim1 ==  b'\xfd' and delim2 == b'\xfe':
                sampel_z.append(val)
            elif delim1 ==  b'\xfe' and delim2 == b'*':
                sampel_t.append(val)
            #sampel_val.append(val)
            #print(val)
            kontainer_val = ''
        else:
            kontainer_val = ''
    except ValueError:
        try:
            kontainer_val += single_byte.decode('ascii')
        except UnicodeDecodeError:
            #reset
            kontainer_val = ''
            delim = []
    
sampel_x = np.array(sampel_x, dtype=np.int16)
sampel_y = np.array(sampel_y, dtype=np.int16)
sampel_z = np.array(sampel_z, dtype=np.int16)
sampel_t = np.array(sampel_t, dtype=np.int16)

#send data to the dev
while(True):
    begin_time = datetime.now()
    random_x = np.random.choice(sampel_x, 100)
    random_y = np.random.choice(sampel_y, 100)
    random_z = np.random.choice(sampel_z, 100)
    random_t = np.random.choice(sampel_t, 100)
    str_send = b''
    for i in range(len(random_x)):
        single_str_x = str(random_x[i])
        single_str_y = str(random_y[i])
        single_str_z = str(random_z[i])
        single_str_t = str(random_t[i])
        if str_send == b'':
            str_send += b'*'
        str_x = bytes(single_str_x, 'utf-8')
        str_y = bytes(single_str_y, 'utf-8')
        str_z = bytes(single_str_z, 'utf-8')
        str_t = bytes(single_str_t, 'utf-8')
        str_send += str_x+b'\xfc'+str_y+b'\xfd'+str_z+b'\xfe'+str_t+b'*'
    str_send += b'\xfb'+b'\n'
    final_time = datetime.now()
    diff_time = final_time - begin_time
    delay_time = 1000 - diff_time.microseconds
    if delay_time > 0:
        time.sleep(delay_time/1000)
    #print(str_send)
    ser.write(str_send)
