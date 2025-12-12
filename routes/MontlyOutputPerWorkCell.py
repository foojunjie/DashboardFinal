from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date

monthlyOutputperWorkcell = Blueprint("monthlyOutputperWorkcell", __name__)

@monthlyOutputperWorkcell.route("/api/monthlyOutputperWorkcell", methods=["GET"])
def get_monthly_output_per_workcell():
    today = date.today()

    this_month = today.month
    this_year = today.year

    # load sql file
    with open("queries/monthlyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query this month
    output_last_month = run_query(sql, (this_month, this_year))

    # return set
    return jsonify({
        "last_month": output_last_month
    })
