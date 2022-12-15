from cmath import pi
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.cm as cm
#import pandas as pd
import time
from multiprocessing import Pool, Array, Pipe
import os
import traceback
import datetime
import serial

import serial.tools.list_ports
from easygui import *

#from pathlib import Path

debug = 0

ID = 0
Seconds = 0
Minutes = 0
Hours = 0
EnviTemp = 0

def readRawData(port):
    global debug

    global ID
    global Seconds
    global Minutes
    global Hours
    global EnviTemp

    Dataleng = 0
    raw_binary = b''
    raw_array = []
    try:
        while Dataleng != 135:
            ser = serial.Serial(port, 1152000000,timeout=0.1)
            raw_binary=ser.read_until(expected= b'\xaa\xaa')
            if raw_binary.startswith(b'\xee\xee'):
                raw_binary = raw_binary.replace(b'\xee\xee',b'').replace(b'\xaa\xaa',b'')
                Dataleng = len(raw_binary)
            
            if debug == 1:
                print(Dataleng)
                print(raw_binary)
            ser.close()

        ID = raw_binary[0]
        Seconds = raw_binary[1]
        Minutes = raw_binary[2]
        Hours = raw_binary[3]
        Holder = raw_binary[4]
        EnviTemp = ((raw_binary[6] << 8) | raw_binary[5])*0.0625

        length = 135
        readRawData_i = 7
        
        while raw_binary:
            raw_array.append(((raw_binary[readRawData_i+1] << 8) | raw_binary[readRawData_i])*0.25)
            readRawData_i = readRawData_i + 2
            if readRawData_i >= length:
                readRawData_i = 0
                break
    except Exception as e:
        errorlog = os.getcwd() + '\\Log\\Sensor' + port + "_error.log"
        with open(errorlog,'a') as errorfile:
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] Error:' + str(e))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] traceback:' + str(traceback.format_exc()))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] raw_binary:' + str(raw_binary))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] raw_array:' + str(raw_array))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] Dataleng:' + str(Dataleng))
    return raw_array

def parseData(port):
    global debug
    
    raw_array = readRawData(port)
    
    try:
        raw_data = np.zeros((8, 8))
        i = 0
        for xi in range (0,8):
            for yi in range (0,8):
                raw_data[xi, yi] = raw_array[i]
                i = i + 1
    except Exception as e:
        errorlog = os.getcwd() + '\\Log\\Sensor' + port + "_error.log"
        with open(errorlog,'a') as errorfile:
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] Error:' + str(e))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] traceback:' + str(traceback.format_exc()))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] raw_data:' + str(raw_data))
    return raw_data

def get_sensor_data(port):
    global debug
    
    print('Run task for port %s (%s)...' % (port, os.getpid()))
    print("port:",port)

    try:

        filename = os.getcwd() + '\\Log\\Sensor' + port + ".txt"
        logname = os.getcwd() + '\\Log\\Sensor' + port + ".csv"
        header = 'DeviceID,EnviTemp,Hours,Minutes,Seconds,SystemTime,P01,P02,P03,P04,P05,P06,P07,P08,P09,P10,P11,P12,P13,P14,P15,P16,P17,P18,P19,P20,P21,P22,P23,P24,P25,P26,P27,P28,P29,P30,P31,P32,P33,P34,P35,P36,P37,P38,P39,P40,P41,P42,P43,P44,P45,P46,P47,P48,P49,P50,P51,P52,P53,P54,P55,P56,P57,P58,P59,P60,P61,P62,P63,P64\n'
        with open(logname,'a') as logfile:
            logfile.write(header)

        while True:
            start_time = time.time()

            port_data = parseData(port)

            if debug == 1:
                print(port_data,port)

            end_time = time.time()

            if debug == 1:
                print('[parseData]: Task for port %s runs %0.2f seconds.' % (port, (end_time - start_time)))

            np.savetxt(filename, port_data, delimiter=',', fmt='%1.2f')
            
            with open(logname,'a') as logfile:
                record = str(ID).zfill(2) + ',' + str(EnviTemp).zfill(2) + ',' + str(Hours).zfill(2) + ',' + str(Minutes).zfill(2) + ',' + str(Seconds).zfill(2) + ',' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+','
                logfile.write(record)
                port_data.tofile(logfile,sep=',')
                logfile.write('\n')
            
            port_data = []
            
            time.sleep(0.01)

    except Exception as e:
        errorlog = os.getcwd() + '\\Log\\Sensor' + port + "_error.log"
        with open(errorlog,'a') as errorfile:
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] Error:' + str(e))
                errorfile.write('[Device ID:'+ str(ID).zfill(2) + '] traceback:' + str(traceback.format_exc()))
                np.savetxt(errorlog, port_data, delimiter=',', fmt='%1.2f')

def get_com_ports():
    global debug
    
    log_folder = os.getcwd() + '\\Log\\'
 
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    port_list = list(serial.tools.list_ports.comports())
    portfile = os.getcwd() + '\\Log\\' + "Ports.txt"
    ports = []

    print(portfile)

    with open(portfile, 'w') as fp:
        if len(port_list) <= 0:
            print("This Serial Port Can not Find!!")
        else:
            for i in list(port_list):
                if str(i.hwid).startswith('USB VID:PID='):
                    if debug == 1:
                        print(i.hwid)
                        print(i)
                        print(ID)                        
                    ports.append(i.name)
                    readRawData(i.name)
                    fp.write(str(ID).zfill(2)+ ',' + i.name + '\n')
    return ports

def main():
    global debug
    
    print('Parent process %s.' % os.getpid())

    ports = get_com_ports()

    if debug == 1:
        print(len(ports))
        print(ports)

    p = Pool(len(ports))

    try:
        for port in ports:
            p.apply_async(get_sensor_data, args=(port,))
        print('Waiting for all subprocesses done...')
        p.close()
        p.join()
        print('All subprocesses done.')

    except KeyboardInterrupt:
        p.terminate()
        p.join()
if __name__ == '__main__':
    main()