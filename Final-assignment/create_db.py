import sqlite3

DB_NAME = "weworkremotely_jobs.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# 求人情報を格納するテーブルを作成
cur.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    category TEXT,
    job_type TEXT,
    location TEXT,
    posted_date TEXT,
    url TEXT UNIQUE,
    description TEXT,
    -- 福利厚生フラグ
    has_macbook BOOLEAN DEFAULT 0,
    has_company_retreat BOOLEAN DEFAULT 0,
    has_unlimited_pto BOOLEAN DEFAULT 0,
    has_premium_benefits BOOLEAN DEFAULT 0,
    -- タイトル分析用フラグ
    is_senior BOOLEAN DEFAULT 0,
    is_lead BOOLEAN DEFAULT 0,
    is_junior BOOLEAN DEFAULT 0,
    is_entry BOOLEAN DEFAULT 0,
    -- 追加情報
    salary_info TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print(f"データベース '{DB_NAME}' を作成しました。")
