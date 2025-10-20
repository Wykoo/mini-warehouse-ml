CREATE OR REPLACE VIEW housing_clean as
with validation as(
	select
	listing_id,
	case	
		when floor > total_floors then 0
		else 1
	end valid_floor
	from housing_standarized
)
select
hs.*,
v.valid_floor
from housing_standarized hs
join validation v using(listing_id);