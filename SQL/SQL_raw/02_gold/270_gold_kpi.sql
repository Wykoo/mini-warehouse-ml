CREATE OR REPLACE VIEW gold.kpi_overview AS
SELECT
  'ALL'::text AS city,
  COUNT(*) AS active_listings,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY price_sqm) AS median_ppsqm,
  AVG(building_age)::int AS avg_building_age,
  AVG(has_elevator_int)::numeric(5,2) AS share_elevator
FROM gold.housing_valid
UNION ALL
SELECT
  city,
  COUNT(*),
  percentile_cont(0.5) WITHIN GROUP (ORDER BY price_sqm),
  AVG(building_age)::int,
  AVG(has_elevator_int)::numeric(5,2)
FROM gold.housing_valid
GROUP BY city
ORDER BY city;