---
type: Metric
title: Delivery time
description: Minutes from when the customer placed the order to when it was delivered. Delivered orders only.
resource: postgresql://localhost/aai_food/public/orders
tags: [metric, delivery, operations]
timestamp: 2026-11-01T10:00:00Z
---

# Definition

**Delivery time** is the number of minutes between `order_placed_at` and
`order_delivered_at` in the [orders](/tables/orders.md) table.
There is no stored column for it; always calculate it.

# SQL formula

```sql
EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0
```

# Rules

- Only **`status = 'Delivered'`** orders. Cancelled orders are **NEVER** counted
  (they have no delivered time).
- Report averages **rounded to 1 decimal**: `ROUND(AVG(...)::numeric, 1)`.
- Filter dates on `order_placed_at`.

# Example SQL

Average delivery time by city:

```sql
SELECT city,
       ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0)::numeric, 1)
         AS avg_delivery_min
FROM orders
WHERE status = 'Delivered'
GROUP BY city
ORDER BY city;
```

# Related

- [orders](/tables/orders.md) – source table
- [late_delivery_rate](/metrics/late_delivery_rate.md) – built on top of delivery time
- [heavy_rain](/playbooks/heavy_rain.md) – why delivery time can jump on rainy evenings
