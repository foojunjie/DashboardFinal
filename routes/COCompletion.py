from flask import Blueprint, jsonify, request
from DBConn.MapsConn import run_sql_query
from DBConn.ejtcConn import run_query
from datetime import date, timedelta, datetime, time
from datetime import datetime as _dt
from flask import current_app as app
from collections import defaultdict

COCompletion = Blueprint("COCompletion", __name__)

@COCompletion.route("/api/COCompletion", methods=["GET"])
def get_COCompletion():
    today = date.today()
    
    this_day = today.day
    this_month = today.month
    this_year = today.year

    iso = today.isoweekday()
    start_of_week = today - timedelta(days=iso - 1)
    end_of_week = start_of_week + timedelta(days=6)

    totalmiss1 = 0
    totaltargetfrommaps = 0
    totalmiss2 = 0
    totaltargetfromjtc = 0
    finaltotalmiss = 0
    finaltotaltarget = 0
    finaldailyoutput = 0
    totaldelivery = 0
    totaldeliverytarget = 0
    finaldailyship = 0

    version = 0
    i = 0

    dailyOutput = {}
    dailyShip = {}

    weeklyproducefromjtc = []
    weeklyproducefrommaps = []
    weekly_result = []

    with open("queries/dailyOutputFromMaps.sql", "r") as f:
        sql = f.read()

    outputFromMaps = run_sql_query(sql, (this_day, this_month, this_year))

    with open("queries/dailyOutputFromJTC.sql", "r") as f:
        sql = f.read()

    outputFromJTC = run_query(sql, (this_day, this_month, this_year))

    for row in outputFromMaps:
        miss1 = row.get("MissingProduce") or 0
        totaltarget1 = row.get("TotalTarget") or 0

        totalmiss1 += miss1
        totaltargetfrommaps += totaltarget1

    for row in outputFromJTC:
        miss2 = row.get("MissingProduce") or 0
        totaltarget2 = row.get("TotalTarget") or 0

        totalmiss2 += miss2
        totaltargetfromjtc += totaltarget2

    finaltotalmiss = totalmiss1 + totalmiss2
    finaltotaltarget = totaltargetfrommaps + totaltargetfromjtc
    finaldailyoutput = "{:.2f}".format((finaltotaltarget - finaltotalmiss)*100/(finaltotaltarget))

    dailyOutput = {"dailyOutput":finaldailyoutput}
    
    with open("queries/dailyShip.sql", "r") as f:
        sql = f.read()

    deliver = run_sql_query(sql, (this_day, this_month, this_year))

    with open("queries/dailyShipTarget.sql", "r") as f:
        sql = f.read()

    delivertarget = run_query(sql, (this_day, this_month, this_year))

    # Build lookup from B (deliver)
    deliver_map = defaultdict(int)

    for row in deliver:
        po = row.get("PONumber")
        deliver_map[po] += row.get("DeliverQuantity", 0)

    # LEFT JOIN A with B (exclude purchase_schedule in output)
    merged = []

    for row in delivertarget:
        po = row.get("purchase_schedule")

        target_qty = row.get("quantity", 0)
        delivered_qty = deliver_map.get(po, 0)

        merged.append({
            "TargetQuantity": target_qty,
            "DeliverQuantity": delivered_qty
        })

    for row in merged:
        delivery = row.get("DeliverQuantity", 0)
        deliverytarget = row.get("TargetQuantity", 0)

        totaldelivery += delivery
        totaldeliverytarget += deliverytarget

    if totaldeliverytarget > 0:
        finaldailyship = "{:.2f}".format(totaldelivery * 100 / totaldeliverytarget)
    else:
        finaldailyship = "0.00"

    dailyShip = {"dailyship": finaldailyship}

    with open("queries/OutputByWeekfromJTC.sql", "r") as f:
        sql = f.read()   

    weeklyoutputfromjtc = run_query(sql, (start_of_week, end_of_week))

    with open("queries/OutputByWeekfromMaps.sql", "r") as f:
        sql = f.read()   

    weeklyoutputfrommaps = run_sql_query(sql, (start_of_week, end_of_week))

    with open("queries/ShippedByWeek.sql","r") as f:
        sql = f.read()

    weeklyship = run_sql_query(sql,(start_of_week, end_of_week))

    with open("queries/CountOFDone.sql","r") as f:
        sql = f.read()
    
    countofdone = run_sql_query(sql,(start_of_week, end_of_week))

    for row in weeklyoutputfromjtc:
        weeklymiss1 = row.get("MissingProduce") or 0
        weeklytotal1 = row.get("TotalTarget") or 0
        weeklydate1 = row.get("jtc_estEndDate")

        weeklyproduce1 = weeklytotal1 - weeklymiss1

        weeklyproducefromjtc.append({
            "date": weeklydate1,
            "produce": weeklyproduce1,
            "WIP":weeklymiss1
        })

    for row in weeklyoutputfrommaps:
        weeklymiss2 = row.get("MissingProduce") or 0
        weeklytotal2 = row.get("TotalTarget") or 0
        weeklydate2 = row.get("EstEndDate")

        weeklyproduce2 = weeklytotal2 - weeklymiss2

        weeklyproducefrommaps.append({
            "date": weeklydate2,
            "produce": weeklyproduce2,
            "WIP":weeklymiss2
        })

    produce_map = defaultdict(int)
    wip_map = defaultdict(int)
    ship_map = defaultdict(int)
    of_map = defaultdict(int)

    # Add JTC data
    for row in weeklyproducefromjtc:
        produce_map[row["date"]] += row["produce"]
        wip_map[row["date"]] += row["WIP"]

    # Add MAPS data
    for row in weeklyproducefrommaps:
        produce_map[row["date"]] += row["produce"]
        wip_map[row["date"]] += row["WIP"]

    # weeklyship: [{DateCreated, DeliverQuantity}]
    for row in weeklyship:
        ship_map[row["DateCreated"]] += row.get("DeliverQuantity", 0)

    # weeklyship: [{DateCreated, OrderFulfill}]
    for row in countofdone:
        of_map[row["DateCreated"]] += row.get("OrderFulFill", 0)

    current_date = start_of_week
    while current_date <= end_of_week:
        produce = produce_map.get(current_date, 0)
        delivered = ship_map.get(current_date, 0)
        order_fulfill = of_map.get(current_date, 0)
        wip = wip_map.get(current_date, 0)

        weekly_result.append({
            "date": current_date,
            "produce": produce,
            "DeliverQuantity": delivered,
            "WIP": wip,
            "OrderFulfill": order_fulfill
        })

        current_date += timedelta(days=1)

    with open("queries/COCompletionFromMaps.sql", "r") as f:
        sql = f.read()   

    cocompletionfrommaps = run_sql_query(sql, ())

    with open("queries/COCompletionFromMapsWithJob.sql", "r") as f:
        sql = f.read()   

    cocompletionfrommapswithjob = run_sql_query(sql, ())

    with open("queries/COCompletionFromJTC.sql", "r") as f:
        sql = f.read()   

    cocompletionfromjtc = run_query(sql, (this_day, this_month, this_year))

    with open("queries/PlanQty.sql", "r") as f:
        sql = f.read()   

    planqty = run_query(sql, (this_day, this_month, this_year))

    cocompletionfrommaps_map = {r["PONumber"]: r for r in cocompletionfrommaps}
    cocompletionfrommapswithjob_map = {r["PONumber"]: r for r in cocompletionfrommapswithjob}

    # D joins to B via orderNumber
    cocompletionfromjtc_map = {}
    for r in cocompletionfromjtc:
        order_no = r.get("CONumber")
        if order_no:
            cocompletionfromjtc_map.setdefault(order_no, []).append(r)

    final_result = []

    while i < len(planqty):
        row = planqty[i]
        ver = row.get("version") or 0
        if ver >= version:
            version = ver
            i=i+1
            continue
        else:
            planqty.pop(i)

    for a in planqty:
        po = a.get("purchase_schedule")

        row = {
            **a,
            "CO": None,
            "Part": None,
            "Workcell": None,
            "COQty": None,
            "CarryForward": None,
            "Output": None,
            "ShippedQty": None,
            "WIPQty": None,
            "BalQty": None,
            "OrderFulfill": None
        }

        # ---- A → B (priority) ----
        if po in cocompletionfrommaps_map:
            b = cocompletionfrommaps_map[po]
            row["CO"] = "orderNumber"
            row["Part"] = "PartNumber"
            row["COQty"] = "OrderQuantity"
            row["ShippedQty"] = "DeliverQuantity"
            row["OrderFulfill"] = "OrderFulFill"

            # ---- B → D ----
            order_no = b.get("orderNumber")
            if order_no and order_no in cocompletionfromjtc_map:
                row["Output"] = "TotalCompleted"
                row["Workcell"] = "name"
                row["WIPQty"] = "MissingProduce"

        # ---- A → C (fallback) ----
        elif po in cocompletionfrommapswithjob_map:
            c = cocompletionfrommapswithjob_map[po]
            row["CO"] = "orderNumber"
            row["Part"] = "PartNumber"
            row["COQty"] = "OrderQuantity"
            row["ShippedQty"] = "DeliverQuantity"
            row["Output"] = "CompletedQuantity"
            row["WIPQty"] = "MissingProduce"
            row["OrderFulfill"] = "OrderFulFill"

        # ---- No match ----
        else:
            continue

        final_result.append(row)

    # return both sets
    return jsonify({
        "dailyOutput": dailyOutput,
        "dailyShip": dailyShip,
        "weeklyResult": weekly_result,
        "COCompletion": final_result
    })
