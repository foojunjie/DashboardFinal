from flask import Blueprint, jsonify, request
from DBConn.MapsConn import run_sql_query
from DBConn.ejtcConn import run_query
from datetime import date, timedelta, datetime, time
from datetime import datetime as _dt
from flask import current_app as app

summaryCO = Blueprint("summaryCO", __name__)

@summaryCO.route("/api/summaryCO", methods=["GET"])
def get_summaryCO():
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

    updatedProductList = []
    
    yamaha_new_part_number = None
    original_part_number = None
    yamaha_map = {}

    Target = 0
    OnTimeProduce = 0
    LateProduce = 0
    OnTimeDeliver = 0
    LateDeliver = 0
    MonthlyCO = 0
    MonthlyProduction = 0

    version = 0
    i = 0

    with open("queries/productListperMonth.sql", "r") as f:
        sql = f.read()

    productList = run_query(sql, (this_month, this_year))

    # --- Find all Yamaha rows ---
    yamaha_rows = [x for x in productList if x["customer_code"] == "46829-P"]

    if yamaha_rows:
        # keep first Yamaha original part for backward compatibility
        original_part_number = yamaha_rows[0]["customer_part_num"]

        # load the changeYamahaPartNum.sql once
        with open("queries/changeYamahaPartNum.sql", "r") as f:
            yamaha_sql = f.read()

        # Build mapping for each Yamaha original part
        for r in yamaha_rows:
            old_part = r["customer_part_num"]
            # query SQL Server for this old part
            res = run_sql_query(yamaha_sql, (old_part,))
            if res and "partnumber" in res[0] and res[0]["partnumber"]:
                yamaha_map[old_part] = res[0]["partnumber"]

        # set yamaha_new_part_number for the original_part_number (if mapping exists)
        if original_part_number in yamaha_map:
            yamaha_new_part_number = yamaha_map[original_part_number]

    # --- Build updatedProductList: apply mapping to all Yamaha rows ---
    updatedProductList = []
    for row in productList:
        if row["customer_code"] == "46829-P":
            old = row.get("customer_part_num")
            if old in yamaha_map:
                row["customer_part_num"] = yamaha_map[old]
        updatedProductList.append(row)

    partNumber = request.args.get("partNumber")
    print("Selected Part Number:", partNumber)

    if not partNumber:
        return jsonify({
            "productList": updatedProductList,
            "mergedOutput": None
        })

    with open("queries/ProductionResultperMonth.sql", "r") as f:
        sql = f.read()

    Result = run_query(sql, (partNumber,))

    partNumberDI = None
    if partNumber == yamaha_new_part_number:
        partNumberDI = original_part_number
    else:
        partNumberDI = partNumber

    with open("queries/dateCommitList.sql", "r") as f:
        sql = f.read()   

    dateCommitList = run_query(sql, (this_month, this_year, partNumberDI))

    while i < len(dateCommitList):
        row = dateCommitList[i]
        ver = row.get("version") or 0
        if ver >= version:
            version = ver
            i=i+1
            continue
        else:
            dateCommitList.pop(i)

    if partNumber == yamaha_new_part_number:
        with open("queries/DeliverOrderYamahaperMonth.sql", "r") as f:
            sql = f.read()

        result = run_sql_query(sql, (partNumber, this_month, this_year))

    else:
        with open("queries/DeliverOrderKoikeperMonth.sql", "r") as f:
            sql = f.read()

        result = run_sql_query(sql, (partNumber, this_month, this_year))

     # Build lookup maps
    result_by_po = {row["PONumber"]: row for row in result}  # For schedule join
    result_by_co = {row["jtc_CONumber"]: row for row in Result}  # JTC table

    merged_output = []

    for row in dateCommitList:  # LEFT JOIN base
        schedule = row.get("purchase_schedule")  # your matching key

        merged = row.copy()  # start with left dataset

        # ------------------------------
        # 1️⃣ LEFT JOIN result ON purchase_schedule = PONumber
        # ------------------------------
        do_row = result_by_po.get(schedule)

        if do_row:
            merged["DateCreated"] = do_row.get("DateCreated")
            merged["DeliverQuantity"] = do_row.get("DeliverQuantity")
            merged["PONumber"] = do_row.get("PONumber")
            merged["OrderNumber"] = do_row.get("OrderNumber")   # link to JTC
        else:
            merged["DateCreated"] = None
            merged["DeliverQuantity"] = 0
            merged["PONumber"] = None
            merged["OrderNumber"] = None

        customer_code = row.get("customer_code")
        if customer_code == "46829-P":
            # ------------------------------
            # 2️⃣ LEFT JOIN JTC Result ON OrderNumber = jtc_CONumber
            # ------------------------------
            order_num = merged.get("OrderNumber")
            jtc_row = result_by_co.get(order_num)

            if jtc_row:
                merged["onTimeProduce"] = jtc_row.get("onTimeProduce")
                merged["lateProduce"] = jtc_row.get("lateProduce")
            else:
                merged["onTimeProduce"] = 0
                merged["lateProduce"] = 0

            merged_output.append(merged)
        else:
            if do_row:
                merged["onTimeProduce"] = do_row.get("onTimeProduce")
                merged["lateProduce"] = do_row.get("lateProduce")
            else:
                merged["onTimeProduce"] = 0
                merged["lateProduce"] = 0
            
            merged_output.append(merged)

    for row in merged_output:

        target = row.get("target_quantity") or 0
        onTimeProduce = row.get("onTimeProduce") or 0
        lateProduce = row.get("lateProduce") or 0
        DeliverQuantity = row.get("DeliverQuantity") or 0

        dc = row.get("DateCreated")
        commit = row.get("date_commit")

        # Only compare if both dates exist
        if dc and commit:
            if dc <= commit:    # on time deliver
                OnTimeDeliver += DeliverQuantity
            else:
                LateDeliver += DeliverQuantity

        # accumulate totals
        Target += target
        OnTimeProduce += onTimeProduce
        LateProduce += lateProduce


    # --- Weekly calculations: filter merged_output for commits within this week ---
    iso = today.isoweekday()
    start_of_week = today - timedelta(days=iso - 1)
    end_of_week = start_of_week + timedelta(days=6)

    W_Target = 0
    W_OnTimeDeliver = 0
    W_LateDeliver = 0

    for row in merged_output:
        w_target = row.get("target_quantity") or 0
        w_DeliverQuantity = row.get("DeliverQuantity") or 0

        w_dc = row.get("DateCreated")
        w_commit = row.get("date_commit")

        in_week = False
        if w_commit:
            try:
                if w_commit >= start_of_week and w_commit <= end_of_week:
                    in_week = True
            except Exception:
                try:
                    parsed = _dt.fromisoformat(str(w_commit)).date()
                    if parsed >= start_of_week and parsed <= end_of_week:
                        in_week = True
                except Exception:
                    in_week = False

        if in_week:
            W_Target += w_target

            if w_dc and w_commit:
                try:
                    if w_dc <= w_commit:
                        W_OnTimeDeliver += w_DeliverQuantity
                    else:
                        W_LateDeliver += w_DeliverQuantity
                except Exception:
                    try:
                        parsed_dc = _dt.fromisoformat(str(w_dc)).date()
                        parsed_commit = _dt.fromisoformat(str(w_commit)).date()
                        if parsed_dc <= parsed_commit:
                            W_OnTimeDeliver += w_DeliverQuantity
                        else:
                            W_LateDeliver += w_DeliverQuantity
                    except Exception:
                        pass

    WeeklyCO = (W_OnTimeDeliver + W_LateDeliver) / W_Target * 100 if W_Target > 0 else 0
    
    MonthlyCO = (OnTimeDeliver + LateDeliver)/(Target)*100 if Target > 0 else 0
    MonthlyProduction = (OnTimeProduce + LateProduce)/(Target)*100 if Target > 0 else 0

    deliverResult = [OnTimeDeliver, LateDeliver]
    productionResult = [OnTimeProduce, LateProduce]
    target = [Target]
    monthlyCO = [MonthlyCO]
    monthlyProduction = [MonthlyProduction]
    weeklyCO = [WeeklyCO]

    def serialize_row(row):
        new_row = {}
        for k, v in row.items():
            if isinstance(v, (date, datetime, time)):
                new_row[k] = v.isoformat()
            else:
                new_row[k] = v
        return new_row

    merged_output = [serialize_row(r) for r in merged_output]

    # return both sets
    return jsonify({
        "productList": productList,
        "mergedOutput": merged_output,
        "deliverResult": deliverResult,
        "productionResult": productionResult,
        "target": target,
        "monthlyCO": monthlyCO,
        "monthlyProduction": monthlyProduction,
        "weeklyCO": weeklyCO
    })
