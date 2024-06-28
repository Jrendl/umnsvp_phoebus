"""@package docstring
Flask blueprint for telemetry requests

"""

import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, current_app
)
from . import socketio
from werkzeug.exceptions import abort
from flask_sqlalchemy import SQLAlchemy, session

import sys
from pathlib import Path
from typing import List
from time import time
from server import db
import yaml
import datetime

src_path = Path("./src/")
can_parser_path = Path("../can_packet_parser")
server_path = Path("./server/")
sys.path.append(str(src_path))
sys.path.append(str(can_parser_path))
sys.path.append(str(server_path))
from scrappy import yamls_to_packets, packet_t
from server.model import packet_history, deserialize

# Bluprint initialization for telemetry
bp = Blueprint("telemetry", __name__, url_prefix="/telemetry")
# Use scrappy to parse yamls and get defs.
# TODO: find a way to pass this in with Phoebus so that everything pulls from the same packets
packet_defs = yamls_to_packets(Path("../../src/cangen/packets"))


def get_boards(yaml_file: Path):
    with open(yaml_file, "r", encoding="utf-8") as stream:
        boards = yaml.safe_load(stream)["boards"]
        board_tree = {a["name"]: a["transmit"] for a in boards}
        # the board tree looks like {"g4_example": [tracker_data, vision_status_front], ...}
        # it uses the transmitted packets for each board. This makes more logical sense because there
        # is (typically) only one sender of a kind of packet
        return board_tree


def do_post_action(packet_info: List):  # passed in as list of telemetry class model
    """Action for posting is the same no matter which view is called
        @param packet_info list of parsed packets in format list(Dict(ID, Packet name, Board, Data))"""
    socketio.emit("packet", packet_info)
    for packet in packet_info:
        db.session.add(deserialize(packet))
    db.session.commit()


def safe_return(q):
    """
    Throws a 404 error if there are no packets in the accessed space yet.
    @param q the object containing the query from the table
    """
    if len(q.all()) == 0:
        abort(404, "The bus has not received any of these packets yet.")
    else:
        return jsonify(json_list=[p.serialize for p in q.all()])


bms_id = {"namespace": "umnsvp.phoebus", "key": "board.bms"}

@bp.route("/schema", methods=["GET"])
def get_board_schema():
    """Returns a schema for the structure of the objects for OpenMCT"""
    board_ids = list()
    boards = get_boards(Path("../../src/cangen/packets/boards.yaml")).keys()
    for board in boards:
        if board == "flight_computer":
            board = "car_control"
        elif board == "skylab2_demo" or board == "g4_example" or board == "vision":
            continue
        board_id = dict()
        board_id["namespace"] = "umnsvp.phoebus"
        board_id["key"] = f"board.{board}"
        board_ids.append(board_id)
    # return jsonify(get_boards(Path("../../src/cangen/packets/boards.yaml")))
    return jsonify(board_ids)


@bp.route("/schema/<string:board>", methods=["GET"])
def get_packet_schema(board: str):
    """ This function returns the packet schemata of a particular board. 
        @params: board (string: name of board)
    """
    board_id = {"namespace": "umnsvp.phoebus", "key": f"board.{board}"}
    packets = list()
    board_def = dict()
    with open(f"../../src/cangen/packets/{board}.yaml", "r", encoding="utf-8") as stream:
        board_def = yaml.safe_load(stream)['packets']

    for packet in board_def:
        packet_name = packet["name"]
        if isinstance(packet_name, list):
            for subpacket in packet_name:
                packets.append({"key": f"board.{board}.{subpacket}", "namespace": "umnsvp.phoebus"})
        else:
            if "repeat" in packet.keys():
                for i in range(packet["repeat"]):
                    packets.append({"key": f"board.{board}.{packet_name}_{i}", "namespace": "umnsvp.phoebus"})
            else:
                packets.append({"key": f"board.{board}.{packet_name}", "namespace": "umnsvp.phoebus"})

    return jsonify({
        "identifier": board_id,
        "name": board,
        "type": "umnsvp-board",
        "description": f"This is the {board} board!",
        "packets": packets
    })

@bp.route("/schema/<string:board>/<string:packet>", methods=["GET"])
def get_packet_data_schema(board: str, packet: str):
    packet_id = {"namespace": "umnsvp.phoebus", "key": f"board.{board}.{packet}"}
    data_fields = list()
    board_def = dict()
    with open(f"../../src/cangen/packets/{board}.yaml", "r", encoding="utf-8") as stream:
        board_def = yaml.safe_load(stream)['packets']
    
    for packet_ in board_def:
        if packet_["name"] == packet or packet in packet_["name"]:
            for data_field in packet_["data"]:
                data_field_name = data_field["name"]
                data_fields.append({"key": f"board.{board}.{packet}.{data_field_name}", "namespace": "umnsvp.phoebus"})
        elif not isinstance(packet_["name"], list) and packet_["name"] in packet:
            for data_field in packet_["data"]:
                data_field_name = data_field["name"]
                data_fields.append({"key": f"board.{board}.{packet}.{data_field_name}", "namespace": "umnsvp.phoebus"})
            break

    return jsonify({
        "identifier": packet_id,
        "name": packet,
        "type": "umnsvp-packet",
        "description": f"This is the {packet} packet!",
        "data_fields": data_fields
    })
    # data = list()
    # board_def = dict()
    # with open(f"../../src/cangen/packets/{board}.yaml", "r", encoding="utf-8") as stream:
    #     board_def = yaml.safe_load(stream)['packets']

    # for packet_ in board_def:
    #     if packet_['name'] == packet:
    #         for data_field in packet_['data']:
    #             if ('units' in data_field):
    #                 data.append({"key": data_field['name'], "unit": data_field['units'], "format": data_field['type'], "hints": { "range": 1 }})
    #             else:
    #                 data.append({"key": data_field['name'], "format": data_field['type'], "hints": { "range": 1 }})
    #         break

    # data.append({"key": "utc", "source": "timestamp", "format": "utc", "hints": {"domain": 1}})
        
    # return jsonify({
    #     "identifier": {"key": f"board.{board}.{packet}", "namespace": "umnsvp.phoebus"},
    #     "name": packet,
    #     "type": "umnsvp-packet",
    #     "telemetry": {
    #         "values": data
    #     }
    # })

