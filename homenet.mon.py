# Author: Wei Yang
#

import sys, os, time, datetime
# if running on a Mac, do this one time step
# cd ~/.matplotlib
# fc-list # this will take severial minutes.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from hometraffic import Traffic
from BGW210_700 import BGW210_700

nhist = 60
sleepTime = 10

myBGW210_700_ip="192.168.1.1"

def willplot(array, min):
    for i in range(0, len(array)):
        if array[i] > min:
            return True
    return False

traffic = Traffic(nhist)
myrouter = BGW210_700(myBGW210_700_ip)

def Init(traffic, myrouter):
    myrouter.wancollector(traffic)
    myrouter.lancollector(traffic)

t = int(time.time())
Init(traffic, myrouter)
t1 = int(time.time())
time.sleep(max(t + sleepTime - t1, 0))

fig, axs = plt.subplots(2, 1, figsize=(15, 6), sharex=True)
fig.set_tight_layout(True)

while 1:
    t = int(time.time())

    myrouter.wancollector(traffic)
    myrouter.lancollector(traffic)

    axs[0].clear()
    axs[1].clear()
    axs[0].set_ylabel("K Bytes / s", fontsize=14)
    axs[1].set_ylabel("K Bytes / s", fontsize=14)
    for dev in traffic.devices():
        tArray = traffic.extract(dev, "t")
        n = len(tArray)
        dArray = traffic.extract(dev, "rxbytes") 
        if dev == "wan":
            #axs[0].set_xlim(left=sleepTime, right=int((tArray[n-1]+sleepTime*nhist*.15)))
            #axs[0].set_xlim(left=tArray[0], right=int((tArray[n-1]+sleepTime*nhist*.15)))
            axs[0].set_xlim(left=tArray[0], 
                            right=mdates.epoch2num(mdates.num2epoch(tArray[n-1]) + int(sleepTime*nhist*.15)))

            axs[0].set_title("Receive (RX)", fontsize=14, fontweight='bold')
            axs[0].plot(tArray, dArray, label=dev, linewidth=3)
        elif willplot(dArray, 25):
            axs[0].plot(tArray, dArray, label=myrouter.query_device_name(dev), linewidth=1)
        dArray = traffic.extract(dev, "txbytes")
        if dev == "wan":
            axs[1].set_title("Transmit (TX)", fontsize=14, fontweight='bold')
            axs[1].plot(tArray, dArray, label=dev, linewidth=3)
        elif willplot(dArray, 25):
            axs[1].plot(tArray, dArray, label=myrouter.query_device_name(dev), linewidth=1)

    axs[0].legend(loc=1)
    axs[1].legend(loc=1)
    axs[0].xaxis.set_major_formatter( mdates.DateFormatter('%M:%S') )
    fig.autofmt_xdate()
    plt.pause(0.05)
    #plt.show()

    t1 = int(time.time())
    time.sleep(max(t + sleepTime - t1, 0))
