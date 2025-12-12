select date_commit, purchase_schedule, customer_code, quantity as target_quantity, created_at, version
from delivery_instruction
where EXTRACT(MONTH FROM date_commit) = %s
and EXTRACT(YEAR FROM date_commit) = %s
and customer_part_num = %s
group by purchase_schedule, date_commit, customer_code, target_quantity, created_at, version
order by date_commit;