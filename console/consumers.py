from channels.generic.websocket import AsyncWebsocketConsumer

import json
import os
import threading
import subprocess
from random import randint
from asyncio import sleep
import pickle
from random import randint
import pandas as pd

scriptDir = os.path.abspath(os.path.dirname(__file__))
fileName = '/capture.csv'
capFile = scriptDir + fileName

## readCaptured CSV functionality
def readCaptured(capFile):
    with open(capFile, "r") as f:
        data = f.read().splitlines()
    return data

def makeItLive(capFile, period=0.15):
    data = readCaptured(capFile)
    while True:
        sleep(period)
        new_data = readCaptured(capFile)
        yield new_data[len(data):]
        data = new_data


## WebSocket xxxx
class ConsoleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # some func
        # for i in range(1000):
        #     await self.send(json.dumps({ "value" : randint(0, 5)}))
        #     await sleep(1)

        # 1. Live Capture capture.csv [[ tshark will be in OPS, so let's see what it's writing ]]

        prev_mac_source = ''
        prev_mac_dest = ''
        prev_prediction = 0
        scanDict = {}

        # attack type dictionary - key -> prediction, value -> attack type
        attack_type = {
            0: 'Normal',
            1: 'Wrong Setup',
            2: 'DDOS',
            3: 'Data Type Probing',
            4: 'Scan Attack',
            5: 'MITM'
        }

        # specify file name of machine learning model - pickle file
        filename = 'ml_models/nbad_model'
        infile = open(filename, 'rb')
        rf_model = pickle.load(infile)

        x = makeItLive(capFile)

        for lines in x:
            lines = lines[1:]
            for line in lines:
                line = line.rstrip("\n")[1:]
                returnLog = line  # storing in temp var to return as log
                # line = line.strip()
                line = line.split('$')

                # print(line)

                if len(line) == 13:  # ----------------------------------------------------------- data cleaning

                    line[1] = line[1].split(' ')[4].replace(':', '').replace('.', '')  # pre time

                    line[3] = int(line[3].replace(':', ''), 16)  # pre eth src
                    line[4] = int(line[4].replace(':', ''), 16)  # pre eth dst
                    try:
                        line[5] = float(line[5].replace('.', ''))  # pre ip src
                    except Exception as ex:
                        line[5] = 0
                    try:
                        line[6] = float(line[6].replace('.', ''))  # pre ip dst
                    except Exception as ex:
                        line[6] = 0
                    try:
                        line[7] = int(line[7])  # pre protocol
                    except Exception as ex:
                        line[7] = -1
                    try:
                        line[8] = int(line[8])  # pre ip length
                    except Exception as ex:
                        line[8] = 0
                    try:
                        line[9] = int(line[9])  # tcp length
                    except Exception as ex:
                        line[9] = 0
                    try:
                        line[10] = int(line[10])  # tcp source port
                    except Exception as ex:
                        line[10] = 0
                    try:
                        line[11] = int(line[11])  # tcp destination port
                    except Exception as ex:
                        line[11] = 0
                    value = -99

                    # ------------------------------------------------------------------------ data preprocessing

                    if(line[-1].startswith("GET / HTTP/1.1 ")):  # NORMAL DATA
                        value = -99

                    elif (line[-1].startswith("GET")):  # WRONG SETUP / DATA TYPE PROBING
                        a = line[-1].split("=")
                        try:  # if = hasn't been read, index 1 doesn't exist
                            b = (a[1].split(" "))
                            try:
                                # check if float data is sent, if string it is data type probing
                                value = float(b[0])
                            except Exception as ex:
                                value = -3
                        except Exception as ex:
                            value = -99

                    elif(line[-1].startswith("Echo")):  # DDOS
                        value = -2

                    elif (line[-1].startswith("Who")):  # SCAN
                        ethSrc = line[3]
                        timeStamp = int(line[1])
                        if ethSrc in scanDict:  # check if eth src in scan dict
                            # if yes, check if time diff is greater than 2 sec
                            if timeStamp - scanDict[ethSrc][0] > 2000000000 and scanDict[ethSrc][1] > 150:
                                value = -4  # scan attack detected
                                # update timestamp and frequency
                                scanDict[ethSrc] = [timeStamp, 0]
                            else:  # if diff less than 2 sec
                                scanDict[ethSrc][1] += 1  # update frequency
                        else:  # eth src not in scanDict
                            value = -99  # pass - reduntant detection
                            # create dict record for eth src with time stamp, frequency as value
                            scanDict[ethSrc] = [timeStamp, 0]

                    elif "duplicate " in line[-1]:  # MITM
                        value = -5
                    else:
                        value = -99
                    line[-1] = value

                    # ------------------------------------------------------------------------ PREDICTION

                    # ip_df = pd.DataFrame([line[1:]])
                    ip_df = pd.DataFrame([line[1:]])
                    # print(ip_df)
                    prediction = rf_model.predict(ip_df)[0]

                    # await self.send(json.dumps({ "value": int(prediction)}))
                    # print(prediction)
                    returnLog = returnLog.split('$')
                    text_data=json.dumps({
                        'value': int(prediction),
                        'attack_type': attack_type[prediction],
                        'frame_number': returnLog[0],
                        'frame_time': returnLog[1],
                        'frame_len': returnLog[2],
                        'eth_src': returnLog[3],
                        'eth_dst': returnLog[4],
                        'ip_src': returnLog[5],
                        'ip_dst': returnLog[6],
                        'ip_proto': returnLog[7],
                        'ip_len': returnLog[8],
                        'tcp_len': returnLog[9],
                        'tcp_srcport': returnLog[10],
                        'tcp_dstport': returnLog[11],
                        '_ws_col_Info': returnLog[12],
                    });
                    # await self.send(json.dumps({ "value": int(prediction)}))
                    await self.send(text_data)
                    await sleep(0.13)
                    # print(prediction)
                    # print(attack_type[prediction])

                    # append a row of value and prediction to the resultfile.csv - used for classification report
                    # csv_writer.writerow([value_to_label.get(value, 0), prediction])

                    ## if prediction != 0:
                        ## # print('attack: ' + str(prediction))
                        ## # still a string to this point
                        ## returnLog = returnLog.split('$')
                        ##
                        ## # check if attack is being repeated for same mac source and dest
                        ## if not (prev_mac_source == returnLog[3] and prev_mac_dest == returnLog[4] and prev_prediction == prediction):
                            ## await self.send(text_data=json.dumps({
                                ## 'attack_type': attack_type[prediction],
                                ## 'frame_number': returnLog[0],
                                ## 'frame_time': returnLog[1],
                                ## 'frame_len': returnLog[2],
                                ## 'eth_src': returnLog[3],
                                ## 'eth_dst': returnLog[4],
                                ## 'ip_src': returnLog[5],
                                ## 'ip_dst': returnLog[6],
                                ## 'ip_proto': returnLog[7],
                                ## 'ip_len': returnLog[8],
                                ## 'tcp_len': returnLog[9],
                                ## 'tcp_srcport': returnLog[10],
                                ## 'tcp_dstport': returnLog[11],
                                ## '_ws_col_Info': returnLog[12],
                            ## }));
                            ## # await self.send({ 'value': text_data["attack_type"]});
                            ## # set prev values - to prevent overloading of front end
                            ## # self.send(attack_type[prediction])
                            ## # print(text_data)
                            ## # self.send(text_data)
                            ## prev_mac_source = returnLog[3]
                            ## prev_mac_dest = returnLog[4]
                            ## prev_prediction = prediction
                            ## await sleep(1)
                            ##

        ## makeItLive as in "tail -f" (+ send live.json)
        ## analyzePackets for attacks (+ send attack.json)

## TSHARK Launch Setup for my Linux ----------------------------------------
def packetCap():
    # params ---
    password='letmein'
    iface='wlan0'
    # secs=10 # add -a duration:{secs} to $cmd

    cmd = f"echo {password} | sudo -S tshark -T fields -e frame.number -e frame.time -e frame.len -e eth.src -e eth.dst -e ip.src -e ip.dst -e ip.proto -e ip.len -e tcp.len -e tcp.srcport -e tcp.dstport -e _ws.col.Info -E header=y -E separator=\"$\" -E quote=n -E occurrence=f > {capFile} -i {iface}"
    proc = subprocess.run([cmd], shell=True)
	# p = subprocess.run(cmd, shell=True)
    # print(proc)


# launch tshark
tshark_thread = threading.Thread(target=packetCap, name='tshark')
tshark_thread.start()
