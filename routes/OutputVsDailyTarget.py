from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date

OutputVsDailyTarget = Blueprint("OutputVsDailyTarget", __name__)

@OutputVsDailyTarget.route("/api/OutputVsDailyTarget", methods=["GET"])
def get_OutputVsDailyTarget():
    today = date.today()

    this_day = today.day
    this_month = today.month
    this_year = today.year

    with open("queries/OutputPerWorkCellwithStation.sql", "r") as f:
        sql = f.read()

    # query today
    output = run_query(sql, (this_day,this_month,this_year))

    with open("queries/WorkcellTable.sql", "r") as f:
        sql = f.read()

    # query today
    table = run_query(sql, (this_day,this_month,this_year))

    with open("queries/StationStatus.sql", "r") as f:
        sql = f.read()

    # query today
    status = run_query(sql, (this_day,this_month,this_year))

    # return set
    return jsonify({
        "output": output,
        "table": table,
        "status": status
    })
