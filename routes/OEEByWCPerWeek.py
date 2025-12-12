from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, timedelta, datetime

OEE_by_WorkCell_per_Week = Blueprint("OEE_by_WorkCell_per_Week", __name__)

@OEE_by_WorkCell_per_Week.route("/api/OEE_by_WorkCell_per_Week", methods=["GET"])
def get_OEE_by_WorkCell_per_Week():
    today = date.today()

    iso = today.isoweekday()
    start_of_week = today - timedelta(days=iso-1)
    end_of_week = start_of_week + timedelta(days=6)

    with open("queries/OEEbyWCperWeek.sql", "r") as f:
        sql = f.read()

    Oee = run_query(sql, (start_of_week, end_of_week))

    final_OEE_per_Week = []
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

        day = actenddate.day

        if workcell not in workcell_data:
            workcell_data[workcell] = {
                "total_oee": 0,
                "total_quality": 0,
                "total_performance": 0,
                "total_availability": 0,
                "count": 0,
                "daily": {i: {"total": 0, "count": 0} for i in range(1, 8)}
            }

        data = workcell_data[workcell]
        data["total_oee"] += temp_oee
        data["total_quality"] += temp_quality
        data["total_performance"] += temp_performance
        data["total_availability"] += temp_availability
        data["count"] += 1


        if day == start_of_week.day:
            week_day = 1
        elif day == (start_of_week + timedelta(days=1)).day:
            week_day = 2
        elif day == (start_of_week + timedelta(days=2)).day:
            week_day = 3
        elif day == (start_of_week + timedelta(days=3)).day:
            week_day = 4
        elif day == (start_of_week + timedelta(days=4)).day:
            week_day = 5
        elif day == (start_of_week + timedelta(days=5)).day:
            week_day = 6
        elif day == (start_of_week + timedelta(days=6)).day:
            week_day = 7

        # Accumulate per workcell
        data["daily"][week_day]["total"] += temp_oee
        data["daily"][week_day]["count"] += 1

    for wc, data in workcell_data.items():
        count = data["count"]
        final_OEE_per_Week.append({
            "workcell": wc,
            "oee": round(data["total_oee"] / count, 2) if count else 0,
            "quality": round(data["total_quality"] / count, 2) if count else 0,
            "performance": round(data["total_performance"] / count, 2) if count else 0,
            "availability": round(data["total_availability"] / count, 2) if count else 0,
            "daily": [
                round(data["daily"][m]["total"] / data["daily"][m]["count"], 2) 
                if data["daily"][m]["count"] > 0 else 0
                for m in range(1, 8)
            ]
        })

    return jsonify({"Oee_per_Week": final_OEE_per_Week})

