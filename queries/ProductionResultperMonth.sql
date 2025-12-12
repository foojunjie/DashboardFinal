SELECT 
    SUM(
        CASE 
            WHEN 
                jtc."jtc_actualEndDate"   <= jtc."jtc_estEndDate"
                AND jtc."jtc_actualStartDate" <= jtc."jtc_estStartDate"
            THEN jtc."jtc_quantityCompleted"
            ELSE 0
        END
    ) AS onTimeProduce,
    SUM(
        CASE 
            WHEN 
                jtc."jtc_actualEndDate"   > jtc."jtc_estEndDate"
                OR  jtc."jtc_actualStartDate" > jtc."jtc_estStartDate"
            THEN jtc."jtc_quantityCompleted"
            ELSE 0
        END
    ) AS lateProduce,
    jtc."jtc_CONumber"
FROM jtc
WHERE jtc."jtc_PartNumber" = %s
group by jtc."jtc_CONumber";;
