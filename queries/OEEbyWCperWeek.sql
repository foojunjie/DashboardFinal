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
station_metrics AS (
  SELECT 
    jtc_station.id,
    jtc_station.name,
    jtc_station.workcell_id,
    jtc_station.zone,
    jtc_station.cycle_time,
    jtc_station.unit_per_hour,
    jtc_station.is_leaktest,
    -- Quality calculation
    CASE 
        WHEN COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) > 0 
        THEN ROUND(
            (SUM(CASE WHEN jtc_action_timeslot.quantity_completed > 0 
                      THEN jtc_action_timeslot.quantity_completed ELSE 0 END)::NUMERIC / 
             (COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) * 50)::NUMERIC) * 100, 
            2
        )
        ELSE NULL
    END AS quality_percentage,
    -- Performance calculation (using first/last output cycle OR first/last leak test modified_at)
    CASE 
        WHEN SUM(CASE 
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
                 END) > 0
        THEN ROUND(
            ((jtc_station.cycle_time * SUM(CASE 
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
                                           END))::NUMERIC / 
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
                 END)::NUMERIC) * 100, 
            2
        )
        ELSE NULL
    END AS performance_percentage,
    -- Planned production time calculation
    (jtc_station.cycle_time * COUNT(CASE WHEN jtc_action_timeslot.quantity_completed > 0 THEN 1 END) * 50) as planned_production_time_seconds,
	"jtc_actualEndDate" as actEndDate, 
	jtc_workcell.name as workcell_name
  FROM jtc_station
  LEFT JOIN jtc_action_timeslot 
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
  left join jtc_output_cycle 
  	on jtc_output_cycle.station_id = jtc_station.id
  left join jtc 
  	on jtc.jtc_id = jtc_output_cycle.jtc_id
  GROUP BY 
    jtc_station.id,
    jtc_station.name,
    jtc_station.workcell_id,
    jtc_station.zone,
    jtc_station.cycle_time,
    jtc_station.unit_per_hour,
    jtc_station.is_leaktest,
	"jtc_actualEndDate", 
	jtc_workcell.name
)
SELECT 
  sm.workcell_id,
  sm.workcell_name,
  sm.actEndDate,
  round(avg(sm.quality_percentage),2) as quality_percentage,
  round(avg(sm.performance_percentage),2) as performance_percentage,
  -- Availability calculation
  CASE 
    WHEN sm.planned_production_time_seconds > 0 
    THEN round(avg(ROUND(
      ((sm.planned_production_time_seconds - COALESCE(cd.total_downtime_seconds, 0))::NUMERIC / 
       nullif(sm.planned_production_time_seconds::NUMERIC, 0)) * 100,
      2
    )),2)
    ELSE NULL
  END AS availability_percentage,
  -- OEE calculation (Availability × Performance × Quality)
  CASE 
    WHEN sm.quality_percentage IS NOT NULL 
    AND sm.performance_percentage IS NOT NULL
    AND sm.planned_production_time_seconds > 0
    THEN round(avg(ROUND(
      (CASE 
        WHEN sm.planned_production_time_seconds > 0 
        THEN ((sm.planned_production_time_seconds - COALESCE(cd.total_downtime_seconds, 0))::NUMERIC / 
             nullif(sm.planned_production_time_seconds::NUMERIC, 0)) * 100
        ELSE NULL
      END * sm.performance_percentage * sm.quality_percentage / 10000),
      2
    )),2)
    ELSE NULL
  END AS oee_percentage
FROM station_metrics sm
LEFT JOIN calculated_downtime cd ON sm.id = cd.station_id
where sm.actEndDate >= %s
and sm.actEndDate <= %s
group by 
sm.workcell_id, 
sm.workcell_name, 
sm.actEndDate, 
sm.planned_production_time_seconds, 
sm.quality_percentage, 
sm.performance_percentage, 
sm.id
ORDER BY sm.id;