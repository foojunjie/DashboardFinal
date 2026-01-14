SELECT
    jtc_workcell.name,
    jtc_workcell.id as workcellid,
    jtc_station.zone,
    jtc_station.name as station,
    jtc_station.id as stationid,
    jtc_station.sequence
from jtc_station
left join jtc_workcell on jtc_workcell.id = jtc_station.workcell_id
order by jtc_workcell.id,jtc_station.zone,jtc_station.id