from flask import Blueprint, jsonify
from DBConn.ejtcConn import run_query
from datetime import date, timedelta, datetime, time

JTCProgress = Blueprint("JTCProgress", __name__)

@JTCProgress.route("/api/JTCProgress", methods=["GET"])
def get_JTCProgress():
    today = date.today()

    first_day = today - timedelta(days=4)
    last_day = today
    progress_today = {}

    with open("queries/WorkcellZoneStation.sql", "r") as f:
        sql = f.read()
    workcells = run_query(sql, ())

    for row in workcells:
        stationID = row["stationid"]
        stationName = row["station"]

        if stationID not in progress_today:
            progress_today[stationID] = {
                "stationName": stationName
            }

    with open("queries/JTCNameAndOutput.sql", "r") as f:
        sql = f.read()
    progress = run_query(sql, (first_day, last_day))

    for r in progress:
        actualEndDate = r["jtc_actualEndDate"]
        orderNumber = r["jtc_orderNumber"]
        jtc_id = r["jtc_id"]
        stationID = r["id"]
        stationName = r["name"]
        quantity = r["quantity"]

        if actualEndDate.date() == today and jtc_id not in progress_today[stationID]:
            progress_today[stationID][jtc_id]= {
                "orderNumber": orderNumber,
                "stationName": stationName,
                "quantity": quantity
            }

    # return both sets
    return jsonify({
        "progress": progress,
        "progress_today": progress_today
    })
