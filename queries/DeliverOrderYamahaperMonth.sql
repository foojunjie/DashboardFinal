select
    DeliveryOrder.DateCreated,
    CustomerOrder.PONumber,
    DeliveryOrderItem.Quantity AS DeliverQuantity,
    CustomerOrder.OrderNumber
from DeliveryOrder 
left join DeliveryOrderItem on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId 
left join product on product.id = DeliveryOrderItem.ProductId 
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId = DeliveryOrderItem.Id
left join CustomerOrderItem on CustomerOrderItem.Id = CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId 
left join CustomerOrder on CustomerOrder.Id = CustomerOrderItem.CustomerOrderId 
where 
    product.PartNumber = ? 
    and MONTH(DeliveryOrder.DateCreated) = ? 
    and YEAR(DeliveryOrder.DateCreated) = ? 
group by DeliveryOrder.DateCreated, CustomerOrder.PONumber, DeliveryOrderItem.Quantity, CustomerOrder.OrderNumber;