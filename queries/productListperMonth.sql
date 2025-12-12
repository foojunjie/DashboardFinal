select
    customer_part_num, customer_code
from delivery_instruction
where extract(month from delivery_instruction.date_commit) = %s
and extract(year from delivery_instruction.date_commit) = %s
group by customer_part_num, customer_code
