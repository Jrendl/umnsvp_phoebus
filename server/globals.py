"""
@package docstring
Global variable blueprint for flask server. 
Stores global vars for access from parallelized tasks without needing to worry about Mutex locks
"""
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, current_app
)
from werkzeug.exceptions import abort

import sys
from pathlib import Path
from typing import List
from time import time
src_path = Path("./src/")
can_parser_path = Path("../can_packet_parser")
server_path = Path("./server/")
sys.path.append(str(src_path))
sys.path.append(str(can_parser_path))
sys.path.append(str(server_path))

#Bluprint initialization for telemetry
bp = Blueprint("globals", __name__, url_prefix="/globals")

global_dict = {}

@bp.route("/", methods = ["GET"])
def all_globals():
    """
    View to get all global variables
    """

    return jsonify(global_dict)

@bp.route("/<string:var>", methods = ["GET", "POST"])
def global_var(var: str):
    """
    View to access global variables
    """
    if request.method == "POST":
        global_dict[var] = request.json
    if var in global_dict.keys():
        return jsonify(global_dict[var])
    else: 
        abort(404, "The variable requested does not exist.")
