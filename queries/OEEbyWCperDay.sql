WITH downtime_periods AS (
  SELECT 
    ats.station_id,
    ats.jtc_id,
    ats.anomaly_timestamp as downtime_start,
    LEAD(ats.anomaly_timestamp) OVER (PARTITION BY ats.station_id, ats.jtc_id ORDER BY ats.anomaly_timestamp) as downtime_end,
    (ats.ms_flag AND ats.me_flag AND ats.mc_flag AND ats.mp_flag AND ats.bt_flag AND ats.qc_flag) as all_flags_true,
    js.cycle_time
  FROM jtc_anomaly_timeslot ats
  JOIN jtc_station js ON ats.station_id = js.id
),
calculated_downtime AS (
  SELECT 
    station_id,
    SUM(EXTRACT(EPOCH FROM (downtime_end - downtime_start))) as total_downtime_seconds
  FROM downtime_periods
  WHERE all_flags_true = false
    AND downtime_end IS NOT NULL
    AND EXTRACT(EPOCH FROM (downtime_end - downtime_start)) < (cycle_time * 50)
  GROUP BY station_id
),
first_output_cycle AS (
  SELECT 
    station_id,
    jtc_id,
    MIN(start_ts) as first_start_ts
  FROM jtc_output_cycle
  GROUP BY station_id, jtc_id
),
last_output_cycle AS (
  SELECT 
    station_id,
    jtc_id,
    MAX(end_ts) as last_end_ts
  FROM jtc_output_cycle
  GROUP BY station_id, jtc_id
),
first_leak_test AS (
  SELECT 
    station_id,
    jtc_id,
    MIN(modified_at) as first_modified_at
  FROM leak_test_log
  GROUP BY station_id, jtc_id
),
last_leak_test AS (
  SELECT 
    station_id,
    jtc_id,
    MAX(modified_at) as last_modified_at
  FROM leak_test_log
  GROUP BY station_id, jtc_id
),
workcell_metrics AS (
  SELECT 
	jtc_workcell.id,
	jtc_workcell.name,
	jtc."jtc_actualEndDate" as actEndDate,
	SUM(CASE WHEN jtc."jtc_quantityCompleted" > 0 
		THEN jtc."jtc_quantityCompleted" ELSE 0 END) as TotalGood, 
	SUM(CASE WHEN jtc."jtc_quantityNeeded" > 0 THEN jtc."jtc_quantityNeeded" ELSE 0 END) as TotalExpected,
	SUM(CASE 
		WHEN jtc_action_timeslot.quantity_completed > 0 
		AND EXTRACT(EPOCH FROM (
			CASE WHEN jtc_station.is_leaktest THEN llt.last_modified_at ELSE loc.last_end_ts END - 
			CASE WHEN jtc_station.is_leaktest THEN flt.first_modified_at ELSE foc.first_start_ts END
		)) BETWEEN 1 AND 86399
		THEN jtc_station.cycle_time * jtc_action_timeslot.quantity_completed 
		ELSE 0 
	END) AS idealRunTime,
	SUM(CASE 
		WHEN jtc_action_timeslot.quantity_completed > 0 
		AND EXTRACT(EPOCH FROM (
			CASE WHEN jtc_station.is_leaktest THEN llt.last_modified_at ELSE loc.last_end_ts END - 
			CASE WHEN jtc_station.is_leaktest THEN flt.first_modified_at ELSE foc.first_start_ts END
		)) BETWEEN 1 AND 86399
		THEN EXTRACT(EPOCH FROM (
			CASE WHEN jtc_station.is_leaktest THEN llt.last_modified_at ELSE loc.last_end_ts END - 
			CASE WHEN jtc_station.is_leaktest THEN flt.first_modified_at ELSE foc.first_start_ts END
		))
		ELSE 0 
	END) AS actualRunTime,
	(jtc_station.cycle_time * COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) * 50) as planned_production_time_seconds
  From jtc
  LEFT JOIN jtc_action_timeslot 
  	ON jtc_action_timeslot.jtc_id = jtc.jtc_id
  LEFT JOIN jtc_station 
    ON jtc_station.id = jtc_action_timeslot.atc_station_id
  LEFT JOIN first_output_cycle foc
    ON jtc_station.id = foc.station_id 
    AND jtc_action_timeslot.jtc_id = foc.jtc_id
  LEFT JOIN last_output_cycle loc
    ON jtc_station.id = loc.station_id 
    AND jtc_action_timeslot.jtc_id = loc.jtc_id
  LEFT JOIN first_leak_test flt
    ON jtc_station.id = flt.station_id 
    AND jtc_action_timeslot.jtc_id = flt.jtc_id
  LEFT JOIN last_leak_test llt
    ON jtc_station.id = llt.station_id
	AND jtc_action_timeslot.jtc_id = llt.jtc_id
  left join jtc_workcell 
  	on jtc_workcell.id = jtc_station.workcell_id
  GROUP BY 
  	jtc_workcell.id,
    jtc_workcell.name,
	jtc."jtc_actualEndDate",
	jtc_station.cycle_time
)
SELECT 
  wm.id,
  wm.name,
  wm.actEndDate,
  wm.TotalGood,
  wm.TotalExpected,
  wm.idealRunTime,
  wm.actualRunTime,
  wm.planned_production_time_seconds,
  COALESCE(cd.total_downtime_seconds, 0) as total_downtime_seconds
FROM workcell_metrics wm
left join jtc_station on jtc_station.workcell_id = wm.id
LEFT JOIN calculated_downtime cd ON jtc_station.id = cd.station_id
where extract(day from wm.actEndDate) = %s
and extract(month from wm.actEndDate) = %s
and extract(year from wm.actEndDate) = %s
ORDER BY wm.id;