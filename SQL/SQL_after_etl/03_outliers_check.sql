create or replace view housing_outliers as
WITH outliers AS (
	SELECT
		city,
		PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY area_sqm) AS q1,
		PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY area_sqm) AS q3
	FROM housing_standarized
	group by 
	city
)
SELECT
hs.*
FROM housing_standarized hs
JOIN outliers USING(city)
where hs.area_sqm < (outliers.q1 - 1.5*(outliers.q3 - outliers.q1))
or hs.area_sqm > (outliers.q1 + 1.5*(outliers.q3 - outliers.q1))
