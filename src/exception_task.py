from simple_task import * 

class ExceptionTask(SimpleTask):
    def update(self, exec_time: float, global_dict: Dict, latest_packets: Dict):

        raise Exception("This is a test")

        return super().update(exec_time, global_dict, latest_packets)