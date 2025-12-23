SELECT 
    SUM(
        CASE 
            WHEN 
                ActualEndDate is null or ActualStartDate is null
            THEN Quantity
            ELSE 0
        END
    ) AS MissingProduce,
    SUM( Quantity ) AS TotalTarget,
    CAST(EstEndDate AS DATE) as EstEndDate
FROM job
WHERE EstEndDate >= ?
and EstEndDate <= ?
group by CAST(EstEndDate AS DATE)