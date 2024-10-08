# Copyright (c) Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
from SnifferAPI import Sniffer, UART
from datetime import datetime
nPackets = 0
mySniffer = None

buffer=[]
def setup():
    global mySniffer
    
    # Find connected sniffers
    ports = UART.find_sniffer()
    
    if len(ports) > 0:
        # Initialize the sniffer on the first COM port found with baudrate 1000000.
        # If you are using an old firmware version <= 2.0.0, simply remove the baudrate parameter here.
        mySniffer = Sniffer.Sniffer(portnum=ports[0], baudrate=1000000)
    
    else:
        print("No sniffers found!")
        return
    
    # Start the sniffer module. This call is mandatory.
    mySniffer.start()
    # Scan for new advertisers
    mySniffer.scan(findScanRsp = False)


last_time = 0

def loop():
    global last_time
    # Enter main loop
    nLoops = 0
    while True:
        time.sleep(0.1)
        # Get (pop) unprocessed BLE packets.
        packets = mySniffer.getPackets()
        
        processPackets(packets) # function defined below
        
        nLoops += 1

        # print diagnostics every so often
        if nLoops % 10 == 0:
            global buffer
            for i in buffer:
                PKTtime = datetime.fromtimestamp(i.time)
                print(PKTtime, i.RSSI, i.blePacket.advAddress, i.channel,[hex(num) for num in i.blePacket.payload][0:8],' '*10,  i.time - last_time)
                last_time = i.time
                #print(i.blePacket.__dict__)
                #print(i.__dict__)
            buffer = []

dict_mac={}
# Takes list of packets
def processPackets(packets):
    global buffer
    global dict_mac
    for packet in packets:
        # packet is of type Packet
        # packet.blePacket is of type BlePacket

        if packet.blePacket:
            if packet.RSSI > -40:

                key = ''.join(format(x, '02X') for x in packet.blePacket.advAddress)
                if key not in dict_mac:
                    buffer.append(packet)
                elif packet.time - dict_mac[key] > 0.012:
                    buffer.append(packet)
                dict_mac[key] = packet.time
                
        global nPackets
        # if packet.OK:
        # Counts number of packets which are not malformed.
        nPackets += 1
    
setup()
if mySniffer is not None:
    loop()
