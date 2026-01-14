from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_Zone_per_Month = Blueprint("OEE_by_Zone_per_Month", __name__)

@OEE_by_Zone_per_Month.route("/api/OEE_by_Zone_per_Month", methods=["GET"])
def get_OEE_by_Zone_per_Month():
    today = date.today()
    this_month = today.month
    this_year = today.year

    final = []
    zone_data = {}

    if this_month == 1 or this_month == 3 or this_month == 5 or this_month == 7 or this_month == 8 or this_month == 10 or this_month == 12:
        max_day = 32
    elif this_month == 2:
        if this_year % 4 == 0:
            max_day = 30
        else:
            max_day = 29
    else:
        max_day = 31

    with open("queries/WorkcellZoneStation.sql", "r") as f:
        sql = f.read()
    workcells = run_query(sql, ())

    for row in workcells:
        workcell = row["name"]
        workcellID = row["workcellid"]
        zone = row["zone"]
        stationID = row["stationid"]

        if workcell not in zone_data:
            zone_data[workcell] = {}

        if zone not in zone_data[workcell]:
            zone_data[workcell][zone] = {
                "stations": [stationID],  # list of station IDs
                "workcellID": workcellID,
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
        else:
            zone_data[workcell][zone]["stations"].append(stationID)

    # ---- Load SQL ----
    with open("queries/OEEbyStationPerDetails.sql", "r") as f:
            sql_month = f.read()

    oee_per_month = run_query(sql_month, ())

    for r in oee_per_month:
        stationid = r["id"]
        stationDay = r["day"]
        stationMonth = r["month"]
        stationYear = r["year"]
        temp_total_good = r["totalgood"] or 0
        temp_total_expected = r["totalexpected"] or 0
        temp_ideal_run_time = r["idealruntime"] or 0
        temp_actual_run_time = r["actualruntime"] or 0
        temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
        temp_total_downtime_seconds = r["total_downtime_seconds"] or 0

        if temp_total_expected == 0 or temp_ideal_run_time == 0 or temp_actual_run_time == 0 \
           or temp_planned_production_time_seconds == 0 or temp_total_downtime_seconds > temp_planned_production_time_seconds:
            continue

        for wc, zones in zone_data.items():
            for zone, data in zones.items():
                if stationid in data["stations"] and stationMonth == this_month and stationYear == this_year:
                    data["total_good"] += temp_total_good
                    data["total_expected"] += temp_total_expected
                    data["total_ideal_run_time"] += temp_ideal_run_time
                    data["total_actual_run_time"] += temp_actual_run_time
                    data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                    data["total_total_downtime_seconds"] += temp_total_downtime_seconds
                
        for day in range(1, max_day):
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

            for wc, zones in zone_data.items():
                for zone, data in zones.items():
                    if stationid in data["stations"] and stationDay == day and stationMonth == this_month and stationYear == this_year:
                        m = data["weekly"][week]
                        m["total_good"] += temp_total_good
                        m["total_expected"] += temp_total_expected
                        m["total_ideal_run_time"] += temp_ideal_run_time
                        m["total_actual_run_time"] += temp_actual_run_time
                        m["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                        m["total_total_downtime_seconds"] += temp_total_downtime_seconds

    # Build final list
    final = []
    for wc, zones in zone_data.items():
        for zone, data in zones.items():
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
            weekly_oee = []
            for m in range(1, 6):
                md = data["weekly"][m]
                if md["total_expected"]>0 and md["total_actual_run_time"]>0 and md["total_planned_production_time_seconds"]>0:
                    q = min(max(float(md["total_good"]) * 100 / float(md["total_expected"]), 0), 100)
                    p = min(max(float(md["total_ideal_run_time"]) * 100 / float(md["total_actual_run_time"]), 0), 100)
                    a = min(max((float(md["total_planned_production_time_seconds"]) - float(md["total_total_downtime_seconds"])) * 100 / float(md["total_planned_production_time_seconds"]), 0), 100)
                    weekly_oee.append(round(q * p * a / 10000, 2))
                else:
                    weekly_oee.append(0)

            final.append({
                "workcell": wc,
                "workcellID": data["workcellID"],
                "zone": zone,
                "oee": oee,
                "quality": quality,
                "performance": performance,
                "availability": availability,
                "weekly": weekly_oee
            })

    return jsonify({"Oee_per_Month": final})


