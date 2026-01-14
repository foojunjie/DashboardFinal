from unittest import case
from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, timedelta, datetime
from flask import Blueprint, jsonify

UpTimeVSDownTime = Blueprint("UpTimeVSDownTime", __name__)

@UpTimeVSDownTime.route("/api/UpTimeVSDownTime", methods=["GET"])
def get_UpTimeVSDownTime():
    today = datetime.now()

    # For last 4 days uptime data (include today and previous 3 days)
    start_date = (today.date() - timedelta(days=3))

    # For last 4 hours data
    start_hour = today.hour - 4
    start_hour_date = today if start_hour >= 0 else today - timedelta(days=1)
    start_hour = start_hour if start_hour >= 0 else start_hour + 24

    # Today's date info
    today_day = today.day
    today_month = today.month
    today_year = today.year
    today_hour = today.hour

    # Start date (3 days ago) info for daily range comparisons
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year

    UpTimeVSDownTime = []
    workcell_data = {}
    station_down_list = {}

    with open("queries/WorkcellZoneStation.sql", "r") as f:
        sql = f.read()
    workcells = run_query(sql, ())

    for row in workcells:
        workcell = row["name"]
        zone = row["zone"]
        stationName = row["station"]
        stationID = row["stationid"]

        if workcell not in workcell_data:
            workcell_data[workcell] = {}

        if zone not in workcell_data[workcell]:
            workcell_data[workcell][zone] = {}
        
        if stationID not in workcell_data[workcell][zone]:
            workcell_data[workcell][zone][stationID] = {
                "stationName": stationName,
                "qc": 0,
                "mp": 0,
                "ms": 0,
                "mc": 0,
                "me": 0,
                "bt": 0,
                "daily": {i: {
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0
                } for i in range(1, 5)},
                "hourly": {i: {
                    "total_planned_production_time_seconds": 0,
                    "total_total_downtime_seconds": 0,
                    "qc": 0,
                    "mp": 0,
                    "ms": 0,
                    "mc": 0,
                    "me": 0,
                    "bt": 0,
                } for i in range(4)}
                }
        else:
            workcell_data[workcell][zone]["stations"].append(stationID)

    with open("queries/OEEbyStationPerDetails.sql", "r") as f:
        sql = f.read()

    uptimedata = run_query(sql, ())

    with open("queries/DownTime.sql", "r") as f:
        sql = f.read()

    downtimedata = run_query(sql, (today_day, today_month, today_year))
        
    for r in uptimedata:
        stationid = r["id"]
        stationName = r["name"]
        stationHour = r["hour"] or 0
        stationDay = r["day"] or 0
        stationMonth = r["month"] or 0
        stationYear = r["year"] or 0
        temp_planned_production_time_seconds = r["planned_production_time_seconds"] or 0
        temp_total_downtime_seconds = r["total_downtime_seconds"] or 0

        if temp_planned_production_time_seconds == 0 or temp_total_downtime_seconds > temp_planned_production_time_seconds:
            continue

        for wc, zones in workcell_data.items():
            for zone, stations in zones.items():
                # For daily uptime data - last 4 calendar days including today
                try:
                    station_date = date(stationYear, stationMonth, stationDay)
                    days_diff = (station_date - start_date).days
                except Exception:
                    days_diff = None

                if days_diff is not None and 0 <= days_diff < 4:
                    day_index = days_diff + 1  # keep existing 1..4 indexing
                    if stationid in stations:
                        data = stations[stationid]
                        data["stationName"] = stationName
                        m = data["daily"][day_index]
                        m["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                        m["total_total_downtime_seconds"] += temp_total_downtime_seconds

                # For hourly uptime data - last 4 hours
                if stationDay == today_day and stationMonth == today_month and stationYear == today_year:
                    if start_hour <= stationHour <= today_hour:
                        hour_index = stationHour - start_hour

                        if stationid in stations:
                            data = stations[stationid]
                            # Guard against out-of-range hour_index (should be 0..3)
                            if 0 <= hour_index < 4:
                                m = data["hourly"][hour_index]

                                m["total_planned_production_time_seconds"] += temp_planned_production_time_seconds
                                m["total_total_downtime_seconds"] += temp_total_downtime_seconds

    for r in downtimedata:
        qc_count = r["qc_flag"] or 0
        mp_count = r["mp_flag"] or 0
        ms_count = r["ms_flag"] or 0
        mc_count = r["mc_flag"] or 0
        me_count = r["me_flag"] or 0
        bt_count = r["bt_flag"] or 0
        stationid = r["station_id"]
        anomaly_hour = r["anomaly_timestamp"] or 0

        if qc_count is False or mp_count is False or ms_count is False or mc_count is False or me_count is False or bt_count is False:
            stationid_down = stationid
            if stationid_down not in station_down_list:
                station_down_list[stationid] = {
                    "down_anomaly_hour": anomaly_hour,
                    "qc": qc_count,
                    "mp": mp_count,
                    "ms": ms_count,
                    "mc": mc_count,
                    "me": me_count,
                    "bt": bt_count,
                }
            else:
                continue
            
            if qc_count is True or mp_count is True or ms_count is True or mc_count is True or me_count is True or bt_count is True and stationid in station_down_list:
                stationid_not_down = stationid
                if station_down_list[stationid]["qc"] is False:
                    qc_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
                if station_down_list[stationid]["mp"] is False:
                    mp_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
                if station_down_list[stationid]["ms"] is False:
                    ms_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
                if station_down_list[stationid]["mc"] is False:
                    mc_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
                if station_down_list[stationid]["me"] is False:
                    me_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
                if station_down_list[stationid]["bt"] is False:
                    bt_down_duration = anomaly_hour - station_down_list[stationid]["down_anomaly_hour"]
        else:
            continue

        for wc, zones in workcell_data.items():
                for zone, stations in zones.items():
                    if stationid_not_down in stations:
                        data = stations[stationid_not_down]
                        # Only count qc, mp, ms, mc, me, bt for today
                        data["qc"] += qc_down_duration
                        data["mp"] += mp_down_duration
                        data["ms"] += ms_down_duration
                        data["mc"] += mc_down_duration
                        data["me"] += me_down_duration
                        data["bt"] += bt_down_duration
                        # For hourly breakdown - last 4 hours only
                        if start_hour <= anomaly_hour <= today_hour:
                            hour_index = anomaly_hour - start_hour

                            # Guard against out-of-range hour_index (should be 0..3)
                            if 0 <= hour_index < 4:
                                data = stations[stationid_not_down]
                                m = data["hourly"][hour_index]

                                m["qc"] += qc_down_duration
                                m["mp"] += mp_down_duration
                                m["ms"] += ms_down_duration
                                m["mc"] += mc_down_duration
                                m["me"] += me_down_duration
                                m["bt"] += bt_down_duration

    for wc, workcells in workcell_data.items():
        for zone, zones in workcells.items():
            for station, data in zones.items():
                daily_uptime = []
                for m in range(1, 5):
                    md = data["daily"][m]
                    uptime = md["total_planned_production_time_seconds"] - md["total_total_downtime_seconds"]
                    performamce = min(max(round((uptime / md["total_planned_production_time_seconds"]) * 100, 2), 0), 100) if md["total_planned_production_time_seconds"] > 0 else 0
                    daily_uptime.append({
                    "uptime": uptime,
                    "performance": performamce
                })
                # Monthly OEE
                hourly_uptime = []
                for m in range(4):
                    md = data["hourly"][m]
                    uptime = md["total_planned_production_time_seconds"] - md["total_total_downtime_seconds"]
                    performamce = min(max(round((uptime / md["total_planned_production_time_seconds"]) * 100, 2), 0), 100) if md["total_planned_production_time_seconds"] > 0 else 0
                    hourly_uptime.append({
                        "uptime": uptime,
                        "performance": performamce,
                        "qc": md["qc"],
                        "mp": md["mp"],
                        "ms": md["ms"],
                        "mc": md["mc"],
                        "me": md["me"],
                        "bt": md["bt"],
                    })

                UpTimeVSDownTime.append({
                    "workcell": wc,
                    "zone": zone,
                    "station": station,
                    "name":data["stationName"],
                    "daily_uptime": daily_uptime,
                    "hourly_uptime": hourly_uptime,
                    "qc": data["qc"],
                    "mp": data["mp"],
                    "ms": data["ms"],
                    "mc": data["mc"],
                    "me": data["me"],
                    "bt": data["bt"],
                })

    return jsonify({"UptimeVSDownTime": UpTimeVSDownTime})
