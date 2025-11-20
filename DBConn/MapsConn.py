import pyodbc

def get_sql_conn():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=10.0.100.15\\SQLEXPRESS;"
        "DATABASE=avelon-yollink;"
        "UID=sa;"
        "PWD=sa@123;"
        "TrustServerCertificate=yes;"
    )
    return conn

def run_sql_query(query, params=()):
    conn = get_sql_conn()
    cursor = conn.cursor()

    cursor.execute(query, params)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    conn.close()

    return [dict(zip(columns, row)) for row in rows]