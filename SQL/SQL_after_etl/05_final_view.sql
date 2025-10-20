DROP TABLE IF EXISTS housing_final_tab;

CREATE TABLE housing_final_tab as
select
*
from housing_clean
where 
valid_floor = 1 