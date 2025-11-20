SELECT 
        Product.Name, 
        Product.PartNumber, 
        SUM(CASE WHEN stock.Type = 1 THEN stock.Quantity ELSE 0 END) AS stockIn, 
        COUNT(CASE WHEN stock.Type = 1 THEN 1 END) AS stockInTimes,
        SUM(CASE WHEN stock.Type = 0 THEN stock.Quantity ELSE 0 END) AS stockOut,
        COUNT(CASE WHEN stock.Type = 0 THEN 1 END) AS stockOutTimes,
        COALESCE(Job.OrderNumber, DeliveryOrder.OrderNumber) AS DocStockOut
      FROM Product
      LEFT JOIN stock ON stock.ProductId = Product.id
      LEFT JOIN job ON Product.Id = job.ProductId
      LEFT JOIN DeliveryOrderItem ON DeliveryOrderItem.ProductId = Product.Id
      LEFT JOIN DeliveryOrder ON DeliveryOrderItem.DeliveryOrderId = DeliveryOrder.Id
      WHERE Product.PartNumber IN (
        :MATERIALS
      )
      AND Stock.LocationId IN (17,18)
      AND MONTH(stock.DateCreated) = ?
      AND YEAR(stock.DateCreated) = ?
      AND CAST(stock.DateCreated AS DATE) = CAST(CONCAT(?,'-',?,'-',?) AS DATE)
      GROUP BY Product.Name, Product.PartNumber, COALESCE(Job.OrderNumber, DeliveryOrder.OrderNumber);