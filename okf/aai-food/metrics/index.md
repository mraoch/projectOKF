---
type: Index
title: Metrics
description: Official Aai-Food Delivery business metric definitions.
resource: postgresql://localhost/aai_food/public
tags: [metrics, index]
timestamp: 2026-11-01T10:00:00Z
---

# Metrics

- [delivery_time](/metrics/delivery_time.md) – minutes from order_placed_at to order_delivered_at; Delivered orders only; average rounded to 1 decimal.
- [late_delivery_rate](/metrics/late_delivery_rate.md) – late = delivery time > 40 minutes; % of Delivered orders that were late.
- [net_revenue](/metrics/net_revenue.md) – SUM(order_value_inr − discount_inr + delivery_fee_inr) for Delivered orders; also defines GMV.
