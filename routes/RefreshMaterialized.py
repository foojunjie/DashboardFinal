from threading import Thread
from time import sleep
from datetime import datetime
from DBConn.ejtcConn import run_command

def refresh_worker():
    last_hour = None
    while True:
        now = datetime.now()
        if now.hour != last_hour:
            run_command("REFRESH MATERIALIZED VIEW public.oee_data_station;")
            run_command("REFRESH MATERIALIZED VIEW public.oee_data_station_in_details;")
            last_hour = now.hour
            print(f"Refreshed materialized view at {now}")
        else:
            print(f"No refresh needed at {now}")
        sleep(1800)
        

Thread(target=refresh_worker, daemon=True).start()
