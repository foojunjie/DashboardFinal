from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query

Running_Status_Station = Blueprint("Running_Status_Station", __name__)

@Running_Status_Station.route("/api/Running_Status_Station", methods=["GET"])
def get_Running_Status_Station():

    with open("queries/RunningStatusStation.sql", "r") as f:
        sql = f.read()
        
    status = run_query(sql, ())
        
    return jsonify({"Status": status})

