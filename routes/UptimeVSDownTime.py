from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime
from flask import Blueprint, jsonify, request

UpTimeVSDownTIme = Blueprint("UpTimeVSDownTIme", __name__)

@UpTimeVSDownTIme.route("/api/UpTimeVSDownTIme", methods=["GET"])
def get_UpTimeVSDownTIme():
    today = date.today()

    this_month = today.month
    this_year = today.year
    this_day = today.day

    this_date = datetime(this_year, this_month, this_day)

    final_OEE_per_Day = []
    workcell_data = {}

    with open("queries/WorkcellZoneStation.sql", "r") as f:
        sql = f.read()
    workcells = run_query(sql, ())

    for row in workcells:
        workcell = row["name"]
        stationID = row["stationid"]

        if workcell not in workcell_data:
            workcell_data[workcell] = {
                "stations": [stationID],  # list of station IDs
                "total_planned_production_time_seconds": 0,
                "total_total_downtime_seconds": 0}
        else:
            workcell_data[workcell]["stations"].append(stationID)

    with open("queries/OEEbyStationPerDay.sql", "r") as f:
        sql = f.read()

    Oee = run_query(sql, (this_date, this_date, this_date, this_date, this_date, this_date, this_date,
                            this_date, this_date, this_date, this_date, this_date, this_date, this_date))
        
    for r in Oee:
        stationid = r["id"]
        temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
        temp_total_downtime_seconds = r["total_downtime_seconds"] or 0

        if temp_planned_production_time_seconds == 0 or temp_total_downtime_seconds > temp_planned_production_time_seconds:
            continue

        for wc, data in workcell_data.items():
            if stationid in data["stations"]:
                data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                data["total_total_downtime_seconds"] += temp_total_downtime_seconds

    

    for wc, data in workcell_data.items():
        # Overall OEE
        quality = min(max(round((float(data["total_good"])*100 / float(data["total_expected"])), 2), 0), 100) \
          if data["total_expected"] > 0 else 0

        performance = min(max(round((float(data["total_ideal_run_time"])*100 / float(data["total_actual_run_time"])), 2), 0), 100) \
                    if data["total_actual_run_time"] > 0 else 0

        availability = min(max(round(((float(data["total_planned_production_time_seconds"]) - float(data["total_total_downtime_seconds"])) * 100 /
                            float(data["total_planned_production_time_seconds"])), 2), 0), 100) \
                    if data["total_planned_production_time_seconds"] > 0 else 0

        oee = round((quality * performance * availability) / 10000, 2)

        # Monthly OEE
        hourly_oee = []
        for m in range(1, 25):
            md = data["hourly"][m]
            if md["total_expected"]>0 and md["total_actual_run_time"]>0 and md["total_planned_production_time_seconds"]>0:
                q = min(max(float(md["total_good"]) * 100 / float(md["total_expected"]), 0), 100)
                p = min(max(float(md["total_ideal_run_time"]) * 100 / float(md["total_actual_run_time"]), 0), 100)
                a = min(max((float(md["total_planned_production_time_seconds"]) - float(md["total_total_downtime_seconds"])) * 100 / float(md["total_planned_production_time_seconds"]), 0), 100)
                hourly_oee.append(round(q * p * a / 10000, 2))
            else:
                hourly_oee.append(0)

        final_OEE_per_Day.append({
            "workcell": wc,
            "oee": oee,
            "quality": quality,
            "performance": performance,
            "availability": availability,
            "hourly": hourly_oee
        })

    return jsonify({"Oee_per_Day": final_OEE_per_Day})
