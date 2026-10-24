"""ETL for the RetailMart data warehouse (Python/Pandas + SQLite SQL)."""
import json, os, re, sqlite3
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")
DB = os.environ.get("DW_DB", os.path.join(HERE, "retail_dw.sqlite"))
LOG = {}
REJECTS = []

# ============================ SCHEMA (DDL) ============================
DDL = """
DROP TABLE IF EXISTS fact_sales;      DROP TABLE IF EXISTS fact_store_visit;
DROP TABLE IF EXISTS dim_date;        DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;     DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_payment;     DROP TABLE IF EXISTS etl_rejects;
DROP TABLE IF EXISTS sf_product;      DROP TABLE IF EXISTS sf_subcategory;  DROP TABLE IF EXISTS sf_category;
DROP TABLE IF EXISTS sf_store;        DROP TABLE IF EXISTS sf_city;         DROP TABLE IF EXISTS sf_region;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,           -- YYYYMMDD surrogate key
    full_date TEXT NOT NULL, day INTEGER, month INTEGER, month_name TEXT,
    quarter INTEGER, year INTEGER, day_name TEXT, is_weekend INTEGER, season TEXT);
CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY, customer_id TEXT, customer_name TEXT, gender TEXT,
    age_group TEXT, city TEXT, state TEXT, signup_year INTEGER, email_valid INTEGER);
CREATE TABLE dim_product (
    product_key INTEGER PRIMARY KEY, product_id TEXT, product_name TEXT, category TEXT,
    subcategory TEXT, brand TEXT, list_price REAL);
CREATE TABLE dim_store (
    store_key INTEGER PRIMARY KEY, store_id TEXT, store_name TEXT, city TEXT, state TEXT, region TEXT);
CREATE TABLE dim_payment (payment_key INTEGER PRIMARY KEY, payment_mode TEXT);

CREATE TABLE fact_sales (                   -- grain: one invoice line
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    store_key INTEGER NOT NULL REFERENCES dim_store(store_key),
    payment_key INTEGER NOT NULL REFERENCES dim_payment(payment_key),
    invoice_id TEXT NOT NULL, line_no INTEGER NOT NULL,       -- degenerate dimensions
    quantity INTEGER,                       -- fully additive
    gross_amount REAL, discount_amount REAL, net_amount REAL, -- fully additive
    unit_price REAL, discount_pct REAL,                       -- non-additive
    PRIMARY KEY (invoice_id, line_no));

CREATE TABLE fact_store_visit (             -- fact-less fact table: records an event, no measures
    date_key INTEGER NOT NULL, customer_key INTEGER NOT NULL, store_key INTEGER NOT NULL,
    PRIMARY KEY (date_key, customer_key, store_key));

-- Snowflake variant: normalised product and store hierarchies
CREATE TABLE sf_category (category_key INTEGER PRIMARY KEY, category TEXT);
CREATE TABLE sf_subcategory (subcategory_key INTEGER PRIMARY KEY, subcategory TEXT, category_key INTEGER REFERENCES sf_category);
CREATE TABLE sf_product (product_key INTEGER PRIMARY KEY, product_id TEXT, product_name TEXT, brand TEXT,
                         list_price REAL, subcategory_key INTEGER REFERENCES sf_subcategory);
CREATE TABLE sf_region (region_key INTEGER PRIMARY KEY, region TEXT);
CREATE TABLE sf_city (city_key INTEGER PRIMARY KEY, city TEXT, state TEXT, region_key INTEGER REFERENCES sf_region);
CREATE TABLE sf_store (store_key INTEGER PRIMARY KEY, store_id TEXT, store_name TEXT, city_key INTEGER REFERENCES sf_city);

CREATE TABLE etl_rejects (invoice_id TEXT, line_no INTEGER, reason TEXT);
CREATE INDEX ix_fact_date ON fact_sales(date_key);
CREATE INDEX ix_fact_prod ON fact_sales(product_key);
CREATE INDEX ix_fact_store ON fact_sales(store_key);
CREATE INDEX ix_fact_cust ON fact_sales(customer_key);
"""

# ============================ EXTRACT ============================
def extract():
    cust = pd.read_csv(f"{SRC}/customers.csv", dtype=str, keep_default_na=False)
    prod = pd.read_csv(f"{SRC}/products.csv", dtype=str, keep_default_na=False)
    store = pd.read_csv(f"{SRC}/stores.csv", dtype=str, keep_default_na=False)
    sales = pd.read_csv(f"{SRC}/sales_raw.csv", dtype=str, keep_default_na=False)
    LOG["extracted"] = dict(customers=len(cust), products=len(prod), stores=len(store), sales_lines=len(sales))
    return cust, prod, store, sales

# ============================ TRANSFORM ============================
STATE_MAP = {"GJ": "Gujarat", "MH": "Maharashtra", "TN": "Tamil Nadu", "KA": "Karnataka", "WB": "West Bengal", "DL": "Delhi"}
GENDER_MAP = {"m": "Male", "male": "Male", "f": "Female", "female": "Female"}
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")


