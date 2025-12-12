from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date

dailyOutputperWorkcell = Blueprint("dailyOutputperWorkcell", __name__)

@dailyOutputperWorkcell.route("/api/dailyOutput", methods=["GET"])
def get_daily_output_per_workcell():
    todayTime = date.today()

    # load sql file
    with open("queries/DailyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query today
    today = run_query(sql, (todayTime,))

    # return set
    return jsonify({
        "today": today
    })
