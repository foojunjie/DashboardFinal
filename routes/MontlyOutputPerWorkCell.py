from flask import Blueprint, jsonify, request
from DBConn.ejtcConn import run_query
from datetime import date, datetime

monthlyOutputperWorkcell = Blueprint("monthlyOutputperWorkcell", __name__)

@monthlyOutputperWorkcell.route("/api/monthlyOutputperWorkcell", methods=["GET"])
def get_monthly_output_per_workcell():
    today = date.today()

    # Check if a specific date was requested
    date_param = request.args.get('date')
    if date_param:
        try:
            # Parse date from ISO format (YYYY-MM-DD)
            today = datetime.strptime(date_param, '%Y-%m-%d').date()
        except Exception:
            pass  # Use default today if parse fails

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