def age_group(birth):
    age = 2025 - int(birth[:4])
    return "18-25" if age <= 25 else "26-35" if age <= 35 else "36-50" if age <= 50 else "51+"


def transform_customers(c):
    n0 = len(c)
    c = c.copy()
    c["name"] = c["name"].str.strip().str.title()
    c["email"] = c["email"].str.strip().str.lower()
    c["email_valid"] = c["email"].apply(lambda e: 1 if EMAIL_RE.match(e) else 0)
    c["gender"] = c["gender"].str.strip().str.lower().map(GENDER_MAP).fillna("Unknown")
    c["state"] = c["state"].str.strip().replace(STATE_MAP)
    missing_city = (c["city"].str.strip() == "").sum()
    c["city"] = c["city"].str.strip().replace("", "Unknown").str.title()
    c["age_group"] = c["birth_date"].apply(age_group)
    c["signup_year"] = c["signup_date"].str[:4].astype(int)
    c = c.drop_duplicates(subset="customer_id", keep="first")
    LOG["customers"] = dict(read=n0, duplicates_removed=n0 - len(c), missing_city_filled=int(missing_city),
                            invalid_email_flagged=int((c.email_valid == 0).sum()), gender_standardised=True, state_codes_expanded=True)
    unknown = pd.DataFrame([{"customer_id": "UNKNOWN", "name": "Unknown / Walk-in", "email": "", "city": "Unknown", "state": "Unknown",
                             "gender": "Unknown", "age_group": "Unknown", "signup_year": 0, "email_valid": 0}])
    return pd.concat([unknown, c[["customer_id", "name", "email", "city", "state", "gender", "age_group", "signup_year", "email_valid"]]], ignore_index=True)


def parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(s, format=fmt)
        except ValueError:
            continue
    return pd.NaT


def transform_sales(s, prod, cust, store):
    s = s.copy()
    n_read = len(s)
    s = s.drop_duplicates()                                                   # exact duplicate lines
    LOG["sales"] = {"read": n_read, "exact_duplicates_removed": n_read - len(s)}
    s["order_date"] = s["order_date"].apply(parse_date)
    s["payment_mode"] = s["payment_mode"].str.strip().str.title().replace({"Upi": "UPI"})
    price_text = s["unit_price"].str.contains("Rs", na=False)
    s["unit_price"] = pd.to_numeric(s["unit_price"].str.replace("Rs.", "", regex=False).str.strip(), errors="coerce")
    s["quantity"] = pd.to_numeric(s["quantity"], errors="coerce")
    s["discount_pct"] = pd.to_numeric(s["discount_pct"], errors="coerce").fillna(0)
    s["line_no"] = s["line_no"].astype(int)
    LOG["sales"]["price_text_cleaned"] = int(price_text.sum())

    # missing price -> take list price from product master
    plist = prod.set_index("product_id")["list_price"].astype(float)
    miss_price = s["unit_price"].isna()
    s.loc[miss_price, "unit_price"] = s.loc[miss_price, "product_id"].map(plist)
    LOG["sales"]["missing_price_filled_from_master"] = int(miss_price.sum())

    # unknown (orphan) customers -> 'UNKNOWN' member
    orphan = ~s["customer_id"].isin(cust["customer_id"])
    s.loc[orphan, "customer_id"] = "UNKNOWN"
    LOG["sales"]["orphan_customers_mapped_to_unknown"] = int(orphan.sum())

    # rejects (business rules)
    rules = [("missing or invalid quantity (<= 0)", s["quantity"].isna() | (s["quantity"] <= 0)),
             ("missing store", s["store_id"].str.strip() == ""),
             ("order date after load date (future)", s["order_date"] > pd.Timestamp("2025-12-31")),
             ("invalid discount (> 50%)", s["discount_pct"] > 50),
             ("unparseable date", s["order_date"].isna())]
    reject_mask = pd.Series(False, index=s.index)
    counts = {}
    for reason, m in rules:
        m = m & ~reject_mask
        counts[reason] = int(m.sum())
        for _, r in s[m].iterrows():
            REJECTS.append((r["invoice_id"], int(r["line_no"]), reason))
        reject_mask |= m
    LOG["sales"]["rejected_by_reason"] = counts
    s = s[~reject_mask].copy()
    s["quantity"] = s["quantity"].astype(int)
    s["gross_amount"] = (s["quantity"] * s["unit_price"]).round(2)
    s["discount_amount"] = (s["gross_amount"] * s["discount_pct"] / 100).round(2)
    s["net_amount"] = (s["gross_amount"] - s["discount_amount"]).round(2)
    LOG["sales"]["loaded"] = len(s)
    return s


def build_dim_date():
    d = pd.date_range("2024-01-01", "2025-12-31")
    df = pd.DataFrame({"full_date": d})
    df["date_key"] = df.full_date.dt.strftime("%Y%m%d").astype(int)
    df["day"] = df.full_date.dt.day; df["month"] = df.full_date.dt.month
    df["month_name"] = df.full_date.dt.strftime("%b"); df["quarter"] = df.full_date.dt.quarter
    df["year"] = df.full_date.dt.year; df["day_name"] = df.full_date.dt.strftime("%a")
    df["is_weekend"] = (df.full_date.dt.weekday >= 5).astype(int)
    df["season"] = df.month.map(lambda m: "Festive (Oct-Nov)" if m in (10, 11) else "Regular")
    df["full_date"] = df.full_date.dt.strftime("%Y-%m-%d")
    return df[["date_key", "full_date", "day", "month", "month_name", "quarter", "year", "day_name", "is_weekend", "season"]]

