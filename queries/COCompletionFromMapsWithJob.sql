select
    CustomerOrder.orderNumber,
    Product.PartNumber,
    CustomerOrderItem.Quantity AS OrderQuantity,
    DeliveryOrderItem.Quantity AS DeliverQuantity,
    Job.Quantity AS CompletedQuantity,
    SUM(
        CASE 
            WHEN 
                ActualEndDate is null or ActualStartDate is null
            THEN job.Quantity
            ELSE 0
        END
    ) AS MissingProduce,
    CustomerOrder.PONumber,
    count(DeliveryOrder.id) as OrderFulFill
from CustomerOrder
left join CustomerOrderItem on CustomerOrder.Id = CustomerOrderItem.CustomerOrderId
left join Product on Product.Id = CustomerOrderItem.ProductId
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId = CustomerOrderItem.Id
left join DeliveryOrderItem on DeliveryOrderItem.Id = CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId
left join DeliveryOrder on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId
left join Job on Job.ProductId = Product.Id
group by 
    CustomerOrder.OrderNumber, 
    Product.PartNumber, 
    CustomerOrderItem.Quantity, 
    DeliveryOrderItem.Quantity, 
    Job.Quantity, 
    CustomerOrder.PONumber
