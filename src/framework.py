"""@package doctring
Task management for strategy software
- takes care of scheduling and initialization of hard and simple tasks
- records runtime of simple tasks and reports when they don't meet timing
- catches any exceptions thrown by simple tasks, notifies the user, the continues operation
- Spawns sub-processes for all hard tasks using Python MultiProcessing 
- restarts hard tasks if they are to fail

"""

from task import *
from simple_task import *
from hard_task import *
from model_import import *
from exception_task import *
from example_hard_task import *
from xbee_task import *
from SD_card_parser import *
import time
import sys
import argparse
import requests
import copy
from datetime import datetime
import logging

# The total time allowed for a simple task's operation in seconds
TASK_TIME_ALLOWED = .010
# The total time allowed for ALL simple tasks together 
TOTAL_TIME_ALLOWED = .25

server_ip: str
packet_path: str
latest_packets = {}
global_dict = {}
global_dict_unchanged = {}

#defined in main()
simple_task_list = []

#defined in main()
hard_task_list = []


def process_init():
    """
    Call the start functions for all tasks
    For Hard tasks, This will set the process up as a sub-process
    """
    for task in simple_task_list:
        task.start()
    for task in hard_task_list:
        task.start()

def pull_new_info():
    """
    Pull down new information from the Flask server, allowing simple tasks to have local access to these variables
    """
    global latest_packets
    global global_dict
    global global_dict_unchanged

    # latest_packets = requests.get(f"http://{server_ip}/telemetry/latest").json()
    global_dict = requests.get(f"http://{server_ip}/globals/").json()
    global_dict_unchanged = copy.deepcopy(global_dict)

    for task in simple_task_list:
        if global_dict['active_task'] == task.name:
            task.active = True
        else:
            task.active = False

def push_updates():
    """
    Push any updates created by the simple tasks
    Genereally, if something has changed from what it was at the beginning of the loop, push that variable
    """
    for key, value in global_dict.items():
        if not key in global_dict_unchanged.keys() or value != global_dict_unchanged[key]:
            requests.post(f"http://{server_ip}/globals/{key}", json = value)

def babysit():
    """
    Monitor hard tasks and restart them if they have killed
    """
    for task in hard_task_list:
        #restart dead tasks
        if not task.is_alive():
            logging.error(f"restarting {task.name} after kill")
            task = task.reset()
            task.start()

def run_update(task: SimpleTask, t: float):
    """
    Run the update function of a simple Task 
    Catch exceptions and relay them to the user 
    Record the Time it takes for the update function to run and report it if it doesn't meet timing
    @param task the Simple Task object for which we would like to run the update function
    @param the time that this iteration of the loop began
    """
    global global_dict
    global latest_packets

    exec_dur = time.time()
    try: 
        task.update(t, global_dict, latest_packets)
    except Exception as err:
        # if it threw an exception, give the user the information but don't kill
        # this will allow other tasks to continue uninterrupted
        logging.error(f"{task.name} threw {err=}, {type(err)=} while updating.")
    exec_dur = time.time() - exec_dur

    # if we didn't error out, we want to make sure we're executing the tasks in the alotted timeframe
    # let the developer know if their task is too long
    if exec_dur >= TASK_TIME_ALLOWED:
            logging.warning(f"{task.name} Exceeds the alotted timeframe of {TASK_TIME_ALLOWED*1000} ms with a runtime of {exec_dur * 1000} ms")
        

def update(t: float):
    """
    Update processes states depending on active state of task
    Sleep for any time that isn't consumed by the tasks in simple_task_list
    """
    
    for task in simple_task_list:

        # catch errors that are thrown by simple Tasks
        if task.active and t - task.last_update >= .25:
            #update ~ every 250 ms
            run_update(task, t)
                
        elif t - task.last_update >= .5:
            #update ~ every 500 ms
            run_update(task, t)

        
    total_exec_duration = time.time() - t

    # Check on the total execution duration of the tasks
    if total_exec_duration  < TOTAL_TIME_ALLOWED:
        # If it's less than Time allowed, this is good. Sleep until the next excecution
        time.sleep(TOTAL_TIME_ALLOWED-total_exec_duration)
    elif total_exec_duration == TOTAL_TIME_ALLOWED:
        # We're at capacity. Maybe take a look at improving the situation
        logging.warning("Simple tasks took 250 ms to execute. Consider switching some to hardTasks.")
    else:
        # Tasks took too long. We need to cut down on what their doing or make some of them hardTasks
        logging.warning("Simple tasks took longer than the aloted timeframe. Please move heavier tasks to hardTasks.")
    

def main():
    #format current datetime for logfile
    dt = datetime.now()
    dt_string = dt.strftime("%d-%m-%Y_%H-%M-%S")


    #parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_ip", help= "Specify the IP and the Port for the Flask server")
    parser.add_argument("--packets", help = "Relative path from tools/strategy_software to the packet definition YAMLS", default = '../../src/cangen/old/packets/')
    parser.add_argument("-l", "--xbee_log",  help = "Relative path from tools/strategy_software for the logfile", default = f'./logs/{dt_string}.txt')
    parser.add_argument("-s", "--cache_size", help = "The size of the packet cache in umnsvp_xbee", default = '100')
    parser.add_argument("-t", "--cache_time" , help = "Time limit for caching in umnsvp_xbee. This will effect program CPU usage.", default = '0.25')
    parser.add_argument("--com_port", help="Com port for the Xbee", default="COM4")
    parser.add_argument("-x", "--xbee", help="Whether or not the program has an Xbee attached", action='store_false')    
    args = parser.parse_args()

    #initialize the server ip
    global server_ip
    server_ip = args.server_ip

    #initialize the path to the packet definitions
    global packet_path
    packet_path = args.packets


    #initilize the simple tasks here so that it's done in the same place as the hard tasks
    global simple_task_list
    simple_task_list = [ModelImporter("model_import")]

    #initilize the hard tasks here because server_ip needs to be populated
    global hard_task_list
    
    if args.xbee:
        hard_task_list.append(XbeeTask("xbee", server_ip, packet_path, args.com_port, args.xbee_log, int(args.cache_size), float(args.cache_time)))

    hard_task_list += [sdCardParser("sd card parser", server_ip, packet_path), 
                        ExampleHardTask("example", repeated=True, period= 1, server= server_ip)]

    #This is a placeholder for now. Activity status will change once the GUI is implemented
    simple_task_list[0].active = True
    #TODO: I don't like doing this. The GUI should be the only one to control this variable.
    # Please advise on a better approach
    requests.post(f"http://{server_ip}/globals/active_task", json=simple_task_list[0].name)

    process_init()
    while True:
        pull_new_info()
        update(time.time())    
        push_updates()
        babysit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        for task in hard_task_list:
            task.terminate()