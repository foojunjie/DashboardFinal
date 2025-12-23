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
        workcell = r["name"]
        temp_total_good = r["totalgood"] or 0
        temp_total_expected = r["totalexpected"] or 0
        temp_ideal_run_time = r["idealruntime"] or 0
        temp_actual_run_time = r["actualruntime"] or 0
        temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
        temp_total_downtime_seconds = r["total_downtime_seconds"] or 0
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
                "total_good": 0,
                "total_expected": 0,
                "total_ideal_run_time": 0,
                "total_actual_run_time": 0,
                "total_planned_production_time_seconds": 0,
                "total_total_downtime_seconds": 0,
                "monthly": {i: {
                    "total_good": 0,
                    "total_expected": 0,
                    "total_ideal_run_time": 0,
                    "total_actual_run_time": 0,
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0,
                    } for i in range(1, 13)}
            }

        data = workcell_data[workcell]
        data["total_good"] += temp_total_good
        data["total_expected"] += temp_total_expected
        data["total_ideal_run_time"] += temp_ideal_run_time
        data["total_actual_run_time"] += temp_actual_run_time
        data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["total_total_downtime_seconds"] += temp_total_downtime_seconds

        if actenddate.year == this_year:
            month = actenddate.month
            data["monthly"][month]["total_good"] += temp_total_good
            data["monthly"][month]["total_expected"] += temp_total_expected
            data["monthly"][month]["total_ideal_run_time"] += temp_ideal_run_time
            data["monthly"][month]["total_actual_run_time"] += temp_actual_run_time
            data["monthly"][month]["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
            data["monthly"][month]["total_total_downtime_seconds"] += temp_total_downtime_seconds

    # Build final list
    final = []
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
            "monthly": [
                round(
                    ((float(data["monthly"][m]["total_good"])*100 / float(data["monthly"][m]["total_expected"]))
                    *(float(data["monthly"][m]["total_ideal_run_time"])*100 / float(data["monthly"][m]["total_actual_run_time"]))
                    *((float(data["monthly"][m]["total_planned_production_time_seconds"]) - float(data["monthly"][m]["total_total_downtime_seconds"]))*100 / float(data["monthly"][m]["total_planned_production_time_seconds"])))
                      /10000, 2)
                if  data["monthly"][m]["total_expected"] > 0 and data["monthly"][m]["total_actual_run_time"] > 0 and data["monthly"][m]["total_planned_production_time_seconds"] > 0 
                else 0
                for m in range(1, 13)
            ]
        })

    return jsonify({"Oee": final})
