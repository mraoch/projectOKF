---
type: Index
title: Aai-Food Delivery knowledge bundle
description: Start here. What Aai-Food Delivery is and a map of every concept in this bundle.
resource: postgresql://localhost/aai_food
tags: [aai-food, index, start-here]
timestamp: 2026-11-01T10:00:00Z
---

# Aai-Food Delivery

Aai-Food Delivery is a food delivery app operating in **Pune, Mumbai and Bengaluru**.
Customers order food from partner restaurants and our riders deliver it.
All order data lives in the PostgreSQL database `aai_food` and covers **1–31 October 2026**.

Read this file first, then open only the concepts you need.

# Folders

| Folder | What is inside |
|--------|----------------|
| [tables/](/tables/index.md) | The database tables: what each row means, columns, allowed values, gotchas |
| [metrics/](/metrics/index.md) | Official business metric definitions with the exact SQL formula |
| [playbooks/](/playbooks/index.md) | Operational situations and how to report on them |
| [glossary/](/glossary/index.md) | Plain-language meaning of business terms used in questions |

# All concepts

- [tables/orders](/tables/orders.md) – one row per customer order; status, timestamps, money, rider, weather, rating.
- [tables/restaurants](/tables/restaurants.md) – one row per partner restaurant; name, cuisine, city, area, rating, active flag.
- [metrics/delivery_time](/metrics/delivery_time.md) – minutes from order placed to delivered; delivered orders only.
- [metrics/late_delivery_rate](/metrics/late_delivery_rate.md) – % of delivered orders that took more than 40 minutes.
- [metrics/net_revenue](/metrics/net_revenue.md) – order value minus discount plus delivery fee, delivered orders only; also GMV.
- [playbooks/heavy_rain](/playbooks/heavy_rain.md) – rain surge rules and the Pune heavy-rain incident on 30 Oct 2026.
- [glossary/business_terms](/glossary/business_terms.md) – late, on-time, GMV, active restaurant, peak hours, "last Friday" and more.

See [log.md](/log.md) for the history of changes to this bundle.
