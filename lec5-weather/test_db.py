import sqlite3

DB_NAME = "weather.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. 地域マスタテーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL
        )
    """)
    
    # 2. 天気予報テーブル作成
    # UNIQUE(area_code, forecast_date) にすることで、
    # 同じ地域の同じ日のデータが重複して登録されるのを防ぎます
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            weather TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(area_code, forecast_date),
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        )
    """)
    
    conn.commit()
    conn.close()

# 最初に一度だけ実行する
if __name__ == "__main__":
    init_db()