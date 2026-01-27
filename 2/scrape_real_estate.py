import sqlite3
import time
import requests
from bs4 import BeautifulSoup

DB_NAME = "countries.db"
BASE_URL = "https://www.scrapethissite.com/pages/simple/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def get_countries():
    """
    scrapethissite.comから国データをスクレイピング
    このサイトは教育目的のスクレイピング練習用に作られています
    """
    countries = []
    url = BASE_URL
    
    print(f"Fetching: {url}")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # 国の情報を含むdivを取得
    country_items = soup.select("div.country")
    
    for item in country_items:
        # 国名
        name_tag = item.select_one("h3.country-name")
        name = name_tag.text.strip() if name_tag else "Unknown"
        
        # 首都
        capital_tag = item.select_one("span.country-capital")
        capital = capital_tag.text.strip() if capital_tag else ""
        
        # 人口
        population_tag = item.select_one("span.country-population")
        if population_tag:
            pop_text = population_tag.text.strip().replace(",", "")
            population = int(pop_text) if pop_text else 0
        else:
            population = 0
        
        # 面積
        area_tag = item.select_one("span.country-area")
        if area_tag:
            area_text = area_tag.text.strip().replace(",", "")
            area = float(area_text) if area_text else 0
        else:
            area = 0
        
        # 人口密度を計算
        population_density = population / area if area > 0 else 0
        
        # 地域を推定
        if any(x in name for x in ['United States', 'Canada', 'Mexico', 'Cuba', 'Jamaica']):
            region = '北米'
        elif any(x in name for x in ['China', 'Japan', 'Korea', 'India', 'Thailand', 'Vietnam', 
                                      'Indonesia', 'Philippines', 'Malaysia', 'Singapore']):
            region = 'アジア'
        elif any(x in name for x in ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom',
                                      'Poland', 'Netherlands', 'Belgium', 'Sweden', 'Norway']):
            region = 'ヨーロッパ'
        elif any(x in name for x in ['Brazil', 'Argentina', 'Chile', 'Peru', 'Colombia', 'Venezuela']):
            region = '南米'
        elif any(x in name for x in ['Egypt', 'Nigeria', 'South Africa', 'Kenya', 'Ethiopia']):
            region = 'アフリカ'
        elif any(x in name for x in ['Australia', 'New Zealand']):
            region = 'オセアニア'
        else:
            region = 'その他'
        
        countries.append((name, capital, population, area, round(population_density, 2), region))
        
        time.sleep(0.1)  # polite wait
    
    return countries


def save_to_db(countries):
    """データをデータベースに保存"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # 既存データを削除
    cur.execute("DELETE FROM countries")
    
    cur.executemany(
        "INSERT INTO countries (name, capital, population, area, population_density, region) VALUES (?, ?, ?, ?, ?, ?)",
        countries
    )
    conn.commit()
    conn.close()
    print("Saved to DB.")


if __name__ == "__main__":
    data = get_countries()
    print("Fetched:", len(data))
    save_to_db(data)
