---
type: Index
title: Tables
description: The PostgreSQL tables in the aai_food database.
resource: postgresql://localhost/aai_food/public
tags: [tables, index]
timestamp: 2026-11-01T10:00:00Z
---

# Tables

- [orders](/tables/orders.md) – one row per customer order. Has NO delivery time column (see [delivery_time](/metrics/delivery_time.md)). Cancelled orders have NULL delivered time, rider and rating.
- [restaurants](/tables/restaurants.md) – one row per partner restaurant. Use `is_active = true` for current restaurants.

Join: `orders.restaurant_id = restaurants.restaurant_id`.
