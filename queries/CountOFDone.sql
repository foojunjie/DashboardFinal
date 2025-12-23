select
    CAST(DeliveryOrder.DateCreated as date) as DateCreated,
    count(deliveryOrder.id) as OrderFulFill
from deliveryOrder
left join DeliveryOrderItem on DeliveryOrderItem.DeliveryOrderId = DeliveryOrder.id
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId = DeliveryOrder.id
left join CustomerOrderItem on CustomerOrderItem.id = CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId
left join CustomerOrder on CustomerOrder.id = CustomerOrderItem.CustomerOrderId
where
    DeliveryOrder.DateCreated >= ?
and DeliveryOrder.DateCreated <= ?
group by CAST(DeliveryOrder.DateCreated as date)
