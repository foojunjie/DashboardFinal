from flask import Blueprint, jsonify, request
from DBConn.ejtcConn import run_query
from datetime import date, datetime

weeklyOutputperWorkcell = Blueprint("weeklyOutputperWorkcell", __name__)

@weeklyOutputperWorkcell.route("/api/weeklyOutput", methods=["GET"])
def get_weekly_output_per_workcell():
    today = date.today()

     # Check if a specific date was requested
    date_param = request.args.get('date')
    if date_param:
        try:
            # Parse date from ISO format (YYYY-MM-DD)
            today = datetime.strptime(date_param, '%Y-%m-%d').date()
        except Exception:
            pass  # Use default today if parse fails

    # load sql file
    with open("queries/weeklyOutputPerWorkcell.sql", "r") as f:
        sql = f.read()

    # query this week
    this_week = run_query(sql, (today,))

    # return set
    return jsonify({
        "this_week": this_week
    })
