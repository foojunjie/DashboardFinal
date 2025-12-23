select
    sum(DeliveryOrderItem.Quantity) AS DeliverQuantity,
    CustomerOrder.PONumber
from DeliveryOrder 
left join DeliveryOrderItem on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId = DeliveryOrderItem.Id
left join CustomerOrderItem on CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId = CustomerOrderItem.Id
left join CustomerOrder on CustomerOrder.id = CustomerOrderItem.CustomerOrderId
where 
    Day(DeliveryOrder.DateCreated) = ?
and MONTH(DeliveryOrder.DateCreated) = ? 
and YEAR(DeliveryOrder.DateCreated) = ?
group by CustomerOrder.PONumber