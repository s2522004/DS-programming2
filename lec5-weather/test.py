def get_forecasts_from_db(area_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 日付順に取得
    cursor.execute("""
        SELECT forecast_date, weather 
        FROM forecasts 
        WHERE area_code = ? 
        ORDER BY forecast_date
    """, (area_code,))
    
    rows = cursor.fetchall() # [(日付, 天気), (日付, 天気)...] というリストが返る
    conn.close()
    return rows