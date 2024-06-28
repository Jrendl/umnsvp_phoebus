from hard_task import *
import time
import logging

class ExampleHardTask(HardTask):

    def update(self, exec_time: float):
        logging.info("Hey from this example")
        time.sleep(.2)

        return super().update(exec_time)