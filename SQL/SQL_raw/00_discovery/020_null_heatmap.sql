-- File: 020_null_heatmap.sql
-- Purpose: Counting all nulls in each housing_raw columns

SELECT
    COUNT(*) AS n_rows,
    COUNT(listing_id)     AS n_listing_id,
    COUNT(date)           AS n_date,
    COUNT(city)           AS n_city,
    COUNT(district)       AS n_district,
    COUNT(rooms)          AS n_rooms,
    COUNT(area_sqm)       AS n_area_sqm,
    COUNT(floor)          AS n_floor,
    COUNT(total_floors)   AS n_total_floors,
    COUNT(has_elevator)   AS n_has_elevator,
    COUNT(year_built)     AS n_year_built,
    COUNT(distance_center_km) AS n_distance_center_km,
    COUNT(postal_code)    AS n_postal_code,
    COUNT(price_sqm)      AS n_price_sqm,
    COUNT(price_total)    AS n_price_total
FROM bronze.housing_raw;
