DROP TABLE IF EXISTS gold.outliers_iqr;
CREATE TABLE gold.outliers_iqr AS
with q as (
select
	city,
	PERCENTILE_CONT(0.25) within group (order by price_sqm) as q1,
	PERCENTILE_CONT(0.75) within group (order by price_sqm) as q3
from gold.housing_valid
group by 1
)
select
hv.*
from gold.housing_valid hv  
join q using (city)
where hv.price_sqm < (q.q1 - 1.5*(q.q3 - q.q1))
or hv.price_sqm > (q.q1 + 1.5*(q.q3 - q.q1))