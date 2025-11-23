create or replace view silver.housing_clean as
	select
	
    replace(listing_id::text, ',', '')::BIGINT           AS listing_id,
    NULLIF(TRIM("date"), '')::date                       AS listing_date,

    CASE WHEN city IS NULL OR TRIM(city) = '' 
         THEN NULL ELSE INITCAP(TRIM(city)) END          AS city,
         
    CASE WHEN district IS NULL OR TRIM(district) = '' 
         THEN NULL ELSE INITCAP(TRIM(district)) END      AS district,
         
    NULLIF(TRIM(postal_code), '')                        AS postal_code,

    rooms::int                                           AS rooms,
    floor::int                                           AS floor,
    total_floors::int                                    AS total_floors,
    REPLACE(year_built::text, ',', '')::int                    AS year_built,
    


    ROUND(area_sqm::numeric, 2)::numeric(12,2)           AS area_sqm,
    ROUND(distance_center_km::numeric, 2)::numeric(12,2) AS distance_center_km,


    (price_sqm::numeric)::numeric(18,2)                  AS price_sqm,
    (price_total::numeric)::numeric(18,2)                AS price_total,
    
	has_elevator


from silver.housing_typed;
