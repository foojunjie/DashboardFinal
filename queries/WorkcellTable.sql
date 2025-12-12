select
	jtc."jtc_orderNumber",
	jtc."jtc_quantityCompleted",
	jtc."jtc_actualEndDate",
	round("jtc_quantityCompleted"*100/"jtc_quantityNeeded",2) as yield,
	jtc_workcell.name
from jtc
left join jtc_output_cycle on jtc_output_cycle.jtc_id = jtc.jtc_id
left join jtc_station on jtc_station.id = jtc_output_cycle.station_id
left join jtc_workcell on jtc_workcell.id = jtc_station.workcell_id
where jtc_workcell.name is not null
and extract(day from jtc."jtc_actualEndDate") = %s
and extract(month from jtc."jtc_actualEndDate") = %s
and extract(year from jtc."jtc_actualEndDate") = %s
group by 
    jtc."jtc_orderNumber", 
    jtc."jtc_quantityCompleted", 
    jtc."jtc_actualEndDate", 
    "jtc_quantityNeeded", 
    jtc_workcell.name
order by jtc."jtc_actualEndDate"