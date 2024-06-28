"""
@package docstring
Import model parameters for the vehicle and race from yaml definition files.
"""
from typing import Dict
from simple_task import *
import yaml
import csv
from math import floor
import logging

class ModelImporter(SimpleTask):
    def __init__(self, name: str):
        super().__init__(name)
        self.import_parameters = True  #always import on startup

    def start(self):
        """
        Starts the operation of the subtask by importing parameters
        Confirms that we will alway have parameters to work with.
        """
        super().start()

    def update(self, exec_time: float,  global_dict: Dict, latest_packets: Dict):
        """
        Runs in a loop in the framework.
        If the user has selected to import new parameters, update those parameters
        """
        self.import_parameters = global_dict['import_new_params']

        if self.import_parameters:
            logging.info("importing params")
            vehicle_model_path =  global_dict['vehicle_model_path']
            race_model_path =   global_dict['race_model_path']
            global_dict['vehicle_model'] = self.create_vehicle_param_dict(vehicle_model_path) 
            global_dict['race_model'] = self.create_race_param_dict(race_model_path)
            global_dict['motor_eff_LUT'] = self.create_motor_LUT_dict(global_dict['vehicle_model'])

            self.import_parameters = False
            global_dict['import_new_params'] = False

        self.last_update = exec_time

    def create_vehicle_param_dict(self, vehcile_model_path: str):
        """
        create dictionary from vehicle yaml file
        @param vehicle_model_path path to the yaml file
        """
        vehicle_model = dict()
        with open(vehcile_model_path, 'r') as file:
            temp = yaml.safe_load(file)
            for key, value in temp.items():
                vehicle_model[key] = value
        
        return vehicle_model

    def create_race_param_dict(self, race_model_path: str):
        """
        create dictionary from race yaml file
        @param race_model_path path to the yaml file
        """
        race_model = dict()
        with open(race_model_path, 'r') as file:
            temp = yaml.safe_load(file)
            for key, value in temp.items():
                race_model[key] = value
        
        return race_model

    def create_motor_LUT_dict(self, vehicle_model: Dict):
        """
        Create LookUp Table for Motor Efficiency
        Dict with format 
            key: (<x_value>,<y_value>)
            value: efficiency
        """
        efficiency_path = vehicle_model['Vehicle']['motor_efficiency']['map']['eff_path']
        x_axis_path = vehicle_model['Vehicle']['motor_efficiency']['map']['x_scale_path']
        y_axis_path = vehicle_model['Vehicle']['motor_efficiency']['map']['y_scale_path']
        efficiency = list()
        x_axis = list()
        y_axis = list()
        motor_eff_LUT = dict()

        with open(efficiency_path, 'r') as eff:
            efficiency = list(csv.reader(eff))
        
        with open(x_axis_path, 'r') as x:
            x_axis = list(csv.reader(x))

        with open(y_axis_path, 'r') as y:
            y_axis = list(csv.reader(y)) 

        for x in range(0, len(efficiency)):
            for y in range(0, len(efficiency[0])):
                motor_eff_LUT[(floor(float(x_axis[x][0])), floor(float(y_axis[0][y])))] = float(efficiency[x][y])
        #json won't accept tuples as keys. can use ast.literal_eval to convert back
        return {str(k): v for k, v in motor_eff_LUT.items()}