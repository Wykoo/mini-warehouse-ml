create or replace view gold.housing_valid as
select
*
from gold.housing_features
where invalid_floor_flag = false
and rooms > 0