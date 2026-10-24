"""Generates the operational (source-system) extracts for the RetailMart case:
customers.csv, products.csv, stores.csv, sales_raw.csv  -- with realistic data-quality problems.
All data are SIMULATED sample data (seeded, reproducible)."""
import csv, os, random
from datetime import date, timedelta
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")
os.makedirs(OUT, exist_ok=True)
rng = random.Random(42)
nrg = np.random.default_rng(42)

# ---------------- products (product_id, name, category, subcategory, brand, price) ----------------
PRODUCTS = [
    ("P001", "Whole Wheat Bread", "Grocery", "Bakery", "FreshBake", 45), ("P002", "Butter 100g", "Grocery", "Dairy", "DairyPure", 56),
    ("P003", "Mixed Fruit Jam", "Grocery", "Spreads", "FruitCo", 120), ("P004", "Milk 1L", "Grocery", "Dairy", "DairyPure", 66),
    ("P005", "Eggs (12)", "Grocery", "Dairy", "FarmFresh", 90), ("P006", "Basmati Rice 5kg", "Grocery", "Staples", "GoldGrain", 620),
    ("P007", "Wheat Flour 5kg", "Grocery", "Staples", "GoldGrain", 290), ("P008", "Tea 500g", "Grocery", "Beverages", "TeaHouse", 260),
    ("P009", "Coffee 200g", "Grocery", "Beverages", "BeanBox", 480), ("P010", "Sugar 1kg", "Grocery", "Staples", "SweetLeaf", 48),
    ("P011", "Potato Chips", "Snacks", "Chips", "CrunchyJoe", 20), ("P012", "Cola 750ml", "Snacks", "Soft Drinks", "FizzUp", 40),
    ("P013", "Cream Cookies", "Snacks", "Biscuits", "BakeHouse", 35), ("P014", "Instant Noodles", "Snacks", "Noodles", "NoodleKing", 14),
    ("P015", "Pasta 500g", "Snacks", "Noodles", "NoodleKing", 85), ("P016", "Pasta Sauce", "Snacks", "Sauces", "FruitCo", 110),
    ("P017", "Laptop 14in", "Electronics", "Computers", "TechNova", 45000), ("P018", "Wireless Mouse", "Electronics", "Accessories", "TechNova", 600),
    ("P019", "Keyboard", "Electronics", "Accessories", "TechNova", 1200), ("P020", "USB Drive 32GB", "Electronics", "Storage", "DataSafe", 450),
    ("P021", "Headphones", "Electronics", "Audio", "SoundWave", 1800), ("P022", "Power Bank 10000mAh", "Electronics", "Mobile Accessories", "VoltPlus", 1500),
    ("P023", "Smartphone", "Electronics", "Mobiles", "TechNova", 15000), ("P024", "Phone Case", "Electronics", "Mobile Accessories", "VoltPlus", 400),
    ("P025", "Screen Guard", "Electronics", "Mobile Accessories", "VoltPlus", 250), ("P026", "Fast Charger", "Electronics", "Mobile Accessories", "VoltPlus", 700),
    ("P027", "Shampoo 340ml", "Personal Care", "Hair Care", "SilkyHair", 250), ("P028", "Soap (4 pack)", "Personal Care", "Bath", "PureBath", 150),
    ("P029", "Toothpaste", "Personal Care", "Oral Care", "BrightSmile", 95), ("P030", "Face Wash", "Personal Care", "Skin Care", "GlowUp", 220),
    ("P031", "Deodorant", "Personal Care", "Fragrance", "FreshFit", 240), ("P032", "Detergent 1kg", "Home", "Cleaning", "CleanMax", 210),
    ("P033", "Dishwash Liquid", "Home", "Cleaning", "CleanMax", 110), ("P034", "Bedsheet Double", "Home", "Furnishing", "HomeNest", 899),
    ("P035", "Water Bottle", "Home", "Kitchenware", "HomeNest", 350), ("P036", "LED Bulb 9W", "Home", "Lighting", "BrightLite", 120),
]
PRICE = {p[0]: p[5] for p in PRODUCTS}
CAT = {p[0]: p[2] for p in PRODUCTS}

