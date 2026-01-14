from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, datetime

OEE_by_Zone = Blueprint("OEE_by_Zone", __name__)

@OEE_by_Zone.route("/api/OEE_by_Zone", methods=["GET"])
def get_OEE_by_Zone():
    today = date.today()
    this_year = today.year

    zone_data = {}
    workcell_list = set()

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
                "stations": [stationID],
                "workcellID": workcellID,
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
        else:
            zone_data[workcell][zone]["stations"].append(stationID)

        workcell_list.add(workcell)
        # 🚩 Remove invalid None entries before sorting
        workcell_list.discard(None)

    with open("queries/OEEbyStation.sql", "r") as f:
        sql = f.read()
    Oee = run_query(sql, ())

    for r in Oee:
        stationid = r["id"]
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
                if stationid in data["stations"]:
                    data["total_good"] += temp_total_good
                    data["total_expected"] += temp_total_expected
                    data["total_ideal_run_time"] += temp_ideal_run_time
                    data["total_actual_run_time"] += temp_actual_run_time
                    data["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                    data["total_total_downtime_seconds"] += temp_total_downtime_seconds

    with open("queries/OEEbyStationPerDetails.sql", "r") as f:
        sql_month = f.read()

    oee_per_month = run_query(sql_month, ())

    for r in oee_per_month:
        stationid = r["id"]
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

        for month in range(1, 13):
            if stationYear == this_year and stationMonth == month:
                for wc, zones in zone_data.items():
                    for zone, data in zones.items():
                        if stationid in data["stations"]:
                            m = data["monthly"][month]
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
            monthly_oee = []
            for m in range(1, 13):
                md = data["monthly"][m]
                if md["total_expected"]>0 and md["total_actual_run_time"]>0 and md["total_planned_production_time_seconds"]>0:
                    q = min(max(float(md["total_good"]) * 100 / float(md["total_expected"]), 0), 100)
                    p = min(max(float(md["total_ideal_run_time"]) * 100 / float(md["total_actual_run_time"]), 0), 100)
                    a = min(max((float(md["total_planned_production_time_seconds"]) - float(md["total_total_downtime_seconds"])) * 100 / float(md["total_planned_production_time_seconds"]), 0), 100)
                    monthly_oee.append(round(q * p * a / 10000, 2))
                else:
                    monthly_oee.append(0)

            final.append({
                "workcell": wc,
                "workcellID": data["workcellID"],
                "zone": zone,
                "oee": oee,
                "quality": quality,
                "performance": performance,
                "availability": availability,
                "monthly": monthly_oee
            })

    return jsonify({"Oee": final, 
                    "List": sorted(list(workcell_list))})


