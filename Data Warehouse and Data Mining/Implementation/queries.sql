-- RetailMart data warehouse: OLAP sample queries (SQLite). Run with:  sqlite3 retail_dw.sqlite < queries.sql

-- 5.1 Roll-up: total sales by year
SELECT d.year, COUNT(DISTINCT f.invoice_id) AS invoices, SUM(f.quantity) AS units, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key GROUP BY d.year ORDER BY d.year;

-- 5.2 Drill-down: year -> quarter
SELECT d.year, d.quarter, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key GROUP BY d.year, d.quarter ORDER BY d.year, d.quarter;

-- 5.3 Drill-down: Electronics by month in Q4 2025
SELECT d.month_name, ROUND(SUM(f.net_amount)) AS net_sales, SUM(f.quantity) AS units
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key JOIN dim_product p ON p.product_key = f.product_key
WHERE d.year = 2025 AND d.quarter = 4 AND p.category = 'Electronics' GROUP BY d.month, d.month_name ORDER BY d.month;

-- 5.4 Slice: Q4 2025 by category
SELECT p.category, ROUND(SUM(f.net_amount)) AS net_sales, SUM(f.quantity) AS units
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key JOIN dim_product p ON p.product_key = f.product_key
WHERE d.year = 2025 AND d.quarter = 4 GROUP BY p.category ORDER BY net_sales DESC;

-- 5.5 Dice: 2025, Electronics and Grocery, West and South regions
SELECT p.category, s.region, ROUND(SUM(f.net_amount)) AS net_sales, SUM(f.quantity) AS units
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_store s ON s.store_key = f.store_key
WHERE d.year = 2025 AND p.category IN ('Electronics', 'Grocery') AND s.region IN ('West', 'South')
GROUP BY p.category, s.region ORDER BY p.category, s.region;

-- 5.6 Pivot / cube cells: category x region, 2025
SELECT p.category, s.region, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_store s ON s.store_key = f.store_key WHERE d.year = 2025 GROUP BY p.category, s.region;

-- 5.7 Top 5 products by net sales
SELECT p.product_name, p.category, SUM(f.quantity) AS units, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_product p ON p.product_key = f.product_key GROUP BY p.product_key ORDER BY net_sales DESC LIMIT 5;

-- 5.8 Net sales by store
SELECT s.store_name, s.region, ROUND(SUM(f.net_amount)) AS net_sales, COUNT(DISTINCT f.invoice_id) AS invoices
FROM fact_sales f JOIN dim_store s ON s.store_key = f.store_key GROUP BY s.store_key ORDER BY net_sales DESC;

-- 5.9 Average daily sales: festive vs regular season
SELECT d.season, ROUND(SUM(f.net_amount) / COUNT(DISTINCT d.date_key)) AS avg_daily_net_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key GROUP BY d.season;

-- 5.10 Customer segments (known customers) by age group
SELECT c.age_group, COUNT(DISTINCT c.customer_key) AS customers, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_customer c ON c.customer_key = f.customer_key WHERE c.customer_key <> 0 GROUP BY c.age_group ORDER BY net_sales DESC;

-- 5.11 Payment mode share
SELECT y.payment_mode, ROUND(SUM(f.net_amount)) AS net_sales,
       ROUND(100.0 * SUM(f.net_amount) / (SELECT SUM(net_amount) FROM fact_sales), 1) AS share_pct
FROM fact_sales f JOIN dim_payment y ON y.payment_key = f.payment_key GROUP BY y.payment_key ORDER BY net_sales DESC;

-- 5.12 Fact-less fact table: customer visits per store
SELECT s.store_name, COUNT(*) AS customer_visits, COUNT(DISTINCT v.customer_key) AS distinct_customers
FROM fact_store_visit v JOIN dim_store s ON s.store_key = v.store_key GROUP BY s.store_key ORDER BY customer_visits DESC;

-- Snowflake version of 5.6 (8 joins instead of 4; identical result)
SELECT c.category, r.region, ROUND(SUM(f.net_amount)) AS net_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key
JOIN sf_product p ON p.product_key = f.product_key JOIN sf_subcategory sc ON sc.subcategory_key = p.subcategory_key
JOIN sf_category c ON c.category_key = sc.category_key
JOIN sf_store s ON s.store_key = f.store_key JOIN sf_city ci ON ci.city_key = s.city_key JOIN sf_region r ON r.region_key = ci.region_key
WHERE d.year = 2025 GROUP BY c.category, r.region;
