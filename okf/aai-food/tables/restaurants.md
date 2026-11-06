---
type: PostgreSQL Table
title: restaurants
description: One row per partner restaurant on the Aai-Food Delivery app.
resource: postgresql://localhost/aai_food/public/restaurants
tags: [table, restaurants, core]
timestamp: 2026-11-01T10:00:00Z
---

# Summary

One row per partner restaurant listed on the app. 18 restaurants across Pune, Mumbai
and Bengaluru. Orders link to restaurants through [orders](/tables/orders.md).

# Schema

| Column | Type | Nullable | Description | Sample values |
|--------|------|----------|-------------|---------------|
| restaurant_id | text (PK) | No | Unique restaurant ID | R001 … R018 |
| restaurant_name | text | No | Restaurant display name | Biryani Darbar, Puneri Misal House, Udupi Tiffin Centre |
| cuisine | text | No | Main cuisine | Street Food, Biryani, Maharashtrian, Healthy, Chinese, Pizza, North Indian, Seafood, Japanese, Cafe, Burgers, South Indian, Andhra, Asian |
| city | text | No | City of the restaurant | Pune, Mumbai, Bengaluru |
| area | text | No | Neighbourhood within the city | Kothrud, Koregaon Park, Baner, Bandra, Andheri, Koramangala, Indiranagar |
| rating | numeric | No | Restaurant's average rating on the app | 3.8 … 4.7 |
| avg_prep_time_min | integer | No | Average kitchen preparation time in minutes | 8 … 25 |
| is_active | boolean | No | Is the restaurant currently live on the app | true, false |
| joined_on | date | No | Date the restaurant joined the platform | 2024-02-11 |

# Allowed values

Values are **case-sensitive**:

- `city`: `'Pune'`, `'Mumbai'`, `'Bengaluru'`
- `is_active`: `true`, `false` (boolean, not text)

# Joins

- `restaurants.restaurant_id = orders.restaurant_id` → [orders](/tables/orders.md)

# Gotchas

- Filter **`is_active = true`** when listing current restaurants.
- **R013 (Burger Barn, Mumbai) is inactive** and has no orders. A LEFT JOIN from restaurants
  to orders will show it with zero orders; an INNER JOIN will drop it.
- `rating` is the restaurant's overall rating; it is not the same as
  `orders.customer_rating` (the rating of a single order).
- `city` exists in both tables. When joined, qualify it (`r.city` or `o.city`).

# Example queries

Current restaurants per city:

```sql
SELECT city, COUNT(*) AS active_restaurants
FROM restaurants
WHERE is_active = true
GROUP BY city
ORDER BY city;
```

Delivered orders per restaurant (with name):

```sql
SELECT r.restaurant_name, r.city, COUNT(*) AS delivered_orders
FROM orders o
JOIN restaurants r ON r.restaurant_id = o.restaurant_id
WHERE o.status = 'Delivered'
GROUP BY r.restaurant_name, r.city
ORDER BY delivered_orders DESC
LIMIT 5;
```
