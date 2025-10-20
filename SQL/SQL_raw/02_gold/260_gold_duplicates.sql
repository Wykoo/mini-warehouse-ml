create or REPLACE view gold.duplicates as
SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY listing_id ORDER BY listing_date DESC) AS rn
  FROM gold.housing_features
) t
WHERE rn > 1;