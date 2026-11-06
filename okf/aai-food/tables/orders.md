---
type: PostgreSQL Table
title: orders
description: One row per customer order placed on the Aai-Food Delivery app (October 2026).
resource: postgresql://localhost/aai_food/public/orders
tags: [table, orders, core]
timestamp: 2026-11-01T10:00:00Z
---

# Summary

One row per customer order placed on the app. Each order comes from one
[restaurant](/tables/restaurants.md), is either Delivered or Cancelled, and records money,
rider, distance, weather and the customer's rating. 734 orders, 1–31 October 2026.

# Schema

| Column | Type | Nullable | Description | Sample values |
|--------|------|----------|-------------|---------------|
| order_id | text (PK) | No | Unique order ID, increases in time order | ORD100001, ORD100734 |
| customer_id | text | No | The customer who placed the order | CUST0001, CUST0400 |
| restaurant_id | text (FK) | No | Restaurant that prepared the food → [restaurants](/tables/restaurants.md) | R001, R018 |
| city | text | No | City where the order was placed | Pune, Mumbai, Bengaluru |
| order_placed_at | timestamp | No | When the customer placed the order (IST, no timezone) | 2026-10-01 09:52:35 |
| order_delivered_at | timestamp | **Yes** | When the order reached the customer (IST). NULL for cancelled orders | 2026-10-01 10:16:35 |
| status | text | No | Final order status | Delivered, Cancelled |
| order_value_inr | integer | No | Food value in rupees, before discount | 86 … 1389 |
| delivery_fee_inr | integer | No | Delivery fee charged in rupees (0 when order_value_inr >= 499) | 0, 25, 30, 35, 40 |
| discount_inr | integer | No | Discount given in rupees | 0, 30, 50, 75, 100 |
| payment_method | text | No | How the customer paid | UPI, Card, Wallet, Cash on Delivery |
| rider_id | text | **Yes** | Rider who delivered. NULL for cancelled orders | RD001 … RD060 |
| distance_km | numeric(3,1) | No | Restaurant to customer distance in km | 1.0 … 8.5 |
| weather | text | No | Weather in that city at order time | Clear, Rain, Heavy Rain |
| customer_rating | smallint | **Yes** | Customer's rating of the order, 1–5 stars. NULL for cancelled orders | 1 … 5 |

# Allowed values

Values are **case-sensitive**. Use these exact spellings in SQL:

- `status`: `'Delivered'`, `'Cancelled'`
- `weather`: `'Clear'`, `'Rain'`, `'Heavy Rain'`
- `payment_method`: `'UPI'`, `'Card'`, `'Wallet'`, `'Cash on Delivery'`
- `city`: `'Pune'`, `'Mumbai'`, `'Bengaluru'` (not "Bangalore", not "Bombay")

# Joins

- `orders.restaurant_id = restaurants.restaurant_id` → [restaurants](/tables/restaurants.md)
  (use this to get restaurant name, cuisine or area).

# Gotchas

- **There is NO delivery time column.** Calculate it from the two timestamps, see
  [delivery_time](/metrics/delivery_time.md). For "late" orders see
  [late_delivery_rate](/metrics/late_delivery_rate.md).
- **Cancelled orders** have NULL `order_delivered_at`, NULL `rider_id` and NULL `customer_rating`.
  Exclude them (`status = 'Delivered'`) from delivery time, late rate and revenue.
- Timestamps are **local India time (IST)** stored without a timezone. Do not convert them.
- Use **`order_placed_at`** for all date filters ("in October", "last Friday", "per day").
- Data covers **October 2026 only** (2026-10-01 to 2026-10-31).
- Revenue rules are in [net_revenue](/metrics/net_revenue.md). Rain effects are in
  [heavy_rain](/playbooks/heavy_rain.md).

# Example queries

Orders by city and status:

```sql
SELECT city, status, COUNT(*) AS orders
FROM orders
GROUP BY city, status
ORDER BY city, status;
```

Delivered orders in Pune on a single day (filter on order_placed_at):

```sql
SELECT COUNT(*) AS delivered_orders
FROM orders
WHERE city = 'Pune'
  AND status = 'Delivered'
  AND order_placed_at >= '2026-10-15'
  AND order_placed_at <  '2026-10-16';
```
