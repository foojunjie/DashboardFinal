select
    sum(DeliveryOrderItem.Quantity) AS DeliverQuantity,
    CAST(DeliveryOrder.DateCreated as date) as DateCreated
from DeliveryOrder 
left join DeliveryOrderItem on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId
where 
    DeliveryOrder.DateCreated >= ?
and DeliveryOrder.DateCreated <= ?
group by DeliveryOrderItem.Quantity, CAST(DeliveryOrder.DateCreated as date);