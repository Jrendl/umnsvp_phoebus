"""
@package docstring
Task to export logs from the SD card to a readible format.
"""
from hard_task import *
from datetime import datetime
import requests
import sys
import os
import glob
from pathlib import Path
from typing import Dict
import csv
import logging
sys.path.append(str(Path('../can_packet_parser')))
from scrappy import yamls_to_packets
from parse_can_log import load_data_from_telem_sd_log

class sdCardParser(HardTask):
    def __init__(self, name: str, server: str, packet_path: str):
        """
        Constructor for sdCardParser class
        @param name the name of the task
        @param server ip address and port of the flask server
        @param packet_path path to yaml definitions of packets
        """
        self.packet_path = packet_path
        self.packets = yamls_to_packets(packet_path)
        self.parse_log = False
        #initialize as a repeated Hardtask with a period of 1 second
        super().__init__(name, server, repeated=True, period=1.0)

    def update(self, exec_time: float):
        """
        Update function for the sdCardParser class
        If it is signaled to process a new set of data it calls ``do_parse_can_log``
        @param exec_time
        """
        self.parse_log = requests.get(f"http://{self.server}/globals/parse_sd_card").json()
        if self.parse_log:
            sd_card_path = requests.get(f"http://{self.server}/globals/sd_card_path").json()
            logging.info('parsing can log')
            self.do_parse_can_log(sd_card_path)
            self.parse_log = False
            requests.post(f"http://{self.server}/globals/parse_sd_card", json=self.parse_log)
        super().update(exec_time)
    
    def do_parse_can_log(self, sd_card_path: str):
        """
        Function that is called from update when new data is available.
        * append all csvs into one
        * output a formatted folder under the current UTC dateTime which contains 
            * a folder for each board
            * a csv per packet (sorted into the corresponding board) 
            * csvs are formatted as timestamp and then data fields
        @param sd_card_path path to the folder containing unformatted csv files from sd card
        """
        out_path = self.path_name()
        sd_card_path = Path(sd_card_path)
        out_dict = self.create_output_dict()

        # concatenate all log files from the SD card to a single csv
        concat_path = Path(f'./logs/{out_path}.csv')
        self.concatenate_logs(Path(sd_card_path), concat_path.absolute())

        # load the data from that single csv file
        packet_list = load_data_from_telem_sd_log(str(concat_path))

        # iterate through the tuples created by ``load_data_from_telem_sd_log()``
        # packet_tuple in format <timestamp, can_id, data>
        for packet_tuple in packet_list:
            # retrieve the packet defintion based on the id
            can_packet_t = self.packets.get(packet_tuple[1], None)
            if can_packet_t is not None:
                # parse the packet to json format using scrappy
                parsed_packet = can_packet_t.parse_packet_to_json(packet_tuple[1], packet_tuple[2])

                #traverse structure of the parsed can packet
                for board in parsed_packet:
                    for message in parsed_packet[board]:
                        for idx in parsed_packet[board][message]:
                            #format a name for the packet
                            packet_name: str
                            if can_packet_t.repeat > 1:
                                # if there's mutliple repititions of the packet
                                # format it as packet_name_offset
                                packet_name = f"{can_packet_t.name[packet_tuple[1]-can_packet_t.ids[0]]}_{can_packet_t.offset*(packet_tuple[1]-can_packet_t.ids[0])}"
                            else:
                                # if there's only one repitition
                                # make sure you're grabbing the correct spot in the name array!
                                # this is relevant for packets defined like the board_id packets
                                packet_name = f"{can_packet_t.name[packet_tuple[1] - can_packet_t.ids[0]]}"
                            # start by adding the timestamp to the list
                            packet_out = [str(packet_tuple[0])]
                            for data in parsed_packet[board][message][idx].values():
                                # extract all data fields and add them to the list
                                packet_out.append(str(data))
                            #add the list to our output dictionary!
                            out_dict[board][packet_name].append(packet_out)
        
        
        self.output(Path(f'./logs/{out_path}_sd_log/'), out_dict)


    
    def output(self, output_dir: Path, out_dict: Dict):
        """
        Format and output to the log directory
        @param output_dir the path to output to
        @param out_dict the parsed data formatted in a dict
        """
        if not output_dir.exists():
            output_dir.mkdir()
        for board in out_dict.keys():
            board_dir = output_dir.joinpath(board)
            if not board_dir.exists():
                board_dir.mkdir()
            for packet_name in out_dict[board].keys():
                cwd = os.getcwd()
                os.chdir(str(board_dir))
                with open(f"{packet_name}.csv", 'a') as f:
                    writer = csv.writer(f, dialect='excel')
                    for line in out_dict[board][packet_name]:
                        writer.writerow(line)
                os.chdir(cwd)


    def concatenate_logs(self, sd_card_path: Path, outfile: Path):
        """
        Rewrite of Maxim's ``sd_car_parsing_tools`` to use the Path object and be runnable from this script
        @param sd_card_path the raw sd card data
        @param outfile where to write the concatenated logs to
        """
        cwd = os.getcwd()
        os.chdir(str(sd_card_path))
        all_filenames = [i for i in glob.glob('*.{}'.format('csv'))]
        #combine all files in the list
        
        with open(str(outfile),"w+") as fout:
            for f in all_filenames:
                with open(f, 'r') as f:
                    for line in f:
                        fout.write(line)
                logging.info(f"Finished copying from file: {f.name}")
        logging.info(f"Combined CSV files to output file: {str(outfile)}.csv")
        os.chdir(cwd)

    def create_output_dict(self):
        """
        This does the parsing of the data from the concatenated logs
        returns a hierarchical dict board->packet->list of data
        """
        out_dict = dict()

        for filename in os.listdir(self.packet_path):
            out_dict[filename.partition('.')[0]] = dict()
            
        i = 0
        for packet_id, packet in self.packets.items():
            packet_name :str
            if packet.repeat > 1:
                packet_name = f"{packet.name[packet_id-packet.ids[0]]}_{packet.offset*(packet_id-packet.ids[0])}"
            else:
                packet_name = f"{packet.name[packet_id - packet.ids[0]]}"
            out_dict[packet.board][packet_name] = list()
            header = ['timestamp']
            for field in packet.data:
                    if field['type'] != 'bitfield':
                        header.append(field['name'])
                    else:
                        for bit in field['bits']:
                            header.append(f"{field['name']}:{bit['name']}")
            out_dict[packet.board][packet_name].append(header)
        return out_dict

    def path_name(self):
        response = requests.get(f"http://{self.server}/globals/log_output_path")
        
        if response.ok:
            return response.json()
        else:
            # format a datetime string to be our folder name
            dt = datetime.utcnow()
            # Windows doesn't like us enough to allow for : in filepaths
            dt_string = dt.isoformat(timespec='seconds').replace(':', '-')
            return dt_string


        
        

        
        
        

        

