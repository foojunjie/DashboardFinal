SELECT 
    jtc_workcell.name,
	jtc_station.zone,
    jtc_station.is_running
FROM jtc
LEFT JOIN jtc_action_timeslot 
    ON jtc_action_timeslot.jtc_id = jtc.jtc_id
LEFT JOIN jtc_station 
    ON jtc_station.id = jtc_action_timeslot.atc_station_id
LEFT JOIN jtc_workcell 
    ON jtc_workcell.id = jtc_station.workcell_id
WHERE jtc_workcell.name IS NOT NULL
GROUP BY jtc_workcell.name, jtc_station.zone, jtc_station.is_running