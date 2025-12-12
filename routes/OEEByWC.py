from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_WorkCell = Blueprint("OEE_by_WorkCell", __name__)

@OEE_by_WorkCell.route("/api/OEE_by_WorkCell", methods=["GET"])
def get_OEE_by_WorkCell():
    today = date.today()
    this_year = today.year

    with open("queries/OEEbyWC.sql", "r") as f:
        sql = f.read()

    Oee = run_query(sql, ())

    # Group data by workcell
    workcell_data = {}

    for r in Oee:
        workcell = r["workcell_name"]
        temp_oee = r["oee_percentage"] or 0
        temp_quality = r["quality_percentage"] or 0
        temp_performance = r["performance_percentage"] or 0
        temp_availability = r["availability_percentage"] or 0
        actenddate = r["actenddate"]

        # Skip if no actenddate
        if actenddate is None:
            continue

        # Convert string timestamp with timezone
        if isinstance(actenddate, str):
            actenddate = actenddate.split("+")[0]
            actenddate = datetime.strptime(actenddate, "%Y-%m-%d %H:%M:%S.%f")

        if workcell not in workcell_data:
            workcell_data[workcell] = {
                "total_oee": 0,
                "total_quality": 0,
                "total_performance": 0,
                "total_availability": 0,
                "count": 0,
                "monthly": {i: {"total": 0, "count": 0} for i in range(1, 13)}
            }

        data = workcell_data[workcell]
        data["total_oee"] += temp_oee
        data["total_quality"] += temp_quality
        data["total_performance"] += temp_performance
        data["total_availability"] += temp_availability
        data["count"] += 1

        if actenddate.year == this_year:
            month = actenddate.month
            data["monthly"][month]["total"] += temp_oee
            data["monthly"][month]["count"] += 1

    # Build final list
    final = []
    for wc, data in workcell_data.items():
        count = data["count"]
        final.append({
            "workcell": wc,
            "oee": round(data["total_oee"] / count, 2) if count else 0,
            "quality": round(data["total_quality"] / count, 2) if count else 0,
            "performance": round(data["total_performance"] / count, 2) if count else 0,
            "availability": round(data["total_availability"] / count, 2) if count else 0,
            "monthly": [
                round(data["monthly"][m]["total"] / data["monthly"][m]["count"], 2) 
                if data["monthly"][m]["count"] > 0 else 0
                for m in range(1, 13)
            ]
        })

    return jsonify({"Oee": final})
