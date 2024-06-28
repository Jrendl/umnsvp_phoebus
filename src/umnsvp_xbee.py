"""@package docstring
Xbee interface program 
* Pulls data from serial port
* Caches data in a parsed format
* POSTs data after a set time or number of packets
"""
import os
import sys

import urllib.parse
import json
import time
from pathlib import Path
from typing import Dict
import requests
import time
import logging
sys.path.append(str(Path("../can_packet_parser/")))

from interface_digi_xbee import interface_digi_xbee
from can_packet_codec import XBeeCANPacketCodec
from scrappy import yamls_to_packets
from packet import Packet

#Cache of packets
packet_cache = list()
#Record the time of the last posted packet
last_post = time.time()

class Logger:
    """
    Class to handle logging packets to a file.
    """

    def __init__(self, filename: str):
        """Constructor for Logger class
            @param filename path to log file
        """
        self.log_file = open(filename, 'a')

    def send(self, packet):
        """Method to write to logfile
            @param packet the packet to log"""
        out = '%.3f ' % time.time() # write time to 3 decimal places and leave a space
        out += '%03X' % packet.id # write the id in hex using 3 digits
        for data in packet.data:
            out += '%02X' % data # write the data in 
        out+= '\n'
        self.log_file.write(out)

    def close(self):
        """Close the logfile"""
        self.log_file.close()





def build_xbee_handler(packets: Dict, server_IP: str, logger: Logger, packet_cache_size: int, packet_cache_time: float):
    """Build function for the xbee handler which will be run every time a packet is recieved over Xbee
        @param packets packet definitions from Scrappy
        @param server_IP Flask server IP and port as a string
        @param logger logger class for log file
        @param packet_cache_size size at which to cap the packet cache
        @param packet_cache_time time interval at which to post packets to server
    """
    def xbee_handler(packet: Packet):
        """Handler function to be called every time a packet is recieved over Xbee
            @param packet formatted Packet class of the packet that was recieved
        """
        global last_post
        can_packet_t = packets.get(packet.id, None)

        logger.send(packet)
 
        while len(packet.data) < 8:
            packet.data.append(0)
        packet.data = bytes(packet.data)

        if can_packet_t is not None:
            parsed_packet = can_packet_t.parse_packet_to_json(
                packet.id, packet.data
            )
            #This triple for loop is necessary because of the way Scrappy parses the packet
            #Although this seems like a O(n^3) operation, it is actually O(1) 
            # since, as I understand it, these lists will all be bounded by a constant
            for board in parsed_packet:
                for message in parsed_packet[board]:
                    for idx in parsed_packet[board][message]:
                        packet_name: str
                        if can_packet_t.repeat > 1:
                            packet_name = f"{can_packet_t.name[packet.id-can_packet_t.ids[0]]}_{can_packet_t.offset*(packet.id-can_packet_t.ids[0])}"
                        else:
                            packet_name = f"{can_packet_t.name[0]}"  
                        p = {   "ID": packet.id,
                                "packet_name": packet_name,
                                "board": board,
                                "data": parsed_packet[board][message]
                        }
                        packet_cache.append(p)
                        if (len(packet_cache) >= packet_cache_size) or (time.time() - last_post >= packet_cache_time ):
                            last_post = time.time()
                            requests.post(f"http://{server_IP}/telemetry/", json = [p])
                            packet_cache.clear()
        else:
            string = "WARNING UNKNOWN PACKET: {0}  {1:8X}   [{2}]  {3}".format(
                'xbee',
                packet.id,
                len(packet.data),
                " ".join(["{0:02X}".format(b) for b in packet.data]),
            )
            logging.info(string)

    return xbee_handler


def main(*args):
    # We will use port 8000, this can change if needed
    server_IP = args[1]

    # Dictionary of packets found in the provided directory
    packets = yamls_to_packets(args[2])

    # Create a Logger object to log to the provided file
    logger = Logger(args[3])

    com_port = args[0]

    interface = interface_digi_xbee(com_port, build_xbee_handler(packets, server_IP, logger, int(args[4]), float(args[5])), codec=XBeeCANPacketCodec())

    interface.start()
    interface.join()

    try:
        # start the thread
        # logging.info(f'Telemetry server available at http://{server_IP}/telemetry/', flush = True)

        while True:
            pass

    except KeyboardInterrupt:
        interface.stop()
        logger.close()
    pass
    

if __name__ == "__main__":
    # logging.info (tuple(sys.argv[1:]), flush = True)
    main(*tuple(sys.argv[1:]))
