--Checkiing if every single null has been filled 
select 
	COUNT(*) as n_counts,
	COUNT(listing_id) as n_listings,
	COUNT(date) as n_dates,
	COUNT(city) as n_city,
	COUNT(district) as n_districts,
	COUNT(rooms) as n_rooms,
	COUNT(area_sqm) as n_areas,
	COUNT(floor) as n_floors,
	COUNT(total_floors) as n_total_floors,
	COUNT(has_elevator) as n_elevators,
	COUNT(year_built) as n_year_built,
	COUNT(distance_center_km) as n_distances,
	COUNT(postal_code) as n_postal_codes,
	COUNT(price_sqm) as n_prices_sqm,
	COUNT(age_years) as n_age_years_building,
	COUNT(floor_ratio) as n_floors_ratio,
	COUNT(year) as n_years,
	COUNT(month) as n_months,
	COUNT(day) as n_days,
	COUNT(dow) as n_dows
from housing;
--Looking for duplicates
select
* 
from(
	select 
		listing_id,
		row_number() over(partition by listing_id order by date DESC) as rn
	from housing
) t
where rn> 1;
--Looking for outliers
select
    MIN(rooms)              						AS min_rooms,
    MAX(rooms)              						AS max_rooms,
    ROUND(AVG(rooms)::numeric, 3)          			AS avg_rooms,
    ROUND(STDDEV(rooms)::numeric, 3)				as std_rooms,
    ROUND((AVG(rooms) - STDDEV(rooms))::numeric, 3) as min_deviation_rooms,
    ROUND((AVG(rooms) + STDDEV(rooms))::numeric, 3) as max_deviation_rooms,
   

    MIN(area_sqm)          									AS min_area,
    MAX(area_sqm)           								AS max_area,
    ROUND(AVG(area_sqm)::numeric, 3)           				AS avg_area,
    ROUND(STDDEV(area_sqm)::numeric, 3)						as avg_area,
    ROUND((AVG(area_sqm) - STDDEV(area_sqm))::numeric, 3) 	as min_deviation_area,
    ROUND((AVG(area_sqm) + STDDEV(area_sqm))::numeric, 3) 	as max_deviation_area,
    

    MIN(floor)              						AS min_floor,
    MAX(floor)              						AS max_floor,	
    ROUND(AVG(floor)::numeric, 3)					as avg_floor,
  	ROUND(STDDEV(floor)::numeric, 3)				as std_floor,
  	ROUND((AVG(floor) - STDDEV(floor))::numeric, 3) AS min_deviation_floor,
	ROUND((AVG(floor) + STDDEV(floor))::numeric, 3) AS max_deviation_floor,

    MIN(total_floors)       										AS min_total_floors,
    MAX(total_floors)       										AS max_total_floors,
    ROUND(AVG(total_floors)::numeric, 3)							as avg_total_floors,
  	ROUND(STDDEV(total_floors)::numeric, 3)							as std_total_floors,
  	ROUND((AVG(total_floors) - STDDEV(total_floors))::numeric, 3) 	AS min_deviation_total_floor,
	ROUND((AVG(total_floors) + STDDEV(total_floors))::numeric, 3) 	AS max_deviation_total_floor,

    MIN(year_built)         									AS min_year_built,
    MAX(year_built)         									AS max_year_built,
    ROUND(AVG(year_built)::numeric, 3)							as avg_year_built,
    ROUND(STDDEV(year_built)::numeric, 3)						as std_year_built,
   	ROUND((AVG(year_built) - STDDEV(year_built))::numeric, 3) 	AS min_deviation_year_built, 
   	ROUND((AVG(year_built) + STDDEV(year_built))::numeric, 3) 	AS max_deviation_year_built, 

    MIN(distance_center_km) 													AS min_distance_center,
    MAX(distance_center_km) 													AS max_distance_center,
    ROUND(AVG(distance_center_km)::numeric, 3) 									AS avg_distance_center,
    ROUND(STDDEV(distance_center_km)::numeric, 3) 								AS std_distance_center,
   	ROUND((AVG(distance_center_km) - STDDEV(distance_center_km))::numeric, 3) 	AS min_deviation_distance_center, 
   	ROUND((AVG(distance_center_km) + STDDEV(distance_center_km))::numeric, 3) 	AS max_deviation_distance_center, 

    MIN(price_sqm)          								AS min_price_sqm,
    MAX(price_sqm)          								AS max_price_sqm,
    ROUND(AVG(price_sqm)::numeric, 3)          				AS avg_price_sqm,
    ROUND(STDDEV(price_sqm)::numeric, 3)					as std_price_sqm,
    ROUND((AVG(price_sqm) - STDDEV(price_sqm))::numeric, 3) AS min_deviation_price_sqm, 
   	ROUND((AVG(price_sqm) + STDDEV(price_sqm))::numeric, 3) AS max_deviation_price_sqm, 

    MIN(price_total)        									AS min_price_total,
    MAX(price_total)        									AS max_price_total,
    ROUND(AVG(price_total)::numeric, 3)        					AS avg_price_total,
    ROUND(STDDEV(price_total)::numeric, 3)						as std_price_total,
    ROUND((AVG(price_total) - STDDEV(price_total))::numeric, 3) AS min_deviation_price_total, 
   	ROUND((AVG(price_total) + STDDEV(price_total))::numeric, 3) AS max_deviation_price_total    
from housing;
