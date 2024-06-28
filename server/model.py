"""@package docstring
SQLAlchemy class definiton for the Telemetry schema 
Organize packets as a single table with 6 columns
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from server import db
from typing import Dict

def dump_datetime(value: datetime):
    """Deserialize datetime object into string form for JSON processing.
        @param value the datetime object to dump"""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

def deserialize(serial_packet: Dict):
    """Deserialize packet for posting to the schema
        @param serial_packet the json formated packet to make into a packet_history object
    """
    return packet_history(packet_id= serial_packet["ID"], 
                            packet_name= serial_packet["packet_name"], 
                            board = serial_packet["board"], 
                            data = serial_packet["data"])


class packet_history(db.Model):
    """Table definition class inherriting from SQLAlchemy Model
        Organize table into 6 columns
        * id - table primary key, autoincremented integer
        * packet_id - CAN ID of the packet 
        * packet_name - name of the packet based on YAML definitons
        * board - PCB from which the packet was transmitted
        * timestamp - the time at which the packet was posted to the table
        * data - JSON formated packet data
    """
    __tablename__ = "packet_history"

    id = db.Column("packet_num", db.Integer, primary_key = True, autoincrement=True)
    packet_id = db.Column(db.Integer, index = True, nullable = False)
    packet_name = db.Column(db.Text(50), index = True, nullable = False)
    board = db.Column(db.Text(50), index = True, nullable = False)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow(), index = True, nullable = False)
    data = db.Column(db.JSON, nullable = False) #data as parsed json

    def __init__(self, packet_id: int, packet_name: str, board: str, data: Dict):
        """Constructor for packet_history class"""
        self.packet_id = packet_id
        self.packet_name = packet_name
        self.board = board
        self.timestamp = datetime.utcnow()
        self.data = data

    @property
    def serialize(self):
        """Serialize packet into Dict for display in JSON format"""
        return {
            "timestamp" : dump_datetime(self.timestamp),
            "ID" : hex(self.packet_id), 
            "packet_name" : self.packet_name,
            "data" : self.data
        }
    
    
