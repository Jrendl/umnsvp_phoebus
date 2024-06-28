"""@package docstring
HardTask class for the G1 Strategy Software
"""
from multiprocessing import Process
from task import Task
import time
import logging
from abc import ABC, abstractmethod

class HardTask(Process, Task, ABC):
    def __init__(self, name: str, server: str, repeated = False, period = 0.0):
        """
        Constructor for the HardTask Class
        Initializes itself as an extension of the Task class as well as a python Process
        @param name the name of the task
        @param server ip adress of the flask server 
        @param repeated boolean flag to indicate whether the task should be ran at a repeated interval
            false by default
        @param period float value that indicates the period of repetition in seconds"""
        Process.__init__(self)
        Task.__init__(self, name, server)

        self.name = name
        self.server = server
        self.repeated = repeated
        self.period = period

    def start(self):
        """
        Call the Python Process start function to set up the subprocess
        """
        return Process.start(self)

    def reset(self):
        """
        Allows for the task to be restart if it ever fails
        Creates a new instantiation of the class
        Initializes it with the same values as itself
        Returns the new object
        """
        fresh = object.__new__(HardTask)
        fresh.__init__(self.name, self.server, self.repeated, self.period)
        return fresh


    def run(self):
        """
        Override of the Process run method
        If the task is repeated, call the update function at that interval and sleep for any remaining time
            Track whether or not the task is meeting it's timing requirements
        If the task is not repeated, call the update function just once
        """
        if self.repeated and self.period != 0:
            #The task wants to be repeated and has a valid period
            while True:
                exec_dur = time.time()
                try:
                    self.update(exec_time= time.time())
                    exec_dur = time.time() - exec_dur
                    if exec_dur > 0.0:
                        time.sleep(self.period - exec_dur)
                    elif exec_dur < 0.0:
                        logging.info(f"{self.name} took {exec_dur} seconds. This is longer than it's set period of {self.period}")
                    else:
                        logging.info(f"{self.name} took exactly the length of it's period {self.period} seconds")
                except Exception as err: 
                    logging.info(f"{self.name} threw {err=}, {type(err)=} while updating.")

        elif self.repeated and self.period == 0:
            #the period is invalid
            logging.info(f"please set a period for {self.name} or turn off the \"repeated\" flag")
            self.terminate()

        else:
            #this is for a non-repeated task that persists 
            #something like the xbee task will use this
            self.update(exec_time= time.time())
    
    @abstractmethod
    def update(self, exec_time: float):
        return super().update(exec_time)
