select
    DeliveryOrder.DateCreated,
    CustomerOrder.PONumber,
    DeliveryOrderItem.Quantity AS DeliverQuantity,
    CustomerOrder.OrderNumber,
    SUM(
        CASE 
            WHEN 
                Job.ActualEndDate   <= Job.EstEndDate
                AND Job.ActualStartDate <= Job.EstEndDate
            THEN Job.Quantity
            ELSE 0
        END
    ) AS onTimeProduce,
    SUM(
        CASE 
            WHEN 
                Job.ActualEndDate   > Job.EstEndDate
                OR  Job.ActualStartDate > Job.EstEndDate
            THEN Job.Quantity
            ELSE 0
        END
    ) AS lateProduce
from DeliveryOrder 
left join DeliveryOrderItem on DeliveryOrder.Id = DeliveryOrderItem.DeliveryOrderId 
left join product on product.id = DeliveryOrderItem.ProductId 
left join CustomerOrderItemDeliveryOrderItemLink on CustomerOrderItemDeliveryOrderItemLink.DeliveryOrderItemId = DeliveryOrderItem.Id
left join CustomerOrderItem on CustomerOrderItem.Id = CustomerOrderItemDeliveryOrderItemLink.CustomerOrderItemId 
left join CustomerOrder on CustomerOrder.Id = CustomerOrderItem.CustomerOrderId 
left join Job on Job.ProductId = product.Id
where 
    product.PartNumber = ? 
    and MONTH(DeliveryOrder.DateCreated) = ? 
    and YEAR(DeliveryOrder.DateCreated) = ? 
group by DeliveryOrder.DateCreated, CustomerOrder.PONumber, DeliveryOrderItem.Quantity, CustomerOrder.OrderNumber;