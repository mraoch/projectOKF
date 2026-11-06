---
type: Playbook
title: Heavy rain (rain surge)
description: What happens operationally during heavy rain and how to report on slow deliveries.
resource: postgresql://localhost/aai_food/public/orders
tags: [playbook, weather, rain, operations, incident]
timestamp: 2026-11-01T10:00:00Z
---

# When it applies

When `weather = 'Heavy Rain'` in the [orders](/tables/orders.md) table, the
**rain surge** playbook is active in that city:

- Customers see **+10 minutes** added to the ETA in the app.
- Riders receive a **rain bonus** per delivery.
- **Cancellations usually rise** (customers give up, restaurants pause).

# Reporting rules

- The late threshold **stays 40 minutes** (see [late_delivery_rate](/metrics/late_delivery_rate.md)).
  Do not relax it for rain.
- When explaining **slow deliveries**, ALWAYS break the results down **by weather**
  and **by date / hour** to check whether rain was the cause.
- Compare [delivery time](/metrics/delivery_time.md) and late rate in `'Heavy Rain'`
  against `'Clear'` for the same city and period.
- Also report cancelled orders in the same window, since they rise in heavy rain.

# Known incident

- **Pune, Friday 30 October 2026, roughly 18:00–23:00 IST**: heavy rain.
  Deliveries were much slower than normal and more orders were cancelled.

# Example SQL

Delivery time and late rate by weather for one city and date:

```sql
SELECT weather,
       COUNT(*) FILTER (WHERE status = 'Delivered') AS delivered,
       COUNT(*) FILTER (WHERE status = 'Cancelled') AS cancelled,
       ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0)
             FILTER (WHERE status = 'Delivered')::numeric, 1) AS avg_delivery_min,
       ROUND(100.0 * COUNT(*) FILTER (
               WHERE status = 'Delivered'
                 AND EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0 > 40)
             / NULLIF(COUNT(*) FILTER (WHERE status = 'Delivered'), 0), 1) AS late_rate_pct
FROM orders
WHERE city = 'Pune'
  AND order_placed_at >= '2026-10-30'
  AND order_placed_at <  '2026-10-31'
GROUP BY weather
ORDER BY weather;
```

For an hour-by-hour view, group by `EXTRACT(HOUR FROM order_placed_at)` and `weather`.

# Related

- [delivery_time](/metrics/delivery_time.md)
- [late_delivery_rate](/metrics/late_delivery_rate.md)
- [orders](/tables/orders.md)