@bp.route("/schema/<string:board>/<string:packet>/<string:data_field>", methods=["GET"])
def get_measurement_object(board: str, packet: str, data_field: str):
    measurement_object = list()
    with open(f"../../src/cangen/packets/{board}.yaml", "r", encoding="utf-8") as stream:
        board_def = yaml.safe_load(stream)['packets']

    for packet_ in board_def:
        if packet_['name'] == packet:
            for data_field_ in packet_['data']:
                if data_field_['name'] == data_field:
                    if 'units' in data_field_:
                        measurement_object.append({"key": data_field_['name'], "unit": data_field_['units'], "format": data_field_['type'], "hints": { "range": 1 }})
                    else:
                        measurement_object.append({"key": data_field_['name'], "format": data_field_['type'], "hints": { "range": 1 }})
            break
        elif not isinstance(packet_["name"], list) and packet_["name"] in packet:
            for data_field_ in packet_['data']:
                if data_field_['name'] == data_field:
                    if 'units' in data_field_:
                        measurement_object.append({"key": data_field_['name'], "unit": data_field_['units'], "format": data_field_['type'], "hints": { "range": 1 }})
                    else:
                        measurement_object.append({"key": data_field_['name'], "format": data_field_['type'], "hints": { "range": 1 }})
            break

    measurement_object.append({"key": "utc", "source": "timestamp", "format": "utc", "hints": {"domain": 1}})
    return jsonify({
        "identifier": {"key": f"board.{board}.{packet}.{data_field}", "namespace": "umnsvp.phoebus"},
        "name": data_field,
        "type": "umnsvp-data",
        "telemetry": {
            "values": measurement_object
        }
    })


@bp.route("/", methods=["GET", "POST"])
def all_boards():
    """View to post and get for /telemetry/"""
    if request.method == "POST":
        do_post_action(request.json)
        return request.json
    q = packet_history.query.order_by(packet_history.timestamp)
    return safe_return(q)


@bp.route("/latest", methods=["GET"])
def get_all_latest():
    out_dict = {}
    for ID, packet_t in packet_defs.items():
        q = packet_history.query.filter_by(packet_name=packet_t.name).order_by(packet_history.timestamp)
        out_dict[packet_t.board][packet_t.name] = q[-1].serialize
    if len(q.all()) == 0:
        abort(404, "The bus has not received any packets yet.")
    else:
        return jsonify(out_dict)


@bp.route("/<string:board_inp>", methods=["GET", "POST"])
def board(board_inp: str):
    """View to POST and GET at board level"""
    if request.method == "POST":
        do_post_action(request.json)
        return request.json

    # FIXME: this sorts by packet name - should it do that? seems odd.
    q = packet_history.query.filter_by(board=board_inp).order_by(packet_history.packet_name, packet_history.timestamp)
    return safe_return(q)


@bp.route("/<string:board>/<string:packet>", methods=["GET", "POST"])
def packet_access(board: str, packet: str):
    """View to POST and GET at packet level"""
    if request.method == "POST":
        do_post_action(request.json)
        return request.json

    q = packet_history.query.filter_by(board=board, packet_name=packet).order_by(packet_history.timestamp)

    # check each query parameter and add it to the query object.
    # if request.args["start_time"]:
    #     # start time in unix timestamp (seconds)
    #     q = q.filter(packet_history.timestamp >= datetime.datetime.fromtimestamp(int(request.args["start_time"])))
    # if request.args["end_time"]:
    #     q = q.filter(packet_history.timestamp <= datetime.datetime.fromtimestamp(int(request.args["end_time"])))

    # if request.args["num"]:
    #     q = q.limit(request.args["num"])

    return safe_return(q)


@bp.route("/<string:board>/<string:packet>/<int:num>", methods=["GET"])
def get_last_X(board: str, packet: str, num: int):
    """View to GET the latest X number of packet p"""
    q = packet_history.query.filter_by(board=board, packet_name=packet).order_by(packet_history.id.desc()).limit(num)
    return safe_return(q)


@bp.route("/<string:board>/<string:packet>/<string:times>", methods=["GET"])
def get_times_between(board: str, packet: str, times: str):
    """View to get the packets between two times
        Times are listed in ISO8601 format with an underscore (_) between them
        YYYY-MM-DDTHH:MM:SS_YYYY-MM-DDTHH:MM:SS

        Break! actually using unix timestamp UTC
    """
    time_list = times.split('_')
    print(time_list[0], time_list[1])
    q = packet_history.query.filter(
        packet_history.board == board,
        packet_history.packet_name == packet,
        packet_history.timestamp >= datetime.datetime.fromisoformat(time_list[0]),
        packet_history.timestamp <= datetime.datetime.fromisoformat(time_list[1])
    ).order_by(packet_history.timestamp)
    return safe_return(q)


@bp.route("/<string:board>/<string:packet>/latest", methods=["GET"])
def get_latest(board: str, packet: str):
    """View to get the latest packet"""
    q = packet_history.query.filter_by(board=board, packet_name=packet)
    if len(q.all()) == 0:
        abort(404, "The bus has not recieved any packets yet.")
    else:
        return jsonify(q[-1].serialize)
