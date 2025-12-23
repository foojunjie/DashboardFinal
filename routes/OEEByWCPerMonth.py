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
        workcell = r["name"]
        temp_total_good = r["totalgood"] or 0
        temp_total_expected = r["totalexpected"] or 0
        temp_ideal_run_time = r["idealruntime"] or 0
        temp_actual_run_time = r["actualruntime"] or 0
        temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
        temp_total_downtime_seconds = r["total_downtime_seconds"] or 0
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
                "total_good": 0,
                "total_expected": 0,
                "total_ideal_run_time": 0,
                "total_actual_run_time": 0,
                "total_planned_production_time_seconds": 0,
                "total_total_downtime_seconds": 0,
                "weekly": {i: {
                    "total_good": 0,
                    "total_expected": 0,
                    "total_ideal_run_time": 0,
                    "total_actual_run_time": 0,
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0,
                } for i in range(1, 6)}
            }

        data = workcell_data[workcell]
        data["total_good"] += temp_total_good
        data["total_expected"] += temp_total_expected
        data["total_ideal_run_time"] += temp_ideal_run_time
        data["total_actual_run_time"] += temp_actual_run_time
        data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["total_total_downtime_seconds"] += temp_total_downtime_seconds

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
        data["weekly"][week]["total_good"] += temp_total_good
        data["weekly"][week]["total_expected"] += temp_total_expected
        data["weekly"][week]["total_ideal_run_time"] += temp_ideal_run_time
        data["weekly"][week]["total_actual_run_time"] += temp_actual_run_time
        data["weekly"][week]["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["weekly"][week]["total_total_downtime_seconds"] += temp_total_downtime_seconds

        
    for wc, data in workcell_data.items():
        final.append({
            "workcell": wc,
            "oee": round(
                ((float(data["total_good"])*100 / float(data["total_expected"]))
                *(float(data["total_ideal_run_time"])*100 / float(data["total_actual_run_time"]))
                *((float(data["total_planned_production_time_seconds"]) - float(data["total_total_downtime_seconds"]))*100 / float(data["total_planned_production_time_seconds"])))
                /10000, 2) 
            if data["total_expected"] > 0 and data["total_actual_run_time"] > 0 and data["total_planned_production_time_seconds"] > 0 
            else 0,
            "quality": round(float(data["total_good"])*100 / float(data["total_expected"]), 2) if data["total_expected"] else 0,
            "performance": round(float(data["total_ideal_run_time"])*100 / float(data["total_actual_run_time"]), 2) if data["total_actual_run_time"] else 0,
            "availability": round((float(data["total_planned_production_time_seconds"]) - float(data["total_total_downtime_seconds"]))*100 / float(data["total_planned_production_time_seconds"]), 2) if  data["total_planned_production_time_seconds"] else 0,
            "weekly": [
                round(
                    ((float(data["weekly"][m]["total_good"])*100 / float(data["weekly"][m]["total_expected"]))
                    *(float(data["weekly"][m]["total_ideal_run_time"])*100 / float(data["weekly"][m]["total_actual_run_time"]))
                    *((float(data["weekly"][m]["total_planned_production_time_seconds"]) - float(data["weekly"][m]["total_total_downtime_seconds"]))*100 / float(data["weekly"][m]["total_planned_production_time_seconds"])))
                      /10000, 2)
                if  data["weekly"][m]["total_expected"] > 0 and data["weekly"][m]["total_actual_run_time"] > 0 and data["weekly"][m]["total_planned_production_time_seconds"] > 0 
                else 0
                for m in range(1, 6)
            ]
        })

    return jsonify({"Oee_per_Month": final})
