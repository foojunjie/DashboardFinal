select
    jtc."jtc_orderNumber",
	jtc.jtc_id,
    jtc_station.id,
    jtc_station.name,
    count(jtc_output_cycle.end_ts) as quantity,
    jtc."jtc_quantityNeeded",
	jtc."jtc_actualEndDate"
from jtc
join jtc_output_cycle on jtc_output_cycle.jtc_id = jtc.jtc_id
join jtc_station on jtc_output_cycle.station_id = jtc_station.id
where jtc.jtc_id != 3150
AND jtc_output_cycle.end_ts >= %s
AND jtc_output_cycle.end_ts <= %s
group by jtc."jtc_orderNumber", jtc.jtc_id, jtc_station.id, jtc_station.name, jtc."jtc_quantityNeeded",	jtc."jtc_actualEndDate"