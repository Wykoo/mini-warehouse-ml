DROP TABLE IF EXISTS gold.price_city_daily;
CREATE TABLE gold.price_city_daily AS
SELECT 
	listing_date AS d,
	city,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_sqm) AS median_sqm,
	PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price_sqm) AS p25_sqm,
	PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price_sqm) AS p75_sqm,
	COUNT(*) AS n_listings
FROM gold.housing_valid
GROUP BY
	1,2
order by 
	d desc
