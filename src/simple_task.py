"""@package docstring
SimpleTask class to encapsulate individual runtime tasks for the G1 Strategy software.
"""

from task import *
from typing import Dict
from abc import ABC, abstractmethod


class SimpleTask(Task, ABC):
    
    def __init__(self, name: str):
        """
        Constructor for the SimpleTask class.
        
        @param name the name of the task.
        """
        #initialize the base class without a web server
        super().__init__(name, None)
        

    @abstractmethod
    def start(self):
        """
        Initialization for internal components of the task.
        
        Meant to be overwritten by children.
        """
        pass

    @abstractmethod
    def update(self, exec_time: float,  global_dict: Dict, latest_packets: Dict):
        """Runs in a loop in the framework. How this task gets anything done.
        
        Meant to be overwritten by children.
        @param exec_time the time in seconds that the update function was called
        @param gloabls_dict dictionary provided by the framework for global variables
        must return back to update any changes
        @param latest_packets dictionary of latest packets provided by the framework

        """     

        #read inputs from website
        # self.web.get()

        """other code based on subclass"""


        self.last_update = exec_time

        



