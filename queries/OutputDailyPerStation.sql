select 
    station_id,
    jtc_output_cycle.jtc_id,
    start_ts,
	end_ts,
    count(end_ts) as output_done,
    duration,
    cycle_time as ideal_duration,
    "jtc_quantityNeeded"
from jtc_output_cycle
join jtc_station on jtc_station.id = jtc_output_cycle.station_id
join jtc on jtc.jtc_id = jtc_output_cycle.jtc_id
WHERE start_ts::date = CURRENT_DATE
group by station_id, jtc_output_cycle.jtc_id, start_ts, end_ts, cycle_time,  "jtc_quantityNeeded", duration