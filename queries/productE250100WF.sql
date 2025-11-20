SELECT jtc_material
FROM public.jtc_bom_insyi
WHERE "product_PartNumber" IN ('E25-0100-WF')
and "isDefault" is true
group by jtc_material;