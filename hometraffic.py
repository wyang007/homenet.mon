# Author: Wei Yang
#

import matplotlib.dates as mdates

class Traffic:
    def __init__(self, length):
        self.length = length
        self.traffic = {}

    # data should be [ t, rxbytes, txbytes, rxpkts, txpkts ]
    def push(self, data):  
        device, t, rxbytes, txbytes, rxpkts, txpkts = data
        if not self.traffic.has_key(device):
            self.traffic[device] = {"hist":[]}
        else:
            dt = t - self.traffic[device]["last"][0]
            x = [dt,
                 int((rxbytes - self.traffic[device]["last"][1]) / dt),
                 int((txbytes - self.traffic[device]["last"][2]) / dt),
                 int((rxpkts - self.traffic[device]["last"][3]) / dt),
                 int((txpkts - self.traffic[device]["last"][4]) / dt)]
            self.traffic[device]["hist"].append(x)

        self.traffic[device]["last"] = [t, rxbytes, txbytes, rxpkts, txpkts]

        while len(self.traffic[device]["hist"]) > self.length:
            t, rxbytes, txbytes, rxpkts, txpkts = self.traffic[device]["hist"].pop(0)
            self.traffic[device]["hist"][0][0] += t

    def devices(self):
        return self.traffic.keys()

    def extract(self, device, type):
        array = []
        # use max(x, 0) to prevent native numbers. This could happen when the number overflow 32bit integer
        if type == "t":
#            t0 = 0
#            for i in range(0, len(self.traffic[device]["hist"])):
#                t0 = t0 + self.traffic[device]["hist"][i][0]
#                array.append(t0)

            t0 = self.traffic[device]["last"][0]
            for i in range(len(self.traffic[device]["hist"]), 0, -1):
                x = mdates.epoch2num(t0)
                array.append(x)
                t0 -= self.traffic[device]["hist"][i-1][0]
            array.reverse()    
        elif type == "rxbytes":
            for i in range(0, len(self.traffic[device]["hist"])): 
                array.append(max(self.traffic[device]["hist"][i][1] / 1024, 0))
        elif type == "txbytes":
            for i in range(0, len(self.traffic[device]["hist"])): 
                array.append(max(self.traffic[device]["hist"][i][2] / 1024, 0))
        elif type == "rxpkts":
            for i in range(0, len(self.traffic[device]["hist"])): 
                array.append(max(self.traffic[device]["hist"][i][3], 0))
        elif type == "txpkts":
            for i in range(0, len(self.traffic[device]["hist"])): 
                array.append(max(self.traffic[device]["hist"][i][4], 0))
        return array
