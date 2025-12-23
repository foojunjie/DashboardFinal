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

        hour = actenddate.hour

        if workcell not in workcell_data:
            workcell_data[workcell] = {
                "total_good": 0,
                "total_expected": 0,
                "total_ideal_run_time": 0,
                "total_actual_run_time": 0,
                "total_planned_production_time_seconds": 0,
                "total_total_downtime_seconds": 0,
                "hourly": {i: {
                    "total_good": 0,
                    "total_expected": 0,
                    "total_ideal_run_time": 0,
                    "total_actual_run_time": 0,
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0,
                } for i in range(1, 25)}
            }

        data = workcell_data[workcell]
        data["total_good"] += temp_total_good
        data["total_expected"] += temp_total_expected
        data["total_ideal_run_time"] += temp_ideal_run_time
        data["total_actual_run_time"] += temp_actual_run_time
        data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["total_total_downtime_seconds"] += temp_total_downtime_seconds

        # Accumulate per workcell
        data["hourly"][hour]["total_good"] += temp_total_good
        data["hourly"][hour]["total_expected"] += temp_total_expected
        data["hourly"][hour]["total_ideal_run_time"] += temp_ideal_run_time
        data["hourly"][hour]["total_actual_run_time"] += temp_actual_run_time
        data["hourly"][hour]["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
        data["hourly"][hour]["total_total_downtime_seconds"] += temp_total_downtime_seconds

    for wc, data in workcell_data.items():
        final_OEE_per_Day.append({
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
            "hourly": [
                round(
                    ((float(data["hourly"][m]["total_good"])*100 / float(data["hourly"][m]["total_expected"]))
                    *(float(data["hourly"][m]["total_ideal_run_time"])*100 / float(data["hourly"][m]["total_actual_run_time"]))
                    *((float(data["hourly"][m]["total_planned_production_time_seconds"]) - float(data["hourly"][m]["total_total_downtime_seconds"]))*100 / float(data["hourly"][m]["total_planned_production_time_seconds"])))
                      /10000, 2)
                if  data["hourly"][m]["total_expected"] > 0 and data["hourly"][m]["total_actual_run_time"] > 0 and data["hourly"][m]["total_planned_production_time_seconds"] > 0 
                else 0
                for m in range(1, 25)
            ]
        })


    return jsonify({"Oee_per_Day": final_OEE_per_Day})
