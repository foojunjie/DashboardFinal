SELECT 
    SUM(
        CASE 
            WHEN 
                ActualEndDate is null or ActualStartDate is null
            THEN Quantity
            ELSE 0
        END
    ) AS MissingProduce,
    SUM( Quantity ) AS TotalTarget
FROM job
WHERE Day(EstEndDate)= ?
and Month (EstEndDate)= ?
and Year (EstEndDate)= ?