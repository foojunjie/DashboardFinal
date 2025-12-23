select
    delivery_instruction.purchase_schedule,
    delivery_instruction.Quantity as PlanQty,
    delivery_instruction.version
from delivery_instruction
where 
    extract(day from delivery_instruction.date_commit) = %s
    and extract(month from delivery_instruction.date_commit) = %s
    and extract(year from delivery_instruction.date_commit) = %s