
-- ============================================
-- E-COMMERCE DATA ENGINEERING PROJECT
-- SQL ANALYTICS
-- ============================================

-- 1. Overall sales KPIs
SELECT
    COUNT(*) AS total_order_items,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue,
    ROUND(AVG(sales_amount), 2) AS average_item_revenue
FROM fact_sales;


-- 2. Monthly revenue
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.sales_amount), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- 3. Top 10 products by revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.sales_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- 4. Top 10 customers by revenue
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;


-- 5. Revenue by location
SELECT
    l.city,
    l.state,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.sales_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY
    l.city,
    l.state
ORDER BY total_revenue DESC;
