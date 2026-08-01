# Reservation Metric Definitions

## reservation_users
Distinct users with a valid reservation.

## order_users
Distinct reservation users matched to an order for the same product and site inside the campaign conversion window.

## paid_users
Distinct reservation users whose matched order has final payment status SUCCESS.

## reservation_to_order_rate
order_users divided by reservation_users.

## reservation_to_payment_rate
paid_users divided by reservation_users.

## reserved_not_paid_users
Distinct reservation users whose paid_flag is zero. This includes users with no matched order and users whose matched order has a failed final payment status.
