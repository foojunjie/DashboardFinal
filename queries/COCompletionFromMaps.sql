select
    CustomerOrder.orderNumber,
    Product.PartNumber,
    CustomerOrderItem.Quantity AS OrderQuantity,
    DeliveryOrderItem.Quantity AS DeliverQuantity,
    CustomerOrder.PONumber,
    count(DeliveryOrder.id) as OrderFulFill
from CustomerOrder
left join CustomerOrderItem on CustomerOrder.Id = CustomerOrderItem.CustomerOrderId
left join Product on Product.Id = CustomerOrderItem.ProductId
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId = CustomerOrderItem.Id
left join DeliveryOrderItem on DeliveryOrderItem.Id = CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId
left join DeliveryOrder on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId
group by 
    CustomerOrder.OrderNumber, 
    Product.PartNumber, 
    CustomerOrderItem.Quantity, 
    DeliveryOrderItem.Quantity,
    CustomerOrder.PONumber
