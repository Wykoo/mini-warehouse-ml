-- File: 010_schema_overview.sql
-- Author: Mateusz
-- Purpose: Discovery – Checking whole table schema housing_raw
-- Date: 2025-10-09

SELECT column_name, data_type, is_nullable
from information_schema.columns
where table_schema = 'bronze' and table_name = 'housing_raw'
order by
ordinal_position

select count(*) as n_rows
from bronze.housing_raw

select * from bronze.housing_raw 
limit(10);