"""@package docstring
Task class to encapsulate individual runtime tasks for the G1 Strategy software.
"""

import time
from abc import ABC, abstractmethod


class Task(ABC):
    
    def __init__(self, name: str, server: str ):
        """
        Constructor for the Task class.
        
        @param name the name of the sub-task.
        @param server the common web sever for all tasks.
        """
        self.name = name
        self.active = False
        self.server = server
        self.last_update = time.time()
        
    @abstractmethod
    def start(self):
        """
        Initialization for internal components of the task.
        
        Meant to be overwritten by children.
        """

        pass


    @abstractmethod
    def update(self, exec_time: float):
        """extended by hardTask and SimpleTask
        
        Meant to be overwritten by children.
        @param exec_time the time in seconds that the update function was called
        """     


        """other code based on subclass"""


        self.last_update = exec_time

        



