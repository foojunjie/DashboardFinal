from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date

weeklyOutputperWorkcell = Blueprint("weeklyOutputperWorkcell", __name__)

@weeklyOutputperWorkcell.route("/api/weeklyOutput", methods=["GET"])
def get_weekly_output_per_workcell():
    today = date.today()

    # load sql file
    with open("queries/weeklyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query this week
    this_week = run_query(sql, (today,))

    # return set
    return jsonify({
        "this_week": this_week
    })
