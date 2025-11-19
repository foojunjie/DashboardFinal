from flask import Blueprint, jsonify
from DBConn.MapsConn import run_sql_query
from DBConn.ejtcConn import run_query
from datetime import date

parts_liveE24 = Blueprint("parts_liveE24", __name__)

@parts_liveE24.route("/api/parts_liveE24", methods=["GET"])
def get_parts_liveE24():
    today = date.today()

    this_month = today.month
    this_year = today.year
    this_day = today.day

    with open("queries/productE240100WF.sql", "r") as f:
        sql = f.read()

    productE24 = run_query(sql, ())

    materials = [row["jtc_material"] for row in productE24]

    # load sql file
    with open("queries/StockInOutPerParts.sql", "r") as f:
        sql = f.read()

    placeholders = ",".join("?" for _ in materials)
    sql = sql.replace(":MATERIALS", placeholders)
    params = (*materials, this_month, this_year, this_year, this_month, this_day)

    output_this_month = run_sql_query(sql, params)

    with open("queries/QuantityPerParts.sql", "r") as f:
        sql = f.read()

    placeholders = ",".join("?" for _ in materials)
    sql = sql.replace(":MATERIALS", placeholders)
    params = (*materials,)
    output_quantity = run_sql_query(sql, params)

    # return both sets
    return jsonify({
        "productE24": productE24,
        "this_month": output_this_month,
        "quantity": output_quantity
    })
