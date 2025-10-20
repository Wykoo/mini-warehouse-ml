CREATE OR REPLACE VIEW gold.clean as

select
	*,
	CASE
		WHEN 
		floor is not null and 
		total_floors is not null AND
		floor > total_floors 
		THEN True
		else False
	end as invalid_floor_flag
		
FROM silver.housing_clean