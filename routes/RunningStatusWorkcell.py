from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query

Running_Status_Workcell = Blueprint("Running_Status_Workcell", __name__)

@Running_Status_Workcell.route("/api/Running_Status_Workcell", methods=["GET"])
def get_Running_Status_Workcell():

    with open("queries/RunningStatusWorkcell.sql", "r") as f:
        sql = f.read()
        
    status = run_query(sql, ())
        
    return jsonify({"Status": status})

