SELECT 
    SUM(
        CASE 
            WHEN 
                jtc."jtc_actualEndDate" is null or jtc."jtc_actualStartDate" is null
            THEN jtc."jtc_quantityCompleted"
            ELSE 0
        END
    ) AS MissingProduce,
    SUM( jtc."jtc_quantityCompleted" ) AS TotalTarget,
    jtc."jtc_estEndDate"::date as jtc_estEndDate
FROM jtc
WHERE jtc."jtc_estEndDate" >= %s
and jtc."jtc_estEndDate" <= %s
group by jtc."jtc_estEndDate"::date