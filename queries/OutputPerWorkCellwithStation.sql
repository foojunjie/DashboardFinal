WITH base AS (
    SELECT
        jtc."jtc_quantityCompleted",
        jtc."jtc_quantityNeeded",
        jtc."jtc_actualEndDate",
        jtc_workcell.name AS workcell,
        jtc_station.id AS station_id
    FROM jtc
    LEFT JOIN jtc_output_cycle 
        ON jtc_output_cycle.jtc_id = jtc.jtc_id
    LEFT JOIN jtc_station 
        ON jtc_station.id = jtc_output_cycle.station_id
    LEFT JOIN jtc_workcell 
        ON jtc_workcell.id = jtc_station.workcell_id
    WHERE jtc_workcell.name IS NOT NULL
    AND extract(day FROM jtc."jtc_actualEndDate") = %s
    AND extract(month FROM jtc."jtc_actualEndDate") = %s
    AND extract(year FROM jtc."jtc_actualEndDate") = %s
),
station_per_workcell AS (
    SELECT id AS station_id, workcell_id
    FROM jtc_station
),
expanded AS (
    SELECT
        b."jtc_quantityCompleted",
        b."jtc_quantityNeeded",
        b."jtc_actualEndDate",
        b.workcell,
        s.station_id,
        COUNT(b.station_id) FILTER (WHERE b.station_id = s.station_id) AS station_qty
    FROM base b
    JOIN station_per_workcell s
      ON s.workcell_id = (SELECT id FROM jtc_workcell WHERE name = b.workcell)
    GROUP BY 
        b."jtc_quantityCompleted",
        b."jtc_quantityNeeded",
        b."jtc_actualEndDate",
        b.workcell,
        s.station_id
),
pivot AS (
    SELECT
        "jtc_quantityCompleted",
        "jtc_quantityNeeded",
        "jtc_actualEndDate",
        workcell,
        jsonb_object_agg(
            'station' || station_id || '_qty',
            station_qty
        ) AS station_counts
    FROM expanded
    GROUP BY 
        "jtc_quantityCompleted",
        "jtc_quantityNeeded",
        "jtc_actualEndDate",
        workcell
)

SELECT 
    "jtc_quantityCompleted",
    "jtc_actualEndDate",
    workcell,
    station_counts
FROM pivot
ORDER BY "jtc_actualEndDate";
