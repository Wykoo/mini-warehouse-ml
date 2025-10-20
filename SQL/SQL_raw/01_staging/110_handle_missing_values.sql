create or replace view silver.housing_typed as
WITH src AS (     
  SELECT
    listing_id,
    date,
    city,
    district,
    postal_code,
    NULLIF(REPLACE(rooms::text,              ',', ''), '')::numeric                 AS rooms_num,
    NULLIF(REPLACE(area_sqm::text,           ',', ''), '')::numeric                 AS area_num,
    NULLIF(REPLACE(floor::text,              ',', ''), '')::numeric                 AS floor_num,
    NULLIF(REPLACE(total_floors::text,       ',', ''), '')::numeric                 AS total_floors_num,
    NULLIF(REPLACE(year_built::text,         ',', ''), '')::numeric                 AS year_num,
    NULLIF(REPLACE(distance_center_km::text, ',', ''), '')::numeric                 AS dist_num,
    CASE
      WHEN has_elevator IS NULL THEN NULL
      WHEN has_elevator::int = 1 THEN 1
      WHEN has_elevator::int = 0 THEN 0
      ELSE NULL
    END AS has_elevator_int,
    price_sqm,
    price_total
  FROM bronze.housing_raw
),
median_calc AS(
	select
		PERCENTILE_CONT(0.5) within group (order by rooms_num) as median_rooms,
		PERCENTILE_CONT(0.5) within group (order by area_num) as median_area,
		PERCENTILE_CONT(0.5) within group (order by floor_num) as median_floors,
		PERCENTILE_CONT(0.5) within group (order by total_floors_num) as median_floors_total,
		PERCENTILE_CONT(0.5) within group (order by year_num) as median_year,
		PERCENTILE_CONT(0.5) within group (order by dist_num) as median_distance
	from src
)
SELECT
  s.listing_id,
  s.date,
  s.city,
  s.district,
  COALESCE(s.rooms_num,            m.median_rooms)        AS rooms,             
  COALESCE(s.area_num,             m.median_area)         AS area_sqm,          
  COALESCE(s.floor_num,            m.median_floors)        AS floor,             
  COALESCE(s.total_floors_num,     m.median_floors_total) AS total_floors,      
  COALESCE(s.year_num,             m.median_year)         AS year_built,        
  COALESCE(s.dist_num,             m.median_distance)         AS distance_center_km,
  COALESCE(
    CASE WHEN s.has_elevator_int = 1 THEN TRUE
         WHEN s.has_elevator_int = 0 THEN FALSE
         ELSE NULL END,
    TRUE  
  ) AS has_elevator,
  s.postal_code,
  s.price_sqm,
  s.price_total
FROM src s
CROSS JOIN median_calc m;