STORES = [("S01", "RetailMart Bhavnagar Central", "Bhavnagar", "Gujarat", "West", "R. Mehta"),
          ("S02", "RetailMart Ahmedabad Mall", "Ahmedabad", "Gujarat", "West", "K. Shah"),
          ("S03", "RetailMart Surat City", "Surat", "Gujarat", "West", "P. Desai"),
          ("S04", "RetailMart Mumbai Andheri", "Mumbai", "Maharashtra", "West", "S. Patil"),
          ("S05", "RetailMart Delhi Connaught", "Delhi", "Delhi", "North", "A. Verma"),
          ("S06", "RetailMart Chennai T Nagar", "Chennai", "Tamil Nadu", "South", "V. Raman"),
          ("S07", "RetailMart Bengaluru Indiranagar", "Bengaluru", "Karnataka", "South", "N. Rao"),
          ("S08", "RetailMart Kolkata Park Street", "Kolkata", "West Bengal", "East", "D. Banerjee")]
STORE_W = [0.16, 0.16, 0.13, 0.17, 0.13, 0.09, 0.10, 0.06]

# ---------------- customers ----------------
FIRST = ["Aarav", "Vivaan", "Aditya", "Riya", "Ananya", "Isha", "Karan", "Meera", "Nikhil", "Pooja", "Rahul", "Sneha", "Tanvi", "Yash", "Zoya", "Dev", "Kavya", "Harsh", "Neha", "Om"]
LAST = ["Shah", "Patel", "Mehta", "Desai", "Joshi", "Sharma", "Verma", "Iyer", "Reddy", "Nair", "Das", "Singh", "Kumar", "Gupta", "Trivedi"]
CITIES = [("Bhavnagar", "Gujarat"), ("Ahmedabad", "Gujarat"), ("Surat", "Gujarat"), ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"),
          ("Chennai", "Tamil Nadu"), ("Bengaluru", "Karnataka"), ("Kolkata", "West Bengal")]
NCUST = 400
customers = []
for i in range(1, NCUST + 1):
    cid = f"C{i:04d}"
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    city, state = rng.choices(CITIES, weights=STORE_W)[0]
    gender = rng.choice(["Male", "Female"])
    by = rng.randint(1958, 2005)
    birth = date(by, rng.randint(1, 12), rng.randint(1, 28))
    signup = date(rng.randint(2019, 2024), rng.randint(1, 12), rng.randint(1, 28))
    email = f"{name.lower().replace(' ', '.')}{rng.randint(1, 99)}@example.com"
    customers.append([cid, name, email, city, state, gender, birth.isoformat(), signup.isoformat()])

# inject quality problems into customer extract
dirty = []
for c in customers:
    c = c[:]
    r = rng.random()
    if r < 0.05: c[3] = ""                                        # missing city
    if rng.random() < 0.04: c[2] = c[2].replace("@", "")         # invalid e-mail
    if rng.random() < 0.30: c[5] = {"Male": rng.choice(["M", "male", "MALE"]), "Female": rng.choice(["F", "female", "FEMALE"])}[c[5]]
    if rng.random() < 0.15: c[1] = "  " + c[1].upper() + " "     # casing / spaces
    if rng.random() < 0.10: c[4] = {"Gujarat": "GJ", "Maharashtra": "MH", "Tamil Nadu": "TN", "Karnataka": "KA", "West Bengal": "WB", "Delhi": "DL"}[c[4]]
    dirty.append(c)
dups = rng.sample(dirty, int(0.03 * len(dirty)))                  # duplicate customer records
dirty += [d[:] for d in dups]
rng.shuffle(dirty)

