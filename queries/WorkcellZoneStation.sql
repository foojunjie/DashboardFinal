SELECT
    jtc_workcell.name,
    jtc_station.zone,
    jtc_station.name as station,
    jtc_station.id as stationid
from jtc_station
left join jtc_workcell on jtc_workcell.id = jtc_station.workcell_id
order by jtc_workcell.id,jtc_station.zone,jtc_station.id