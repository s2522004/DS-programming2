import sqlite3
import random

DB_NAME = "real_estate.db"

# 国土交通省不動産情報ライブラリAPI
# 注: 実際のAPIエンドポイントは不動産取引価格情報のCSVダウンロードまたはWebページからのスクレイピングが必要
# ここでは教育目的のため、サンプルデータを生成します

def generate_sample_data():
    """
    実際のAPIが利用できない場合のサンプルデータ生成
    実際の国土交通省データの特徴を模擬
    """
    properties = []
    
    # 東京23区のデータ（都市部）
    tokyo_wards = ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", 
                   "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
                   "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"]
    
    for _ in range(150):
        ward = random.choice(tokyo_wards)
        floor_area = random.uniform(20, 150)  # 20-150㎡
        # 都市部は単価が高い: 50万円/㎡ - 150万円/㎡
        unit_price = random.uniform(500000, 1500000)
        trade_price = int(floor_area * unit_price)
        
        properties.append({
            'prefecture': '東京都',
            'city': ward,
            'district': f'{ward}○○',
            'trade_price': trade_price,
            'floor_area': round(floor_area, 2),
            'unit_price': round(unit_price, 2),
            'building_year': random.randint(1990, 2024),
            'structure': random.choice(['RC', 'SRC', '木造', '鉄骨造']),
            'use_type': random.choice(['住宅', '店舗', '事務所', '住宅・店舗']),
            'land_shape': random.choice(['ほぼ長方形', '不整形', 'ほぼ正方形', '台形']),
            'frontage': round(random.uniform(4, 20), 1),
            'city_planning': random.choice(['商業地域', '準工業地域', '第一種住居地域', '第二種住居地域']),
            'trade_period': f'2024年第{random.randint(1,4)}四半期',
            'region_type': '都市部'
        })
    
    # 地方都市のデータ
    local_cities = [
        ('福岡県', '福岡市博多区'),
        ('福岡県', '福岡市中央区'),
        ('北海道', '札幌市中央区'),
        ('北海道', '札幌市北区'),
        ('愛知県', '名古屋市中区'),
        ('大阪府', '大阪市北区'),
        ('宮城県', '仙台市青葉区'),
        ('広島県', '広島市中区'),
    ]
    
    for _ in range(150):
        prefecture, city = random.choice(local_cities)
        floor_area = random.uniform(30, 180)  # 30-180㎡
        # 地方は単価が低い: 15万円/㎡ - 60万円/㎡
        unit_price = random.uniform(150000, 600000)
        trade_price = int(floor_area * unit_price)
        
        properties.append({
            'prefecture': prefecture,
            'city': city,
            'district': f'{city}○○',
            'trade_price': trade_price,
            'floor_area': round(floor_area, 2),
            'unit_price': round(unit_price, 2),
            'building_year': random.randint(1985, 2024),
            'structure': random.choice(['RC', 'SRC', '木造', '鉄骨造', 'ブロック造']),
            'use_type': random.choice(['住宅', '店舗', '事務所', '工場', '倉庫']),
            'land_shape': random.choice(['ほぼ長方形', '不整形', 'ほぼ正方形', '台形', '袋地等']),
            'frontage': round(random.uniform(5, 25), 1),
            'city_planning': random.choice(['商業地域', '準工業地域', '第一種住居地域', '工業地域', '市街化調整区域']),
            'trade_period': f'2024年第{random.randint(1,4)}四半期',
            'region_type': '地方'
        })
    
    return properties

def save_to_db(properties):
    """データをデータベースに保存"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    for prop in properties:
        cur.execute("""
            INSERT INTO properties (
                prefecture, city, district, trade_price, floor_area, unit_price,
                building_year, structure, use_type, land_shape, frontage,
                city_planning, trade_period, region_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prop['prefecture'], prop['city'], prop['district'], prop['trade_price'],
            prop['floor_area'], prop['unit_price'], prop['building_year'],
            prop['structure'], prop['use_type'], prop['land_shape'], prop['frontage'],
            prop['city_planning'], prop['trade_period'], prop['region_type']
        ))
    
    conn.commit()
    conn.close()
    print(f"データベースに {len(properties)} 件のデータを保存しました。")

if __name__ == "__main__":
    print("=" * 60)
    print("国土交通省不動産情報ライブラリ データ取得")
    print("=" * 60)
    print()
    print("【クレジット表示】")
    print("このサービスは、国土交通省の不動産情報ライブラリのAPI機能を")
    print("使用していますが、提供情報の最新性、正確性、完全性等が")
    print("保証されたものではありません。")
    print()
    print("=" * 60)
    print()
    
    print("サンプルデータを生成中...")
    properties = generate_sample_data()
    
    print(f"取得件数: {len(properties)} 件")
    print(f"  - 都市部（東京23区）: {sum(1 for p in properties if p['region_type'] == '都市部')} 件")
    print(f"  - 地方都市: {sum(1 for p in properties if p['region_type'] == '地方')} 件")
    print()
    
    print("データベースに保存中...")
    save_to_db(properties)
    
    print()
    print("完了しました！")
