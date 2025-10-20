SELECT column_name, data_type, is_nullable
from information_schema.columns
where table_schema = 'public' and table_name = 'housing'
order by
ordinal_position;

create or REPLACE view housing_standarized as 
select 
replace(listing_id::text, ',', '')::BIGINT           	AS listing_id,
date::date                       						AS listing_date,
CASE WHEN city IS NULL OR TRIM(city) = '' 
         THEN NULL ELSE INITCAP(TRIM(city)) END         AS city,
CASE WHEN district IS NULL OR TRIM(district) = '' 
         THEN NULL ELSE INITCAP(TRIM(district)) END     AS district,
rooms::int 												as rooms,
floor::int 												as floor,
total_floors::int										as total_floors,
ROUND(area_sqm::numeric, 2)::numeric(12,2)           	AS area_sqm,
ROUND(distance_center_km::numeric, 2)::numeric(12,2) 	AS distance_center_km,
REPLACE(year_built::text, ',', '')::int                 AS year_built,
has_elevator,
(price_total::numeric)::numeric(18,2)                	AS price_total,
ROUND(floor_ratio::numeric, 2)::float					as floor_ratio,
age_years::int											as age_of_bulding,
year,
month,
day,
case
	when dow = 0 then 'Sunday'
	when dow = 1 then 'Monday'
	when dow = 2 then 'Tuesday'
	when dow = 3 then 'Wednesday'
	when dow = 4 then 'Thursday'
	when dow = 5 then 'Friday'
	when dow = 6 then 'Saturday'
end as dow
from housing;