# ---------------- transactions ----------------
THEMES = [  # (weight, mandatory items, optional items with probability)
    (0.20, ["P001", "P002", "P003"], [("P004", .45), ("P005", .30)]),                 # breakfast basket
    (0.14, ["P011", "P012"], [("P013", .35), ("P014", .20)]),                          # snacking
    (0.06, ["P017", "P018"], [("P019", .40), ("P020", .35)]),                          # laptop bundle
    (0.06, ["P023", "P024", "P025"], [("P026", .45), ("P022", .20)]),                  # smartphone bundle
    (0.10, ["P027", "P028", "P029"], [("P030", .35), ("P031", .25)]),                  # personal care
    (0.12, ["P006", "P007", "P010"], [("P008", .50), ("P009", .20)]),                  # staples
    (0.06, ["P014", "P015", "P016"], [("P011", .25)]),                                 # pasta night
    (0.06, ["P032", "P033"], [("P036", .30), ("P035", .20)]),                          # home cleaning
]
START, END = date(2024, 1, 1), date(2025, 12, 31)
NDAYS = (END - START).days + 1
all_pid = [p[0] for p in PRODUCTS]
day_w = []
for k in range(NDAYS):
    d = START + timedelta(days=k)
    w = 1.0 + (0.15 if d.weekday() >= 5 else 0) + (0.45 if (d.month in (10, 11)) else 0) + 0.25 * (d.year - 2024)
    day_w.append(w)
day_w = np.array(day_w) / sum(day_w)

rows = []
inv_no = 0
for _ in range(1500):
    inv_no += 1
    d = START + timedelta(days=int(nrg.choice(NDAYS, p=day_w)))
    cust = f"C{rng.randint(1, NCUST):04d}"
    store = rng.choices([s[0] for s in STORES], weights=STORE_W)[0]
    r = rng.random(); acc = 0; items = None
    for w, must, opt in THEMES:
        acc += w
        if r < acc:
            items = list(must) + [p for p, pr in opt if rng.random() < pr]
            break
    if items is None:
        items = rng.sample(all_pid, rng.randint(1, 4))
    if rng.random() < 0.35:                                         # extra random item
        items.append(rng.choice(all_pid))
    items = list(dict.fromkeys(items))
    pay = rng.choices(["UPI", "Cash", "Card", "Wallet"], weights=[.45, .25, .22, .08])[0]
    seasonal_disc = 10 if d.month in (10, 11) else rng.choice([0, 0, 0, 5, 10])
    for ln, pid in enumerate(items, start=1):
        qty = 1 if CAT[pid] == "Electronics" else rng.choice([1, 1, 1, 2, 2, 3])
        rows.append([f"INV{inv_no:05d}", ln, d, cust, pid, store, qty, PRICE[pid], seasonal_disc if rng.random() < .8 else 0, pay])

# inject problems
def fmt_date(d):
    k = rng.random()
    if k < 0.70: return d.isoformat()
    if k < 0.85: return d.strftime("%d-%m-%Y")
    return d.strftime("%Y/%m/%d")

raw = []
for r in rows:
    r = r[:]
    r[2] = fmt_date(r[2])
    if rng.random() < 0.03: r[7] = f"Rs. {r[7]}"                    # price stored as text
    if rng.random() < 0.01: r[7] = ""                              # missing price
    if rng.random() < 0.01: r[6] = ""                              # missing quantity
    if rng.random() < 0.005: r[6] = -abs(r[6] if r[6] != "" else 1)  # negative quantity (returns keyed wrongly)
    if rng.random() < 0.01: r[3] = f"C{rng.randint(900, 999):04d}"  # orphan customer
    if rng.random() < 0.003: r[5] = ""                              # missing store
    if rng.random() < 0.003: r[2] = "2026-03-15"                    # future date
    if rng.random() < 0.002: r[8] = 95                              # impossible discount
    r[9] = rng.choice([r[9], r[9].lower(), r[9].upper()]) if rng.random() < .3 else r[9]
    raw.append(r)
dup_rows = rng.sample(raw, int(0.02 * len(raw)))
raw += [d[:] for d in dup_rows]
rng.shuffle(raw)

def write(name, header, data):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(data)

write("customers.csv", ["customer_id", "name", "email", "city", "state", "gender", "birth_date", "signup_date"], dirty)
write("products.csv", ["product_id", "product_name", "category", "subcategory", "brand", "list_price"], PRODUCTS)
write("stores.csv", ["store_id", "store_name", "city", "state", "region", "manager"], STORES)
write("sales_raw.csv", ["invoice_id", "line_no", "order_date", "customer_id", "product_id", "store_id", "quantity", "unit_price", "discount_pct", "payment_mode"], raw)
print("customers", len(dirty), "| products", len(PRODUCTS), "| stores", len(STORES), "| sales lines", len(raw), "| invoices", inv_no)
