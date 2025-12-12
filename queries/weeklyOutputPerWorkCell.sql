SELECT
    SUM(sub."jtc_quantityCompleted") AS total,
    SUM(sub."jtc_quantityNeeded") AS tarTotal,
    sub.workcell_id AS id,
    sub.workcell_name AS name
FROM (
    SELECT DISTINCT
        jtc.jtc_id,
        jtc."jtc_quantityCompleted",
        jtc."jtc_quantityNeeded",
        jtc_workcell.id AS workcell_id,
        jtc_workcell.name AS workcell_name
    FROM jtc
    LEFT JOIN jtc_output_cycle ON jtc.jtc_id = jtc_output_cycle.jtc_id
    LEFT JOIN jtc_station ON jtc_output_cycle.station_id = jtc_station.id
    LEFT JOIN jtc_workcell ON jtc_workcell.id = jtc_station.workcell_id
    WHERE DATE_TRUNC('week', jtc."jtc_actualEndDate") = DATE_TRUNC('week', %s)
      AND jtc_workcell.id IS NOT NULL
) AS sub
GROUP BY sub.workcell_id, sub.workcell_name
ORDER BY sub.workcell_id;
