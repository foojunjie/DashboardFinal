from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import datetime, timezone, timedelta

Track_Output_Quantity = Blueprint("Track_Output_Quantity", __name__)

@Track_Output_Quantity.route("/api/Track_Output_Quantity", methods=["GET"])
def get_Track_Output_Quantity():
    MY_TZ = timezone(timedelta(hours=8))
    today = datetime(2025, 12, 30, 18, 0, 0, tzinfo=MY_TZ)#.now(MY_TZ)

    remaining = False
    quantity_list = {}

    with open("queries/OutputDailyPerStation.sql", "r") as f:
        sql = f.read()
        
    status = run_query(sql, ())

    quantity_list = {}

    for row in status:
        stationid = row["station_id"]
        output_done = row["output_done"] or 0
        ideal_duration = row["ideal_duration"] or 0
        duration = row["duration"] or 0
        jtc_id = row["jtc_id"]
        quantityNeeded = row["jtc_quantityNeeded"] or 0
        start_time = row["start_ts"]
        end_time = row["end_ts"]

        if stationid not in quantity_list:
            quantity_list[stationid] = {}

        if jtc_id not in quantity_list[stationid]:
            quantity_list[stationid][jtc_id] = {
                "output_done": 0,
                "missed_quantity": 0,
                "start_time": start_time,
                "quantityNeeded": quantityNeeded,
                "hourly": {i: {"output_done": 0, "ideal_quantity": 0} for i in range(24)}
            }

        # Add total output_done for this JTC
        quantity_list[stationid][jtc_id]["output_done"] += output_done

        # Calculate ideal_quantity
        total_seconds = (today - start_time).total_seconds()
        ideal_quantity = min(round(total_seconds / ideal_duration, 2), quantityNeeded) if ideal_duration > 0 else 0
        quantity_list[stationid][jtc_id]["missed_quantity"] = max(0, ideal_quantity - quantity_list[stationid][jtc_id]["output_done"])

        worked_start_hour = quantity_list[stationid][jtc_id]["start_time"]
        for hour_number in range (24):
            if worked_start_hour.hour == hour_number:
                remaining_time = 3600 - (worked_start_hour.minute*60) - worked_start_hour.second
                ideal_quantity_hour = min(round(remaining_time/ideal_duration,2),quantity_list[stationid][jtc_id]["quantityNeeded"]) if ideal_duration > 0 else 0
                quantity_list[stationid][jtc_id]["hourly"][hour_number]["ideal_quantity"] = ideal_quantity_hour*ideal_duration
                if ideal_quantity_hour < quantity_list[stationid][jtc_id]["quantityNeeded"]:
                    remaining = True
            if end_time.hour == hour_number:
                quantity_list[stationid][jtc_id]["hourly"][hour_number]["output_done"] += duration
                if remaining is True:
                    quantity_list[stationid][jtc_id]["hourly"][hour_number]["ideal_quantity"] = quantity_list[stationid][jtc_id]["quantityNeeded"]*ideal_duration - quantity_list[stationid][jtc_id]["hourly"][hour_number - 1]["ideal_quantity"]
                    remaining = False

    final_list = {}
    for stationid, station in quantity_list.items():
        if stationid not in final_list:
            final_list[stationid] = {
                "missed_quantity": 0,
                "output_done": 0,
                "hourly": {i: {"output_done": 0, "ideal_quantity": 0} for i in range(24)}
            }
        for jtc_id, data in station.items():
            final_list[stationid]["missed_quantity"] += data["missed_quantity"]
            final_list[stationid]["output_done"] += data["output_done"]

            for hour in range(24):
                final_list[stationid]["hourly"][hour]["ideal_quantity"] += data["hourly"][hour]["ideal_quantity"]
                final_list[stationid]["hourly"][hour]["output_done"] += data["hourly"][hour]["output_done"]

    return jsonify({"Quantity": final_list}) 