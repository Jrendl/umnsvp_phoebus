"""@package docstring
Main executable program for Phoebus
Spawns sub processes for each of the parts of the software. 
Options:
* -ip           Specify the IP address for the Flask server
* --port        Specify the Port for the Flask Server
* --packets     Relative path from tools/strategy_software to the packet definition YAMLS
* --log_file    Relative path from tools/strategy_software for the logfile
* --cache_size  The size of the packet cache in umnsvp_xbee
* --cache_time  Time limit for caching in umnsvp_xbee. This will effect program CPU usage.
* --race        File path to the Race definition file.
* --vehicle     File path to the vehicle definition file.
* --no-xbee     Include when no xbee is attached
* --xbee-port   Mannually set the port that the xbee is on
"""

import sys 
import os
import time
import webbrowser
from pathlib import Path
import subprocess
import argparse
import requests
from datetime import datetime
sys.path.append(str(Path('src/')))
sys.path.append(str(Path('../can_packet_parser/')))
from xbeefind import serial_ports
from server import create_app

if __name__ == '__main__':
    #format current datetime for logfile
    dt = datetime.now()
    dt_string = dt.strftime("%d-%m-%Y_%H-%M-%S")

    #read optional arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help = "Specify the IP address for the Flask server", default = "127.0.0.1")
    parser.add_argument("-p", "--port", help = "Specify the Port for the Flask Server", default = "5000")
    parser.add_argument("--packets", help = "Relative path from tools/strategy_software to the packet definition YAMLS", default = '../../src/cangen/packets/')
    parser.add_argument("-l", "--log_file",  help = "Relative path from tools/strategy_software for the logfile", default = f'./logs/{dt_string}.txt')
    parser.add_argument("-s", "--cache_size", help = "The size of the packet cache in umnsvp_xbee", default = '100')
    parser.add_argument("-t", "--cache_time" , help = "Time limit for caching in umnsvp_xbee. This will effect program CPU usage.", default = '0.25')
    parser.add_argument("-r", "--race", help = "File path to the Race definition file.", default = 'data/WSC_2023.yaml')
    parser.add_argument("-v", "--vehicle", help = "File path to the vehicle definition file.", default = 'data/G1.yaml')
    parser.add_argument("-nx", "--no-xbee", help="Include when no xbee is attached", action='store_false')
    parser.add_argument("-x", "--xbee-port", help="Manually set the port that the xbee is on", default = None)
    args = parser.parse_args()


    #find port for xbee
    if not args.xbee:
        coms = serial_ports()[0]
    else:
        coms = args.xbee




    #spawn subprocesses for different parts of Phoebus
    flask_server = subprocess.Popen(f'flask --app server run -h {args.ip} -p {args.port}', shell=True)

    time.sleep(0.5)
    
    requests.post(f"http://{args.ip}:{args.port}/globals/vehicle_model_path", json = str(args.vehicle))
    requests.post(f"http://{args.ip}:{args.port}/globals/race_model_path", json = str(args.race))
    requests.post(f"http://{args.ip}:{args.port}/globals/parse_sd_card", json = False)
    requests.post(f"http://{args.ip}:{args.port}/globals/import_new_params", json = True)

    if args.xbee:
        framework_exec = subprocess.Popen(f'python src/framework.py --server_ip {args.ip}:{args.port} --packets {args.packets} --com_port {coms} --xbee_log {args.log_file} --cache_size {args.cache_size} --cache_time {args.cache_time}', shell=True) 
    else: 
        framework_exec = subprocess.Popen(f'python src/framework.py --server_ip {args.ip}:{args.port} --packets {args.packets} -x', shell=True) 
    
    with open(Path("./gui/.env"), 'w') as gui_env:
        gui_env.write( f"""REACT_APP_GLOBALS = http://{args.ip}:{args.port}/globals
        REACT_APP_TELEMETRY = http://{args.ip}:{args.port}/telemetry""")
    
    
    with open(Path("./openmct/.env"), 'w') as openmct_env:
        openmct_env.write(f"""VUE_APP_TELEM = http://{args.ip}:{args.port}/telemetry
        VUE_APP_TELEM_PORT = {args.port}""")


    gui = subprocess.Popen('npm start --prefix ./gui', shell=True)
    openMCT = subprocess.Popen('npm --prefix ./openmct run serve', shell=True)


    webbrowser.open('http://10.131.81.235:8080/', autoraise=True)   

    #allow for all processes to be killed with ctrl+C
    try:
        while True: 
            pass

    except KeyboardInterrupt:
        flask_server.terminate()
        if sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
            os.popen("killall flask")
        framework_exec.terminate()
        gui.terminate()
        openMCT.terminate()

