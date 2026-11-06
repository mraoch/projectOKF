---
type: Glossary
title: Business terms
description: Simple definitions of the words the Aai-Food Delivery team uses in questions.
resource: postgresql://localhost/aai_food
tags: [glossary, definitions]
timestamp: 2026-11-01T10:00:00Z
---

# Business terms

**Order** – one customer checkout on the app. One row in [orders](/tables/orders.md).

**Delivered order** – an order with `status = 'Delivered'`. It has a delivered time, rider and
rating. See [orders](/tables/orders.md).

**Cancelled order** – an order with `status = 'Cancelled'`. It never reached the customer;
delivered time, rider and rating are NULL. Never counted in delivery time, late rate or revenue.

**Delivery time** – minutes from order placed to delivered. See
[delivery_time](/metrics/delivery_time.md).

**Late delivery** – a delivered order that took **more than 40 minutes**. See
[late_delivery_rate](/metrics/late_delivery_rate.md).

**On-time delivery** – a delivered order that took **40 minutes or less**. See
[late_delivery_rate](/metrics/late_delivery_rate.md).

**GMV** – gross merchandise value: total `order_value_inr` of delivered orders. See
[net_revenue](/metrics/net_revenue.md).

**Net revenue** – order value minus discount plus delivery fee, delivered orders only.
"Revenue" means net revenue by default. See [net_revenue](/metrics/net_revenue.md).

**Active restaurant** – a restaurant with `is_active = true`. See
[restaurants](/tables/restaurants.md).

**Peak hours** – lunch **12:00–14:59** and dinner **19:00–22:59** IST, based on
`order_placed_at`. In SQL: `EXTRACT(HOUR FROM order_placed_at) BETWEEN 12 AND 14` or
`BETWEEN 19 AND 22`.

**Heavy rain / rain surge** – `weather = 'Heavy Rain'`; special operating rules apply. See
[heavy_rain](/playbooks/heavy_rain.md).

**"Last Friday", "yesterday", "last week"** – relative dates. Resolve them against **today's
date, which the agent receives in its prompt**. "Last Friday" means the most recent Friday
before today. Example: if today is Monday 2026-11-02, last Friday is **2026-10-30**. Then filter
`order_placed_at >= '2026-10-30' AND order_placed_at < '2026-10-31'`.
