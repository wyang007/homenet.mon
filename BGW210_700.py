# Author: Wei Yang
#

import os, time

class BGW210_700:
    def __init__(self, ip, manual_device_list = {}):
        self.devip = ip
        self.devices = {}
        self.manual_device_list = manual_device_list
        self.devlistcmd = "curl -s http://%s/cgi-bin/devices.ha" % self.devip
        self.wanquerycmd = "curl -s http://%s/cgi-bin/broadbandstatistics.ha" % self.devip
        self.lanquerycmd = "curl --stderr /dev/null -s http://%s/cgi-bin/lanstatistics.ha" % self.devip

    def make_device_list(self):
        p = os.popen(self.devlistcmd)
        while 1:
            line = p.readline()
            if not line:
                break
            if line.find("MAC Address") > 0:
                macaddr = p.readline()[:-1]
                p.readline()
                p.readline()
                ipaddr = p.readline()[:-1]
                name = p.readline().replace(" ","").replace("/","")[:-1]
                if name.find("unknown") == 0:
                    devname = ipaddr
                else:
                    devname = name
                self.devices[macaddr] = devname
        p.close()
    
    def query_device_name(self, macaddr):
        if self.manual_device_list.has_key(macaddr):
            return self.manual_device_list[macaddr]
        if macaddr.find("lan") == 0:
            return macaddr
        if self.devices.has_key(macaddr):
            return self.devices[macaddr]
        else:
            self.make_device_list()
            if self.devices.has_key(macaddr):
                return self.devices[macaddr]
            else:
                return macaddr
    
    def wancollector(self, traffic):
        t = int(time.time())
        p = os.popen(self.wanquerycmd)
        wanipv4sector = 0
        while 1:
            line = p.readline()
            if not line:
                break
            elif (line.find("IPv4 Statistics") > 0):
                wanipv4sector = 1
            elif (line.find("IPv6 Statistics") > 0):
                wanipv4sector = 0
    
            if wanipv4sector == 0:
                continue 
    
            if (line.find("Receive Packets") > 0):
                line = p.readline()
                rxpkts = int(line.split(">")[1].split("<")[0])
            elif (line.find("Transmit Packets") > 0):
                line = p.readline()
                txpkts = int(line.split(">")[1].split("<")[0])
            elif (line.find("Receive Bytes") > 0):
                line = p.readline()
                rxbytes = int(line.split(">")[1].split("<")[0])
            elif (line.find("Transmit Bytes")  > 0):
                line = p.readline()
                txbytes = int(line.split(">")[1].split("<")[0])
        p.close()
        traffic.push(["wan", t, rxbytes, txbytes, rxpkts, txpkts ])
    
    def lancollector(self, traffic):
        t = int(time.time())
        p = os.popen(self.lanquerycmd)
        wifisector = 0
        lansector = 0
        while 1:
            line = p.readline()
            if not line:
                break
            elif line.find("Wi-Fi Client Connection Statistics") > 0:
                wifisector = 1
                lansector = 0
                continue
            elif line.find(">LAN Ethernet Statistics<") > 0:
                wifisector = 0
                lansector = 1
                lantrafficstatistics = {"rxbytes":[], "txbytes":[], "rxpkts":[], "txpkts":[]}
                continue
            elif line.find('<div id="help">') > 0:
                break
    
            if wifisector:
                if line.find('<tr class="a"><td scope="row" class="heading">') == 0:
                    macaddr = p.readline()[:-1]
                    for i in range(0, 9):
                        line = p.readline()
                    rxpkts = int(p.readline().replace(" ","").split("<")[0])
    
                    txpkts = int(p.readline().replace(" ","").split("<")[0])
    
                    rxbytes = int(p.readline().replace(" ","").split("<")[0])
    
                    txbytes = int(p.readline().replace(" ","").split("<")[0])
                    traffic.push([macaddr, t, rxbytes, txbytes, rxpkts, txpkts ])
    
            if lansector:
                if line.find('<tr><td class="col1" scope="row">Transmit Packets</td>') > 0:
                    lantrafficstatistics["rxpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                elif line.find('<tr><td class="col1" scope="row">Transmit Bytes</td>') > 0:
                    lantrafficstatistics["rxbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["rxbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                elif line.find('<tr><td class="col1" scope="row">Receive Packets</td>') > 0:
                    lantrafficstatistics["txpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txpkts"].append(int(p.readline().split(">")[1].split("<")[0]))
                elif line.find('<tr><td class="col1" scope="row">Receive Bytes</td>') > 0:
                    lantrafficstatistics["txbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    lantrafficstatistics["txbytes"].append(int(p.readline().split(">")[1].split("<")[0]))
                    ports = ["lan1", "lan2", "lan3", "lan4"]
    
                    for i in range(0, len(ports)):
                        lanport = ports[i]
                        rxpkts = lantrafficstatistics["rxpkts"][i]
                        txpkts = lantrafficstatistics["txpkts"][i]
                        rxbytes = lantrafficstatistics["rxbytes"][i]
                        txbytes = lantrafficstatistics["txbytes"][i]
                        traffic.push([lanport, t, rxbytes, txbytes, rxpkts, txpkts ])
        p.close()
    
     
