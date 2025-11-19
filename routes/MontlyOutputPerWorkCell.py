from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date

monthlyOutputperWorkcell = Blueprint("monthlyOutputperWorkcell", __name__)

@monthlyOutputperWorkcell.route("/api/monthlyOutputperWorkcell", methods=["GET"])
def get_monthly_output_per_workcell():
    today = date.today()

    this_month = today.month
    this_year = today.year

    # compute last month
    if this_month == 1:
        last_month = 12
        last_year = this_year - 1
    else:
        last_month = this_month - 1
        last_year = this_year

    # load sql file
    with open("queries/monthlyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query last month
    output_last_month = run_query(sql, (last_month, last_year))

    # return both sets
    return jsonify({
        "last_month": output_last_month
    })
