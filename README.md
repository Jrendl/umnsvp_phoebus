# Phoebus #

This is Phoebus, the strategy software originally developed during the G1 cycle.
The goal of Phoebus is to provide an extensible and modular base for development
and use for future solar cars. At the time of development, Phoebus will include a 
telemetry monitoring system and two solar race simulators, one for quick 
low-parameter simulations, and one for longer high-parameter simulations.

* All in-code paths to use ``/`` and be reletive from the ``strategy_software`` directory

* More extensive documentation can be found in [this google drive folder](https://drive.google.com/drive/folders/1tt09WwttNsl3ZCwnsZMDzpimYRiXzKOt?usp=share_link)

## Table Of Contents ## 

- [Phoebus](#Phoebus)
    - [Table Of Contents](#table-of-contents)
    - [Dependencies](#dependencies)
    - [phoebus.py](#phoebuspy)
    - [Software Framework](#software-framework)
        - [Program Outline](#program-outline)
            - [framework.py](#frameworkpy)
            - [task.py](#taskpy)
            - [hard_task.py](#hard_taskpy)
            - [simple_task.py](#simple_taskpy)
            - [model_import.py](#model_importpy)
            - [SD_card_paser.py](#sd_card_parserpy)
            - [umnsvp_xbee.py](#umnsvp_xbeepy)
            - [xbee_task.py](#xbee_taskpy)
            - [G1.yaml](#g1yaml)
            - [WSC_2023.yaml](#wsc_2023yaml)
            - [model_testing.ipynb](#model_testingipynb)
    - [Flask Server](#flask-server)
        - [Program Outline](#program-outline-1)
            - [__init__.py](#initpy)
            - [model.py](#modelpy)
            - [telemetry.py](#telemetrypy)
            - [globals.py](#globalspy)

## Dependencies ##

Phoebus depends on multiple python modules for operation and ease of 
implementation. The most basic of these requirements is a version of Python 3, 
preferably >3.10, as the program will suffer significant performance losses on 
older versions of python. Instructions for install and set-up can be found [here](https://docs.google.com/document/d/10vMGffOPt3vgJVgoksbvyXe9rgkXU-RZqBHcoCS-5Gg/edit?usp=sharing)


## Phoebus.py ##

* Main Executable program for Phoebus. Spawns sub processes for each of the parts of the software. 
* Options:
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
* To run Phoebus, navigate to ``tools/strategy_software/`` and execute ``python phoebus.py`` with the desired options

## Software Framework ##

This section of the project is meant to define the skeleton in which the rest of 
the development can occur. A single python program will act as a task scheduler 
for the rest of the submodules. It will initialize Flask server for 
communication with the telemetry hardware, GUI, and tasks, which will serve to 
abstract the connection between these parts. Each subtask of the software will
inherit from a parent class, outlining the communication between the framework 
and the subtask. This will allow for easy implementation of new features and 
improve the expandability of the program. The framework program itself will run "Simple Tasks" in a
loop architecture that will make sure tasks are run 
regularly and at frequencies depending on their status. It will initialize more 
computationally intensive tasks, known as "Hard Tasks", as Sub-processes 
using Python Multiprocessing. The most important part of this section is to provide 
the modularity and expandability that the other programs have lacked. 
With a strong skeleton, within which different features can fit, 
the likelihood that this program remains relevant increases.

### Program Outline ###

#### framework.py ####

* Main executable for the program. Initializes all subtasks and runs forever-loop updates as well as "babysits" Hard Tasks.
* Holds global dictionaries of the data in the Flask server to allow for Simple Tasks to have faster access to these components
* Performs exception catching and provides indications of performance
* ``simple_task_list``: python list of SimpleTasks to be iterated through in the init and update function.
* ``hard_task_list``: python list of HardTasks to initialized as a Process and babysat on a regular basis. 
* ``process_init()``: initialize all subtasks by calling their ``task.start()`` function. 
* ``update(t)``: consistently update different tasks based upon whether or not they're active.
 Usually, the active status of a task will be determined by whether or not it is currently displayed in the GUI,
 for now we just set the first task in ``simple_task_list`` to active. An "active" task is updated every 250 ms 
 and an unactive task is updated every 500 ms. The program then sleeps for the remainder of the time in a 250 ms block.

#### task.py ####

* Inheritable task class for all subtasks to expand upon
* ``__init__()``: base initialization for internal variables. All tasks start as inactive and set their last_update time at the current time. 
* ``start()``: placeholder for subtasks to override. Currently sends the task name to the web server.
* ``update()``: this is the function that will be called by the framework in a loop or as a process. It will be where the main operation of the task will get done. 

#### hard_task.py ####

* Inheritable HardTask class for computationally time intensive tasks
* Inherrits from python ``Process`` class and ``Task``
* Can initialize its own period or just be ran once
* ``__init__()``: initializes ``HardTask`` object as both a subclass of the ``Process`` class and the ``Task`` class
* ``start()``: call the ``start()`` function of the ``Process`` class explicitly so the start function of the ``Task`` class isn't called. 
  * This function initializes the class as a new python process and calls the ``run`` function
* ``reset()``: Allows the framework to restart this task if it ever fails. This cannot be done by simply re-calling the ``start()`` function because Python will complain
* ``run()``: Override of the ``Process.run()`` function to
  * check if a task is repeated
    * attempt to call the ``Task.update()`` function at intervals set by the ``period`` parameter in the constructor
    * throw warnings is exceptions are thrown or the task exceeds the period
  * If it's not repeated
    * Simply cally the update function which is *expected* to never exit

#### simple_task.py ####

* Inherritable ``SimpleTask`` class for quick and dirty processes in Phoebus
* ``__init__()``: call the ``Task`` constructor without a server address
* ``start()``: A place for the developer to initialize any internal components of the task
* ``update()``: Runs in a loop in the Framework. Will provide the main functionality of the task.
  * *Note*: This override of the ``update`` function passes in the information updated from the framework on this iteration

#### model_import.py ####

* The first subtask implemented. This will serve the purpose of reading the yaml files that outline the race and vehicle and importing them into useful datastructures. It can be run during the operation of the framework by setting ``import_parameters`` to ``True``. 
* ``__init()__``: adds the vehicle model, race model, motor efficiency table, and import_parameters bool to the base initializer.
* ``start()``: Simply calls ``update`` to import parameters at the beginning. 
* ``update()``: imports parameters if ``import__parameters == True``
    * Creates the dictionaries for the vehicle model, race model, and motor efficiency.
    * resets ``import_parameters = False``
* ``create_vehicle_param_dict()``: creates dictionary from vehicle yaml file with all pertinent information.
* ``create_race_param_dict()``: creates dictionary from race yaml file with all pertinent information.
* ``create_motor_LUT_dict()``: creates a dictionary for O(1) lookUp of motor efficiency values
    * key: <x_value>/<y_value>
    * value: efficiency

#### SD_card_parser.py ####
* Task to take an unparsed sd card log from a day's drive and output a formatted folder of parsed data
* Inherrits from ``HardTask`` as the parsing process takes over 2 minutes
* ``__init__``: Constructor for sdCardParser class
* ``update``:  Update function for the sdCardParser class
  * If it is signaled to process a new set of data it calls ``do_parse_can_log``
* ``do_parse_can_log``: Function that is called from update when new data is available.
  * append all csvs into one
  * output a formatted folder under the current UTC dateTime which contains 
    * a folder for each board
    * a csv per packet (sorted into the corresponding board) 
    * csvs are formatted as timestamp and then data fields
* ``output``: Format and output to the log directory
* ``concatenate_logs``: Rewrite of Maxim's ``sd_car_parsing_tools`` to use the ``Path`` object and be runnable from this script.
* ``create_output_dict``: This does the parsing of the data from the concatenated logs
  * returns a hierarchical dict board->packet->list of data

#### umnsvp_xbee.py ####

* This is treated as a library, defining useful classes and factories for the xbee task
* ``class Logger``: logger class which encapsulates the logging action of the xbee handler. Currently organizes the packet into ``<timestamp>, <ID>, <data in hex>`` and writes to a given csv file
* ``build_xbee_handler``: Factory which creates a handler function to be called by the xbee python module when a packet is recieved. 
  * This handler will 
    * Write the packet to the logger
    * Parse the data using Scrappy
    * Store the data in a list 
    * Post that list to the Flask server *if* the the list exceeds the size limit or we have passed the timeout 

#### xbee_task.py ####

* Defines ``XbeeTask`` which is an extension of the ``HardTask`` class
* ``__init__()``: Initializes the extra variables that are needed for caching time, logging, and communicating with the xbee. Calls the ``HardTask.__init__()`` to initialize itself as a non-repeating ``HardTask`` 
* ``udpate()``: initializes the Logger, packet definitions, and xbee interface and starts the interface. 


#### G1.yaml ####
* Vehicle definiton file. This format is to be copied to all other vehicles.
* Charger efficiency and array efficiency could have more detailed maps implemented later

```
Vehicle:
  name: 
  pseudonym: 
  weight:
   value: 
   unit: 
  CdA: 
  Crr: 
  motor_efficiency:
    basic: 
    map: 
      eff_path:  #relative path from strategy_software/src
      x_scale_path: 
      x_unit: 
      y_scale_path: 
      y_unit: 
    unit: 
  battery:
    num_packs: 
    cell_esr: 
      value:
      unit: 
    cells_in_series:
    cells_in_parallel:
    energy_per_cell: 
      value:
      unit: 
    cell_IV_map:
      path: 
      x_unit: 
      y_unit: 
  powertrain_efficieny: 
    value: 
    unit:
  charger_efficiency:
    value: 
    unit:
  array_efficiency:
    value:
    unit:
```

#### WSC_2023.yaml ####

* Race definition file. This format is to be copied by all other races:

```
Race:
  name: 
  length: 
    value: 
    unit: 
  base_route_distance: 
    value: 
    unit: 
  race_type: #wsc or asc
  route: 
  distane_events:
    - checkpoint:
      name: 
      distance: 
        value: 
        unit: 
      hold_duration: 
        value: 
        unit: 
      latest_arrival: 
    - stage_stop:
      name: 
      distance: 
        value: 
        unit: 
      target_arrival: 
      latest_arrival: 
  time_events:
    - start_of_day: 
      name: 
      time: 
    - end_of_day: 
      name: 
      time: 
    - start_grid_charge: 
      time: 
    - end_grid_charge:
      time: 
    - start_normalization:
      time:
    - end_normalization:
      time:
```

#### model_testing.ipynb ####
* test notebook for the model_import module

## Flask Server ##

This section of the software implements the REST HTTP server within which 
communication between the different programs can occur. It uses the python module
Flask to run the HTTP server along with SQLAlchemy to create the SQLite3
database. The understanding of the way this is implemented can be gained through 
this [Tutorial](https://flask.palletsprojects.com/en/2.2.x/tutorial/). We use 
python [Requests](https://requests.readthedocs.io/en/latest/) module to implement 
the REST API. 

### Program Outline ###

#### __init__.py ####
* Application Factory for the flask server
* ``create_app()``: Initializes the flask application

#### model.py ####
* Class definition using SQLAlchemy to define a database
* ``dump_datetime()``: Deserialize datetime object into string form for JSON processing.
* ``deserialize()``: Convert packet dictionary into a packet_history object.
* ``packet_history(db.Model)``: Defintion of the columns in the table using SQLAlchemy model conversion.
  * id - table primary key, autoincremented integer
  * packet_id - CAN ID of the packet 
  * packet_name - name of the packet based on YAML definitons
  * board - PCB from which the packet was transmitted
  * timestamp - the time at which the packet was posted to the table
  * data - JSON formated packet data

#### telemetry.py ####
* Flask Blueprint for telemetry requests from the server. I won't be defining these on a function basis but by URL.
* ``/telemetry/``: POST and GET
  * A POST will add a packet to the packet_history table. 
  * A GET will return a JSON formated Dict of all the packets ordered by timestamp.
* ``/telemetry/<board_name>``: POST and GET
  * a POST will add a packet to the packet_history table.
  * a GET will return a JSON formatted Dict of all packets related to the board in the URL ordered by timestamp
* ``/telemetry/<board_name>/<packet_name>``: POST and GET
  * a POST will add a packet to the packet_history table.
  * a GET will return a JSON formatted Dict of the packet specified in the URL ordered by timestamp 
* ``/telemetry/<board_name>/<packet_name>/<X>``: GET
  * a GET will return the latest ``X`` packets of type ``packet_name``
* ``/telemetry/<board_name>/<packet_name>/latest``: GET
  * GETting will return the most recently recieved packet specified in the URL as a JSON formatted dict
* ``/telemetry/<board_name>/<packet_name>/YYYY-MM-DDTHH:MM:SS_YYYY-MM-DDTHH:MM:SS``: GET
  * GETting will return all packets of ``<packet_name>`` between the two times in the URL seperated by an underscore
  * Times should be listed in ISO8601 format as shown above

#### globals.py ####
* Flask blueprint for global variable access from parallelized tasks. 
* ``/globals/<var_name>``:POST and GET
  * Access dictionary of global variables
  * a POST will update the entry of the dict if ``var_name`` exists and create the key if it doesn't
  * a GET will return the value store in ``var_name`` and will abort with error code 404 if it doesn't exist