select
    jtc_station.is_running,
    jtc_station.id,
    jtc_workcell.name as workcell_name,
    jtc."jtc_orderNumber"
from jtc_station
left join jtc_workcell on jtc_workcell.id = jtc_station.workcell_id
left join jtc_output_cycle on jtc_output_cycle.station_id = jtc_station.id
left join jtc on jtc.jtc_id = jtc_output_cycle.jtc_id
where jtc_workcell.name is not null
and extract(day from jtc."jtc_actualEndDate") = %s
and extract(month from jtc."jtc_actualEndDate") = %s
and extract(year from jtc."jtc_actualEndDate") = %s
group by 
    jtc_station.is_running,
    jtc_station.id,
    jtc_workcell.name,
    jtc."jtc_orderNumber"
order by jtc_workcell.name, jtc_station.id