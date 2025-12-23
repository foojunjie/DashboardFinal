SELECT 
    SUM(
        CASE 
            WHEN 
                jtc."jtc_actualEndDate" is null or jtc."jtc_actualStartDate" is null
            THEN jtc."jtc_quantityCompleted"
            ELSE 0
        END
    ) AS MissingProduce,
    SUM( jtc."jtc_quantityCompleted" ) AS TotalTarget
FROM jtc
WHERE extract (day from jtc."jtc_estEndDate" )= %s
and extract (month from jtc."jtc_estEndDate" )= %s
and extract (year from jtc."jtc_estEndDate" )= %s