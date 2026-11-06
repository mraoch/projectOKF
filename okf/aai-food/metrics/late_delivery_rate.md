---
type: Metric
title: Late delivery rate
description: Percentage of delivered orders whose delivery time was more than 40 minutes.
resource: postgresql://localhost/aai_food/public/orders
tags: [metric, delivery, sla, operations]
timestamp: 2026-11-01T10:00:00Z
---

# Definition

An order is **LATE** when its [delivery time](/metrics/delivery_time.md) is
**more than 40 minutes**. Exactly 40 minutes is **on time**.

**Late delivery rate** = late delivered orders ÷ all delivered orders × 100,
rounded to 1 decimal.

# Rules

- Cancelled orders are **excluded from both numerator and denominator**
  (filter `status = 'Delivered'`).
- Threshold is strictly greater than: `> 40`, not `>= 40`.
- The threshold stays 40 minutes in every weather (see [heavy_rain](/playbooks/heavy_rain.md)).

# Example SQL

Late delivery rate by city using FILTER:

```sql
SELECT city,
       COUNT(*) AS delivered_orders,
       COUNT(*) FILTER (
         WHERE EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0 > 40
       ) AS late_orders,
       ROUND(100.0 * COUNT(*) FILTER (
         WHERE EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0 > 40
       ) / COUNT(*), 1) AS late_rate_pct
FROM orders
WHERE status = 'Delivered'
GROUP BY city
ORDER BY city;
```

The same with CASE:

```sql
SELECT ROUND(100.0 * SUM(CASE WHEN EXTRACT(EPOCH FROM (order_delivered_at - order_placed_at)) / 60.0 > 40
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_rate_pct
FROM orders
WHERE status = 'Delivered';
```

# Related

- [delivery_time](/metrics/delivery_time.md) – how delivery time is calculated
- [orders](/tables/orders.md) – source table
- [heavy_rain](/playbooks/heavy_rain.md) – always check weather when the late rate is high
