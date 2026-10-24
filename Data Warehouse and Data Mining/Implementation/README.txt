DWDM (METCE11507) - supporting files for ALA 1 and ALA 2
=========================================================
All data are SIMULATED sample data for a fictitious retail chain ("RetailMart").

source/            raw extracts: customers.csv, products.csv, stores.csv, sales_raw.csv (with deliberate quality problems)
gen_data.py        generates the source extracts (seeded -> reproducible)
etl.py             ETL: extract, clean, transform, load into retail_dw.sqlite (star + snowflake schemas); writes etl_log.json
queries.sql        OLAP sample queries (roll-up, drill-down, slice, dice, pivot, snowflake comparison)
retail_dw.sqlite   the loaded data warehouse (SQLite)
DWDM_ALA2_Association_Rules_Notebook.ipynb   Apriori / FP-Growth notebook (reads retail_dw.sqlite; keep both in the same folder)

How to run (Python 3 with pandas, numpy, matplotlib):
  python gen_data.py        # optional: regenerate the source CSV files
  python etl.py             # rebuild the warehouse
  sqlite3 retail_dw.sqlite < queries.sql
  jupyter notebook DWDM_ALA2_Association_Rules_Notebook.ipynb
