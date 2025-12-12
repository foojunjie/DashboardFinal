from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_WorkCell_per_Month = Blueprint("OEE_by_WorkCell_per_Month", __name__)

@OEE_by_WorkCell_per_Month.route("/api/OEE_by_WorkCell_per_Month", methods=["GET"])
def get_OEE_by_WorkCell_per_Month():
    today = date.today()

    this_month = today.month
    this_year = today.year

    # ---- Load SQL ----
    with open("queries/OEEbyWCperMonth.sql", "r") as f:
        sql = f.read()

    rows = run_query(sql, (this_month, this_year))

    final = []
    workcell_data = {}
    for r in rows:
        workcell = r["workcell_name"]
        temp_oee = r["oee_percentage"] or 0
        temp_quality = r["quality_percentage"] or 0
        temp_performance = r["performance_percentage"] or 0
        temp_availability = r["availability_percentage"] or 0
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
                "weekly": {i: {"total": 0, "count": 0} for i in range(1, 6)}
            }

        data = workcell_data[workcell]
        data["total_oee"] += temp_oee
        data["total_quality"] += temp_quality
        data["total_performance"] += temp_performance
        data["total_availability"] += temp_availability
        data["count"] += 1

        # Week of month
        if day <= 7:
            week = 1
        elif day <= 14:
            week = 2
        elif day <= 21:
            week = 3
        elif day <= 28:
            week = 4
        else:
            week = 5

        # Accumulate per workcell
        data["weekly"][week]["total"] += temp_oee
        data["weekly"][week]["count"] += 1

        
    for wc, data in workcell_data.items():
        count = data["count"]
        final.append({
            "workcell": wc,
            "oee": round(data["total_oee"] / count, 2) if count else 0,
            "quality": round(data["total_quality"] / count, 2) if count else 0,
            "performance": round(data["total_performance"] / count, 2) if count else 0,
            "availability": round(data["total_availability"] / count, 2) if count else 0,
            "weekly": [
                round(data["weekly"][m]["total"] / data["weekly"][m]["count"], 2) 
                if data["weekly"][m]["count"] > 0 else 0
                for m in range(1, 6)
            ]
        })

    return jsonify({"Oee_per_Month": final})
