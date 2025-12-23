select
    jtc."jtc_CONumber",
    sum(jtc."jtc_quantityCompleted") AS TotalCompleted,
    SUM(
        CASE 
            WHEN 
                jtc."jtc_actualEndDate" is null or jtc."jtc_actualStartDate" is null
            THEN jtc."jtc_quantityCompleted"
            ELSE 0
        END
    ) AS MissingProduce,
    jtc_workcell.name
from jtc
LEFT JOIN jtc_output_cycle ON jtc.jtc_id = jtc_output_cycle.jtc_id
LEFT JOIN jtc_station ON jtc_output_cycle.station_id = jtc_station.id
LEFT JOIN jtc_workcell ON jtc_workcell.id = jtc_station.workcell_id
where 
    extract(day from jtc."jtc_actualEndDate") = %s
    and extract(month from jtc."jtc_actualEndDate") = %s
    and extract(year from jtc."jtc_actualEndDate") = %s
group by jtc."jtc_CONumber", jtc_workcell.name