BEGIN;

DROP TABLE IF EXISTS gold.housing_features;

CREATE TABLE gold.housing_features AS
with features as (
	select 
		case
			when invalid_floor_flag = False then ROUND((floor::float/nullif(total_floors::float, 0))::numeric, 3)
		else 0
		end as floor_ratio,
		(year_built/10)*10 AS decade,
		(extract(year from CURRENT_DATE) - year_built)::int 		as building_age,
		EXTRACT(year from listing_date)::int 						as listing_year,
		EXTRACT(month from listing_date)::int 						as listing_month,
		EXTRACT(day from listing_date)::int 						as listing_day,
		to_char(listing_date,'FMDay')			         			AS listing_day_of_week,
			
		CASE EXTRACT(MONTH FROM listing_date)::int
	      	WHEN 12 THEN 'Winter' 
	      	WHEN 1 THEN 'Winter' 	
	      	WHEN 2 THEN 'Winter'
	      	WHEN 3  THEN 'Spring' 
	      	WHEN 4 THEN 'Spring' 
	      	WHEN 5 THEN 'Spring'
	      	WHEN 6  THEN 'Summer' 
	      	WHEN 7 THEN 'Summer' 
	      	WHEN 8 THEN 'Summer'
	      	ELSE 'Autumn'
	    END AS season,
	    
	    CASE
	      WHEN area_sqm IS NULL   THEN 'unknown'
	      WHEN area_sqm < 35      THEN '<35'
	      WHEN area_sqm < 50      THEN '35-49'
	      WHEN area_sqm < 70      THEN '50-69'
	      WHEN area_sqm < 100     THEN '70-99'
	      ELSE '100+'
	    END AS area_sqm_bucket,
	    
	    CASE
	      WHEN distance_center_km IS NULL THEN 'unk'
	      WHEN distance_center_km < 1     THEN '<1'
	      WHEN distance_center_km < 3     THEN '1-2.9'
	      WHEN distance_center_km < 5     THEN '3-4.9'
	      WHEN distance_center_km < 10    THEN '5-9.9'
	      ELSE '10+'
	    END AS distance_km_bucket,
	    
	    CASE WHEN has_elevator THEN 1 ELSE 0 END      AS has_elevator_int,
	    listing_id
			
	from gold.clean
)
select 
gc.listing_id,
gc.listing_date,
f.season,
f.listing_year,
f.decade,
f.listing_month,
f.listing_day,
f.listing_day_of_week,
gc.city,
gc.district,
gc.postal_code,
gc.rooms,
gc.floor,
gc.total_floors,
f.floor_ratio,
gc.year_built,
f.building_age,
gc.area_sqm,
f.area_sqm_bucket,
gc.distance_center_km,
f.distance_km_bucket,
gc.price_sqm,
gc.price_total,
f.has_elevator_int,
gc.invalid_floor_flag

from gold.clean gc
JOIN features f USING (listing_id);

COMMIT;