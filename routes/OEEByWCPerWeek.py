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
                "daily": {i: {
                    "total_good": 0,
                    "total_expected": 0,
                    "total_ideal_run_time": 0,
                    "total_actual_run_time": 0,
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0,
                } for i in range(1, 8)}
            }

        data = workcell_data[workcell]
        data["total_good"] += temp_total_good
        data["total_expected"] += temp_total_expected
        data["total_ideal_run_time"] += temp_ideal_run_time
        data["total_actual_run_time"] += temp_actual_run_time
        data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["total_total_downtime_seconds"] += temp_total_downtime_seconds


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
        data["daily"][week_day]["total_good"] += temp_total_good
        data["daily"][week_day]["total_expected"] += temp_total_expected
        data["daily"][week_day]["total_ideal_run_time"] += temp_ideal_run_time
        data["daily"][week_day]["total_actual_run_time"] += temp_actual_run_time
        data["daily"][week_day]["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["daily"][week_day]["total_total_downtime_seconds"] += temp_total_downtime_seconds

    for wc, data in workcell_data.items():
        final_OEE_per_Week.append({
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
            "daily": [
               round(
                    ((float(data["daily"][m]["total_good"])*100 / float(data["daily"][m]["total_expected"]))
                    *(float(data["daily"][m]["total_ideal_run_time"])*100 / float(data["daily"][m]["total_actual_run_time"]))
                    *((float(data["daily"][m]["total_planned_production_time_seconds"]) - float(data["daily"][m]["total_total_downtime_seconds"]))*100 / float(data["daily"][m]["total_planned_production_time_seconds"])))
                      /10000, 2)
                if  data["daily"][m]["total_expected"] > 0 and data["daily"][m]["total_actual_run_time"] > 0 and data["daily"][m]["total_planned_production_time_seconds"] > 0 
                else 0
                for m in range(1, 8)
            ]
        })

    return jsonify({"Oee_per_Week": final_OEE_per_Week})

