-- Standardize Date Format
ALTER TABLE `sql-428610.DSFGDFG.hotel_booking`
ADD COLUMN arrival_date DATE;

UPDATE `sql-428610.DSFGDFG.hotel_booking`
SET arrival_date = DATE(arrival_date_year, arrival_date_month, arrival_date_day_of_month);

-- Populate missing data (if any)
UPDATE `sql-428610.DSFGDFG.hotel_booking` a
SET a.country = b.country
FROM `sql-428610.DSFGDFG.hotel_booking` b
WHERE a.country IS NULL
  AND a.market_segment = b.market_segment
  AND a.distribution_channel = b.distribution_channel
  AND b.country IS NOT NULL;

-- Breaking out meal into meal type and board basis
ALTER TABLE `sql-428610.DSFGDFG.hotel_booking`
ADD COLUMN meal_type STRING,
ADD COLUMN board_basis STRING;

UPDATE `sql-428610.DSFGDFG.hotel_booking`
SET meal_type = CASE
    WHEN meal = 'BB' THEN 'Breakfast'
    WHEN meal = 'HB' THEN 'Half Board'
    WHEN meal = 'FB' THEN 'Full Board'
    ELSE 'Unknown'
  END,
  board_basis = CASE
    WHEN meal = 'BB' THEN 'Bed & Breakfast'
    WHEN meal = 'HB' THEN 'Half Board'
    WHEN meal = 'FB' THEN 'Full Board'
    ELSE 'Unknown'
  END;

-- Standardize 'Yes' and 'No' values
UPDATE `sql-428610.DSFGDFG.hotel_booking`
SET is_repeated_guest = CASE 
    WHEN is_repeated_guest = 0 THEN 'No'
    WHEN is_repeated_guest = 1 THEN 'Yes'
    ELSE is_repeated_guest
  END;

-- Remove duplicates
WITH RowNumCTE AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY 
        hotel,
        arrival_date,
        adults,
        children,
        babies,
        meal,
        country,
        market_segment,
        reserved_room_type,
        assigned_room_type,
        deposit_type,
        customer_type
      ORDER BY name
    ) AS row_num
  FROM `sql-428610.DSFGDFG.hotel_booking`
)
DELETE FROM `sql-428610.DSFGDFG.hotel_booking`
WHERE name IN (
  SELECT name
  FROM RowNumCTE
  WHERE row_num > 1
);

-- Delete unused columns
ALTER TABLE `sql-428610.DSFGDFG.hotel_booking`
DROP COLUMN arrival_date_year,
DROP COLUMN arrival_date_month,
DROP COLUMN arrival_date_day_of_month,
DROP COLUMN meal;

-- Create a view for analysis
CREATE VIEW `sql-428610.DSFGDFG.vw_hotel_booking_analysis` AS
SELECT
  hotel,
  is_canceled,
  lead_time,
  arrival_date,
  stays_in_weekend_nights,
  stays_in_week_nights,
  adults + COALESCE(children, 0) + babies AS total_guests,
  meal_type,
  country,
  market_segment,
  distribution_channel,
  is_repeated_guest,
  reserved_room_type,
  assigned_room_type,
  booking_changes,
  deposit_type,
  days_in_waiting_list,
  customer_type,
  adr,
  required_car_parking_spaces,
  total_of_special_requests,
  reservation_status
FROM `sql-428610.DSFGDFG.hotel_booking`;
