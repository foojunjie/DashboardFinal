from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_Station_per_Month = Blueprint("OEE_by_Station_per_Month", __name__)

@OEE_by_Station_per_Month.route("/api/OEE_by_Station_per_Month", methods=["GET"])
def get_OEE_by_Station_per_Month():
    today = date.today()
    this_month = today.month
    this_year = today.year

    final = []
    station_data = {}

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
        zone = row["zone"]
        stationID = row["stationid"]

        if workcell not in station_data:
            station_data[workcell] = {}

        if zone not in station_data[workcell]:
            station_data[workcell][zone] = {}

        if stationID not in station_data[workcell][zone]:    
            station_data[workcell][zone][stationID] = {
                "name":" ",
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

    # ---- Load SQL ----
    with open("queries/OEEbyStationPerMonth.sql", "r") as f:
            sql_month = f.read()

    oee_per_month = run_query(sql_month, ())

    for r in oee_per_month:
        stationID = r["id"]
        stationName = r["name"]
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

        for wc, zones in station_data.items():
            for zone, stations in zones.items():
                if stationID in stations and stationMonth == this_month and stationYear == this_year:   # only update the matching station
                    data = stations[stationID]
                    data["name"] = stationName
                    data["total_good"] += temp_total_good
                    data["total_expected"] += temp_total_expected
                    data["total_ideal_run_time"] += temp_ideal_run_time
                    data["total_actual_run_time"] += temp_actual_run_time
                    data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                    data["total_total_downtime_seconds"] += temp_total_downtime_seconds

    with open("queries/OEEbyStationPerDay.sql", "r") as f:
                sql_day = f.read()
                
    for day in range(1, max_day):

        this_date = date(this_year, this_month, day)

        oee_per_day = run_query(sql_day, (this_date, this_date, this_date, this_date, this_date, this_date, this_date,
                                            this_date, this_date, this_date, this_date, this_date, this_date, this_date))

        for r in oee_per_day:
            stationID = r["id"]
            temp_total_good = r["totalgood"] or 0
            temp_total_expected = r["totalexpected"] or 0
            temp_ideal_run_time = r["idealruntime"] or 0
            temp_actual_run_time = r["actualruntime"] or 0
            temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
            temp_total_downtime_seconds = r["total_downtime_seconds"] or 0

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

            if temp_total_expected == 0 or temp_ideal_run_time == 0 or temp_actual_run_time == 0 \
            or temp_planned_production_time_seconds == 0 or temp_total_downtime_seconds > temp_planned_production_time_seconds:
                continue

            for wc, zones in station_data.items():
                for zone, stations in zones.items():
                    if stationID in stations:   # only update the matching station
                        data = stations[stationID]
                        m = data["weekly"][week]
                        m["total_good"] += temp_total_good
                        m["total_expected"] += temp_total_expected
                        m["total_ideal_run_time"] += temp_ideal_run_time
                        m["total_actual_run_time"] += temp_actual_run_time
                        m["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                        m["total_total_downtime_seconds"] += temp_total_downtime_seconds

    # Build final list
    final = []
    for wc, workcells in station_data.items():
        for zone, zones in workcells.items():
            for station, data in zones.items():
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
                    "zone": zone,
                    "station": station,
                    "name":data["name"],
                    "oee": oee,
                    "quality": quality,
                    "performance": performance,
                    "availability": availability,
                    "weekly": weekly_oee
                })

    return jsonify({"Oee_per_Month": final})


