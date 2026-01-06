from flask import Blueprint, jsonify, request
from DBConn.ejtcConn import run_query
from datetime import date, datetime


dailyOutputperWorkcell = Blueprint("dailyOutputperWorkcell", __name__)

@dailyOutputperWorkcell.route("/api/dailyOutput", methods=["GET"])
def get_daily_output_per_workcell():
    today = date.today()

    # Check if a specific date was requested
    date_param = request.args.get('date')
    if date_param:
        try:
            # Parse date from ISO format (YYYY-MM-DD)
            today = datetime.strptime(date_param, '%Y-%m-%d').date()
        except Exception:
            pass  # Use default today if parse fails

    this_day = today.day
    this_month = today.month
    this_year = today.year

    # load sql file
    with open("queries/DailyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query today
    today = run_query(sql, (this_day, this_month, this_year))

    # return set
    return jsonify({
        "today": today
    })
