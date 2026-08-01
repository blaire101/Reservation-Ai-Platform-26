# Table Dictionary

## dim_campaign
One row per campaign. Includes campaign name, product, site, reservation window, sale start, and conversion end time.

## dim_product
One row per product model. Includes product name, product category, and launch date.

## fact_reservation
One row per reservation event. Required keys: reservation_id, user_id, campaign_id, product_id, site, reservation_time.

## fact_order
One row per order. The MVP stores final payment outcome directly in payment_status and payment_time. A separate payment-attempt fact is future work.

## dm_reservation_conversion
One row per User × Campaign × Product × Site. A reservation is matched to the earliest order with the same user, product, and site where order_time is between sale_start_time and conversion_end_time.
