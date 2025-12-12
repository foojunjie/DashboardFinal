from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime
from flask import Blueprint, jsonify, request

OEE_by_WorkCell_per_Day = Blueprint("OEE_by_WorkCell_per_Day", __name__)

@OEE_by_WorkCell_per_Day.route("/api/OEE_by_WorkCell_per_Day", methods=["GET"])
def get_OEE_by_WorkCell_per_Day():
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
    this_day = today.day

    with open("queries/OEEbyWCperDay.sql", "r") as f:
        sql = f.read()

    Oee = run_query(sql, (this_day, this_month, this_year))

    final_OEE_per_Day = []
    workcell_data = {}

    for r in Oee:
        workcell = r["workcell_name"]
        temp_oee = r["oee_percentage"] if r["oee_percentage"] is not None else 0
        temp_quality = r["quality_percentage"] if r["quality_percentage"] is not None else 0
        temp_performance = r["performance_percentage"] if r["performance_percentage"] is not None else 0
        temp_availability = r["availability_percentage"] if r["availability_percentage"] is not None else 0
        actenddate = r["actenddate"]

        if actenddate is None:
            continue

        # Convert string timestamp with timezone
        if isinstance(actenddate, str):
            # Remove timezone manually (+08 part)
            actenddate = actenddate.split("+")[0]
            actenddate = datetime.strptime(actenddate, "%Y-%m-%d %H:%M:%S.%f")

        hour = actenddate.hour

        if workcell not in workcell_data:
            workcell_data[workcell] = {
                "total_oee": 0,
                "total_quality": 0,
                "total_performance": 0,
                "total_availability": 0,
                "count": 0,
                "hourly": {i: {"total": 0, "count": 0} for i in range(1, 25)}
            }

        data = workcell_data[workcell]
        data["total_oee"] += temp_oee
        data["total_quality"] += temp_quality
        data["total_performance"] += temp_performance
        data["total_availability"] += temp_availability
        data["count"] += 1

        # Accumulate per workcell
        data["hourly"][hour]["total"] += temp_oee
        data["hourly"][hour]["count"] += 1


    for wc, data in workcell_data.items():
        count = data["count"]
        final_OEE_per_Day.append({
            "workcell": wc,
            "oee": round(data["total_oee"] / count, 2) if count else 0,
            "quality": round(data["total_quality"] / count, 2) if count else 0,
            "performance": round(data["total_performance"] / count, 2) if count else 0,
            "availability": round(data["total_availability"] / count, 2) if count else 0,
            "hourly": [
                round(data["hourly"][m]["total"] / data["hourly"][m]["count"], 2) 
                if data["hourly"][m]["count"] > 0 else 0
                for m in range(1, 25)
            ]
        })


    return jsonify({"Oee_per_Day": final_OEE_per_Day})