# ============================ LOAD ============================
def load():
    cust, prod, store, sales = extract()
    dim_cust = transform_customers(cust)
    fact = transform_sales(sales, prod, dim_cust, store)
    con = sqlite3.connect(DB)
    con.executescript(DDL)

    build_dim_date().to_sql("dim_date", con, if_exists="append", index=False)

    dim_cust.insert(0, "customer_key", range(0, len(dim_cust)))               # key 0 = Unknown
    dim_cust["customer_name"] = dim_cust["name"]
    dim_cust[["customer_key", "customer_id", "customer_name", "gender", "age_group", "city", "state", "signup_year", "email_valid"]].to_sql(
        "dim_customer", con, if_exists="append", index=False)

    prod = prod.copy(); prod["list_price"] = prod["list_price"].astype(float)
    prod.insert(0, "product_key", range(1, len(prod) + 1))
    prod[["product_key", "product_id", "product_name", "category", "subcategory", "brand", "list_price"]].to_sql("dim_product", con, if_exists="append", index=False)

    store = store.copy(); store.insert(0, "store_key", range(1, len(store) + 1))
    store[["store_key", "store_id", "store_name", "city", "state", "region"]].to_sql("dim_store", con, if_exists="append", index=False)

    pay = pd.DataFrame({"payment_mode": sorted(fact["payment_mode"].unique())}); pay.insert(0, "payment_key", range(1, len(pay) + 1))
    pay.to_sql("dim_payment", con, if_exists="append", index=False)

    # surrogate-key lookups
    ck = dict(zip(dim_cust["customer_id"], dim_cust["customer_key"])); pk = dict(zip(prod["product_id"], prod["product_key"]))
    sk = dict(zip(store["store_id"], store["store_key"])); yk = dict(zip(pay["payment_mode"], pay["payment_key"]))
    f = pd.DataFrame({
        "date_key": fact["order_date"].dt.strftime("%Y%m%d").astype(int), "customer_key": fact["customer_id"].map(ck),
        "product_key": fact["product_id"].map(pk), "store_key": fact["store_id"].map(sk), "payment_key": fact["payment_mode"].map(yk),
        "invoice_id": fact["invoice_id"], "line_no": fact["line_no"], "quantity": fact["quantity"], "gross_amount": fact["gross_amount"],
        "discount_amount": fact["discount_amount"], "net_amount": fact["net_amount"], "unit_price": fact["unit_price"], "discount_pct": fact["discount_pct"]})
    assert f.isna().sum().sum() == 0, "lookup failure"
    f.to_sql("fact_sales", con, if_exists="append", index=False)

    con.execute("INSERT INTO fact_store_visit SELECT DISTINCT date_key, customer_key, store_key FROM fact_sales WHERE customer_key <> 0")
    pd.DataFrame(REJECTS, columns=["invoice_id", "line_no", "reason"]).to_sql("etl_rejects", con, if_exists="append", index=False)

    # snowflake tables populated from the star dimensions (SQL)
    con.executescript("""
    INSERT INTO sf_category(category) SELECT DISTINCT category FROM dim_product ORDER BY 1;
    INSERT INTO sf_subcategory(subcategory, category_key)
        SELECT DISTINCT p.subcategory, c.category_key FROM dim_product p JOIN sf_category c ON c.category = p.category ORDER BY 1;
    INSERT INTO sf_product(product_key, product_id, product_name, brand, list_price, subcategory_key)
        SELECT p.product_key, p.product_id, p.product_name, p.brand, p.list_price, s.subcategory_key
        FROM dim_product p JOIN sf_category c ON c.category = p.category
        JOIN sf_subcategory s ON s.subcategory = p.subcategory AND s.category_key = c.category_key;
    INSERT INTO sf_region(region) SELECT DISTINCT region FROM dim_store ORDER BY 1;
    INSERT INTO sf_city(city, state, region_key) SELECT DISTINCT d.city, d.state, r.region_key FROM dim_store d JOIN sf_region r ON r.region = d.region;
    INSERT INTO sf_store(store_key, store_id, store_name, city_key)
        SELECT d.store_key, d.store_id, d.store_name, c.city_key FROM dim_store d JOIN sf_city c ON c.city = d.city AND c.state = d.state;
    """)
    con.commit()
    LOG["loaded"] = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
                     ["dim_date", "dim_customer", "dim_product", "dim_store", "dim_payment", "fact_sales", "fact_store_visit", "etl_rejects",
                      "sf_category", "sf_subcategory", "sf_product", "sf_region", "sf_city", "sf_store"]}
    con.close()
    json.dump(LOG, open(os.path.join(HERE, "etl_log.json"), "w"), indent=1)
    return LOG


if __name__ == "__main__":
    print(json.dumps(load(), indent=1))
