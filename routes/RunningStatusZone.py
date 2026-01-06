from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query

Running_Status_Zone = Blueprint("Running_Status_Zone", __name__)

@Running_Status_Zone.route("/api/Running_Status_Zone", methods=["GET"])
def get_Running_Status_Zone():

    with open("queries/RunningStatusZone.sql", "r") as f:
        sql = f.read()
        
    status = run_query(sql, ())
        
    return jsonify({"Status": status})

