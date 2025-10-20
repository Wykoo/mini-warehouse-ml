create or replace view gold.housing_invalid as
select
COUNT(*)
from gold.housing_features
where invalid_floor_flag = True
and rooms > 0