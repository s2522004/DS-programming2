import sqlite3

DB_NAME = "real_estate.db"

# データベース接続
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# テーブル作成
cur.execute("""
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prefecture TEXT NOT NULL,
    city TEXT,
    district TEXT,
    trade_price INTEGER,
    floor_area REAL,
    unit_price REAL,
    building_year INTEGER,
    structure TEXT,
    use_type TEXT,
    land_shape TEXT,
    frontage REAL,
    city_planning TEXT,
    trade_period TEXT,
    region_type TEXT
)
""")

conn.commit()
conn.close()

print(f"データベース '{DB_NAME}' を作成しました。")
print("テーブル 'properties' が正常に作成されました。")
