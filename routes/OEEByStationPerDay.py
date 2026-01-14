from flask import Blueprint, jsonify, request
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_Station_per_Day = Blueprint("OEE_by_Station_per_Day", __name__)

@OEE_by_Station_per_Day.route("/api/OEE_by_Station_per_Day", methods=["GET"])
def get_OEE_by_Station_per_Day():
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

    this_date = date(this_year, this_month, this_day)

    final = []
    station_data = {}

    with open("queries/WorkcellZoneStation.sql", "r") as f:
        sql = f.read()
    workcells = run_query(sql, ())

    for row in workcells:
        workcell = row["name"]
        workcellID = row["workcellid"]
        zone = row["zone"]
        stationID = row["stationid"]
        sequence = row["sequence"]

        if workcell not in station_data:
            station_data[workcell] = {}

        if zone not in station_data[workcell]:
            station_data[workcell][zone] = {}

        if stationID not in station_data[workcell][zone]:    
            station_data[workcell][zone][stationID] = {
                "name":" ",
                "workcellID": row["workcellid"],
                "sequence": row["sequence"],
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
                } for i in range(24)}
            }

    with open("queries/OEEbyStationPerDetails.sql", "r") as f:
        sql = f.read()

    Oee = run_query(sql, ())
        
    for r in Oee:
        stationID = r["id"]
        stationName = r["name"]
        stationHour = r["hour"] or 0
        stationDay = r["day"] or 0
        stationMonth = r["month"] or 0
        stationYear = r["year"] or 0
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
                if stationID in stations and stationDay == this_day and stationMonth == this_month and stationYear == this_year:   # only update the matching station
                    data = stations[stationID]
                    data["name"] = stationName
                    data["total_good"] += temp_total_good
                    data["total_expected"] += temp_total_expected
                    data["total_ideal_run_time"] += temp_ideal_run_time
                    data["total_actual_run_time"] += temp_actual_run_time
                    data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                    data["total_total_downtime_seconds"] += temp_total_downtime_seconds

        for i in range(24):
            for wc, zones in station_data.items():
                for zone, stations in zones.items():
                    if stationID in stations and stationHour == i and stationDay == this_day and stationMonth == this_month and stationYear == this_year:
                        data = stations[stationID]
                        m = data["hourly"][i]
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
                quality = min(max(round((float(data["total_good"]) * 100 / float(data["total_expected"])), 2), 0), 100) \
                        if data["total_expected"] > 0 else 0

                performance = min(max(round((float(data["total_ideal_run_time"]) * 100 / float(data["total_actual_run_time"])), 2), 0), 100) \
                            if data["total_actual_run_time"] > 0 else 0

                availability = min(max(round(((float(data["total_planned_production_time_seconds"]) - float(data["total_total_downtime_seconds"])) * 100 /
                                            float(data["total_planned_production_time_seconds"])), 2), 0), 100) \
                            if data["total_planned_production_time_seconds"] > 0 else 0

                oee = min(max(round((quality * performance * availability) / 10000, 2), 0), 100)

                # Monthly OEE
                hourly_oee = []
                for m in range(24):
                    md = data["hourly"][m]
                    if md["total_expected"] > 0 and md["total_actual_run_time"] > 0 and md["total_planned_production_time_seconds"] > 0:
                        q = min(max(float(md["total_good"]) * 100 / float(md["total_expected"]), 0), 100)
                        p = min(max(float(md["total_ideal_run_time"]) * 100 / float(md["total_actual_run_time"]), 0), 100)
                        a = min(max((float(md["total_planned_production_time_seconds"]) - float(md["total_total_downtime_seconds"])) * 100 /
                                    float(md["total_planned_production_time_seconds"]), 0), 100)
                        hourly_oee.append(round(q * p * a / 10000, 2))
                    else:
                        hourly_oee.append(0)

                final.append({
                    "workcell": wc,
                    "workcellID": data["workcellID"],
                    "sequence": data["sequence"],
                    "zone": zone,
                    "station": station,
                    "name":data["name"],
                    "oee": oee,
                    "quality": quality,
                    "performance": performance,
                    "availability": availability,
                    "hourly": hourly_oee
                })

    return jsonify({"Oee_per_Day": final})


