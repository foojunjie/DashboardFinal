SELECT 
        Product.Name, 
        Product.PartNumber, 
        SUM(CASE WHEN stock.Type = 1 THEN stock.Quantity ELSE 0 END) AS stockInAllTime,
        SUM(CASE WHEN stock.Type = 0 THEN stock.Quantity ELSE 0 END) AS stockOutAllTime
      FROM Product
      LEFT JOIN stock ON stock.ProductId = Product.id
      WHERE Product.PartNumber IN (
        :MATERIALS
      )
      AND Stock.LocationId IN (17,18)
      GROUP BY Product.Name, Product.PartNumber;