---
type: Metric
title: Net revenue
description: Order value minus discount plus delivery fee, for Delivered orders only, in INR. Also defines GMV.
resource: postgresql://localhost/aai_food/public/orders
tags: [metric, revenue, finance]
timestamp: 2026-11-01T10:00:00Z
---

# Definition

**Net revenue** = `SUM(order_value_inr - discount_inr + delivery_fee_inr)`
for **Delivered** orders only.

**GMV** (gross merchandise value) = `SUM(order_value_inr)` for **Delivered** orders only.

# Rules

- Cancelled orders **never** count as revenue or GMV.
- Currency is **INR (₹)**. Values are whole rupees.
- "Revenue" in a question means **net revenue** unless the user says GMV or gross.
- Filter dates on `order_placed_at`.

# Example SQL

Net revenue and GMV by city:

```sql
SELECT city,
       SUM(order_value_inr - discount_inr + delivery_fee_inr) AS net_revenue_inr,
       SUM(order_value_inr)                                   AS gmv_inr
FROM orders
WHERE status = 'Delivered'
GROUP BY city
ORDER BY net_revenue_inr DESC;
```

# Related

- [orders](/tables/orders.md) – source table and money columns
- [business_terms](/glossary/business_terms.md) – GMV and net revenue in plain words
