WITH downtime_periods AS (
  SELECT 
    ats.station_id,
    ats.jtc_id,
    ats.anomaly_timestamp AS downtime_start,
    LEAD(ats.anomaly_timestamp) OVER (PARTITION BY ats.station_id, ats.jtc_id ORDER BY ats.anomaly_timestamp) AS downtime_end,
    (ats.ms_flag AND ats.me_flag AND ats.mc_flag AND ats.mp_flag AND ats.bt_flag AND ats.qc_flag) AS all_flags_true,
    js.cycle_time
  FROM jtc_anomaly_timeslot ats
  JOIN jtc_station js ON ats.station_id = js.id
  WHERE anomaly_timestamp >= %s::date 
  AND anomaly_timestamp < (%s::date + INTERVAL '1 day')
),
calculated_downtime AS (
  SELECT 
    station_id,
    SUM(EXTRACT(EPOCH FROM (downtime_end - downtime_start))) AS total_downtime_seconds
  FROM downtime_periods
  WHERE all_flags_true = false
    AND downtime_end IS NOT NULL
    AND EXTRACT(EPOCH FROM (downtime_end - downtime_start)) < (cycle_time * 50)
  GROUP BY station_id
),
first_output_cycle AS (
  SELECT station_id, jtc_id, MIN(start_ts) AS first_start_ts
  FROM jtc_output_cycle
  WHERE start_ts >= %s::date 
  AND start_ts < (%s::date + INTERVAL '1 day')
  GROUP BY station_id, jtc_id
),
last_output_cycle AS (
  SELECT station_id, jtc_id, MAX(end_ts) AS last_end_ts
  FROM jtc_output_cycle
  WHERE end_ts >= %s::date 
  AND end_ts < (%s::date + INTERVAL '1 day')
  GROUP BY station_id, jtc_id
),
first_leak_test AS (
  SELECT station_id, jtc_id, MIN(modified_at) AS first_modified_at
  FROM leak_test_log
  WHERE modified_at >= %s::date 
  AND modified_at < (%s::date + INTERVAL '1 day')
  GROUP BY station_id, jtc_id
),
last_leak_test AS (
  SELECT station_id, jtc_id, MAX(modified_at) AS last_modified_at
  FROM leak_test_log
  WHERE modified_at >= %s::date 
  AND modified_at < (%s::date + INTERVAL '1 day')
  GROUP BY station_id, jtc_id
),
-- ... (Keep downtime_periods, calculated_downtime, and first/last cycle CTEs as they are)

station_metrics AS (
  SELECT 
    jtc_station.id,
    jtc_station.name,
    jtc_station.workcell_id,
    jtc_station.zone,
    jtc_station.cycle_time,
    jtc_station.is_leaktest,

    jtc_station.cycle_time * SUM(CASE 
                                    WHEN jtc_action_timeslot.quantity_completed > 0 
                                    AND CASE 
                                        WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                                        ELSE foc.first_start_ts
                                    END IS NOT NULL
                                    AND CASE 
                                        WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                                        ELSE loc.last_end_ts
                                    END IS NOT NULL
                                    AND EXTRACT(EPOCH FROM (
                                        CASE 
                                            WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                                            ELSE loc.last_end_ts
                                        END - 
                                        CASE 
                                            WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                                            ELSE foc.first_start_ts
                                        END)) < 86400
                                    AND EXTRACT(EPOCH FROM (
                                        CASE 
                                            WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                                            ELSE loc.last_end_ts
                                        END - 
                                        CASE 
                                            WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                                            ELSE foc.first_start_ts
                                        END)) > 0
                                    THEN jtc_action_timeslot.quantity_completed 
                                    ELSE 0 
                                 END) AS idealruntime,
	SUM(CASE 
          WHEN jtc_action_timeslot.quantity_completed > 0 
          AND CASE 
              WHEN jtc_station.is_leaktest THEN flt.first_modified_at
              ELSE foc.first_start_ts
          END IS NOT NULL
          AND CASE 
              WHEN jtc_station.is_leaktest THEN llt.last_modified_at
              ELSE loc.last_end_ts
          END IS NOT NULL
          AND EXTRACT(EPOCH FROM (
              CASE 
                  WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                  ELSE loc.last_end_ts
              END - 
              CASE 
                  WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                  ELSE foc.first_start_ts
              END)) < 86400
          AND EXTRACT(EPOCH FROM (
              CASE 
                  WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                  ELSE loc.last_end_ts
              END - 
              CASE 
                  WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                  ELSE foc.first_start_ts
              END)) > 0
          THEN EXTRACT(EPOCH FROM (
              CASE 
                  WHEN jtc_station.is_leaktest THEN llt.last_modified_at
                  ELSE loc.last_end_ts
              END - 
              CASE 
                  WHEN jtc_station.is_leaktest THEN flt.first_modified_at
                  ELSE foc.first_start_ts
              END))
          ELSE 0 
       END) AS actualruntime,
    -- QUALITY COMPONENT
    SUM(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN jtc_action_timeslot.quantity_completed ELSE 0 END) AS totalgood,
    (COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) * 50) AS totalexpected,

    -- AVAILABILITY COMPONENT
    (jtc_station.cycle_time * COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) * 50) as planned_production_time_seconds

  FROM jtc_station
  LEFT JOIN jtc_action_timeslot ON jtc_station.id = jtc_action_timeslot.atc_station_id
  LEFT JOIN first_output_cycle foc ON jtc_station.id = foc.station_id AND jtc_action_timeslot.jtc_id = foc.jtc_id
  LEFT JOIN last_output_cycle loc ON jtc_station.id = loc.station_id AND jtc_action_timeslot.jtc_id = loc.jtc_id
  LEFT JOIN first_leak_test flt ON jtc_station.id = flt.station_id AND jtc_action_timeslot.jtc_id = flt.jtc_id
  LEFT JOIN last_leak_test llt ON jtc_station.id = llt.station_id AND jtc_action_timeslot.jtc_id = llt.jtc_id
  WHERE jtc_station.workcell_id is not null
  and atc_timestamp_start >= %s::date 
  AND atc_timestamp_start < (%s::date + INTERVAL '1 day')
  and atc_timestamp_end >= %s::date 
  AND atc_timestamp_end < (%s::date + INTERVAL '1 day')
  GROUP BY jtc_station.id, jtc_station.name, jtc_station.workcell_id, jtc_station.zone, jtc_station.cycle_time, jtc_station.is_leaktest
)

SELECT 
  sm.id,
  sm.name,
  sm.idealruntime,
  sm.actualruntime,
  sm.totalgood,
  sm.totalexpected,
  sm.planned_production_time_seconds,
  cd.total_downtime_seconds
FROM station_metrics sm
LEFT JOIN calculated_downtime cd ON sm.id = cd.station_id;