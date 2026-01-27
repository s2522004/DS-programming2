import sqlite3
import time
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DB_NAME = "weworkremotely_jobs.db"
BASE_URL = "https://weworkremotely.com"
CATEGORIES = [
    "/remote-jobs/search?term=programming",
    "/remote-jobs/search?term=design",
    "/remote-jobs/search?term=marketing",
    "/remote-jobs/search?term=customer-support",
    "/remote-jobs/search?term=sales",
    "/remote-jobs/search?term=product",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_job_listings(soup):
    """求人リストからジョブ情報を抽出"""
    jobs = []
    
    # We Work Remotelyの一般的な求人リストのセレクタ
    # 実際のサイト構造に応じて調整が必要
    job_items = soup.select("li.feature, li article, section.jobs li")
    
    for item in job_items:
        try:
            # タイトルとURLを取得
            title_tag = item.select_one("a.title, h2 a, .job-title a, a[href*='/remote-jobs/']")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            job_url = title_tag.get("href", "")
            if job_url and not job_url.startswith("http"):
                job_url = BASE_URL + job_url
            
            # 会社名を取得
            company_tag = item.select_one(".company, .company-name, span.company")
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            
            # カテゴリを取得
            category_tag = item.select_one(".region, .category, span.region")
            category = category_tag.get_text(strip=True) if category_tag else "Unknown"
            
            # ロケーション情報
            location_tag = item.select_one(".location, .region-name")
            location = location_tag.get_text(strip=True) if location_tag else "Remote"
            
            jobs.append({
                "title": title,
                "company": company,
                "category": category,
                "location": location,
                "url": job_url,
            })
            
        except Exception as e:
            print(f"ジョブアイテムの解析エラー: {e}")
            continue
    
    return jobs

def scrape_job_detail(job_url):
    """個別の求人詳細ページから情報を取得"""
    try:
        print(f"  詳細取得中: {job_url}")
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 求人詳細を取得
        description_tag = soup.select_one(".listing-container, .job-description, #job-listing-show-container")
        description = description_tag.get_text(strip=True) if description_tag else ""
        
        # ジョブタイプ
        job_type_tag = soup.select_one(".job-type, .listing-tag")
        job_type = job_type_tag.get_text(strip=True) if job_type_tag else "Full-time"
        
        # 投稿日
        posted_tag = soup.select_one("time, .posted-date")
        posted_date = posted_tag.get("datetime", "") or posted_tag.get_text(strip=True) if posted_tag else ""
        
        # 給与情報
        salary_match = re.search(r'\$[\d,]+\s*-?\s*\$?[\d,]*[kK]?', description)
        salary_info = salary_match.group(0) if salary_match else ""
        
        return {
            "description": description,
            "job_type": job_type,
            "posted_date": posted_date,
            "salary_info": salary_info,
        }
    except Exception as e:
        print(f"  詳細取得エラー: {e}")
        return {
            "description": "",
            "job_type": "Full-time",
            "posted_date": "",
            "salary_info": "",
        }

def analyze_job(title, description):
    """求人のタイトルと説明文を分析してフラグを設定"""
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = title_lower + " " + desc_lower
    
    # 福利厚生の検出
    has_macbook = any(keyword in combined for keyword in [
        "macbook", "mac book", "apple laptop", "laptop provided"
    ])
    
    has_company_retreat = any(keyword in combined for keyword in [
        "company retreat", "team retreat", "annual retreat", 
        "offsites", "team offsite", "company trip"
    ])
    
    has_unlimited_pto = any(keyword in combined for keyword in [
        "unlimited pto", "unlimited vacation", "unlimited time off",
        "unlimited paid time off", "flexible vacation", "unlimited leave"
    ])
    
    # 包括的な福利厚生（上記のいずれかを含む）
    has_premium_benefits = has_macbook or has_company_retreat or has_unlimited_pto
    
    # タイトル分析（職位レベル）
    is_senior = any(keyword in title_lower for keyword in [
        "senior", "sr.", "sr ", "principal", "staff"
    ])
    
    is_lead = any(keyword in title_lower for keyword in [
        "lead", "head of", "director", "manager", "vp", "chief"
    ])
    
    is_junior = any(keyword in title_lower for keyword in [
        "junior", "jr.", "jr ", "associate"
    ])
    
    is_entry = any(keyword in title_lower for keyword in [
        "entry", "entry-level", "entry level", "intern", "graduate"
    ])
    
    return {
        "has_macbook": has_macbook,
        "has_company_retreat": has_company_retreat,
        "has_unlimited_pto": has_unlimited_pto,
        "has_premium_benefits": has_premium_benefits,
        "is_senior": is_senior,
        "is_lead": is_lead,
        "is_junior": is_junior,
        "is_entry": is_entry,
    }

def scrape_jobs_from_category(category_url, max_pages=5):
    """特定のカテゴリから求人を取得"""
    jobs = []
    
    for page in range(1, max_pages + 1):
        try:
            if page == 1:
                url = BASE_URL + category_url
            else:
                # ページネーション（サイトによって異なる）
                url = f"{BASE_URL}{category_url}?page={page}"
            
            print(f"スクレイピング中: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            page_jobs = extract_job_listings(soup)
            
            if not page_jobs:
                print(f"  {page}ページ目に求人が見つかりませんでした。")
                break
            
            print(f"  {len(page_jobs)}件の求人を発見")
            jobs.extend(page_jobs)
            
            # 丁寧な待機時間
            time.sleep(2)
            
        except Exception as e:
            print(f"カテゴリスクレイピングエラー: {e}")
            break
    
    return jobs

def save_to_db(jobs):
    """求人データをデータベースに保存"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    saved_count = 0
    skipped_count = 0
    
    for job in jobs:
        try:
            # 詳細情報を取得
            if job["url"]:
                detail = scrape_job_detail(job["url"])
                time.sleep(2)  # 丁寧な待機
            else:
                detail = {
                    "description": "",
                    "job_type": "Full-time",
                    "posted_date": "",
                    "salary_info": "",
                }
            
            # 分析フラグを取得
            analysis = analyze_job(job["title"], detail["description"])
            
            # データベースに挿入
            cur.execute("""
                INSERT OR IGNORE INTO jobs (
                    title, company, category, job_type, location,
                    posted_date, url, description, salary_info,
                    has_macbook, has_company_retreat, has_unlimited_pto, 
                    has_premium_benefits, is_senior, is_lead, is_junior, is_entry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["title"],
                job["company"],
                job["category"],
                detail["job_type"],
                job["location"],
                detail["posted_date"],
                job["url"],
                detail["description"],
                detail["salary_info"],
                analysis["has_macbook"],
                analysis["has_company_retreat"],
                analysis["has_unlimited_pto"],
                analysis["has_premium_benefits"],
                analysis["is_senior"],
                analysis["is_lead"],
                analysis["is_junior"],
                analysis["is_entry"],
            ))
            
            if cur.rowcount > 0:
                saved_count += 1
                print(f"  保存: {job['title']} - {job['company']}")
            else:
                skipped_count += 1
                print(f"  スキップ（重複）: {job['title']}")
                
        except Exception as e:
            print(f"データベース保存エラー: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n保存完了: {saved_count}件の新規求人")
    print(f"スキップ: {skipped_count}件の重複求人")

def main():
    """メイン実行関数"""
    print("=== We Work Remotely 求人スクレイピング開始 ===\n")
    
    all_jobs = []
    
    # 各カテゴリから求人を取得
    for category in CATEGORIES:
        print(f"\n--- カテゴリ: {category} ---")
        jobs = scrape_jobs_from_category(category, max_pages=3)
        all_jobs.extend(jobs)
        print(f"このカテゴリで {len(jobs)} 件取得")
        time.sleep(3)  # カテゴリ間の待機
    
    print(f"\n総取得数: {len(all_jobs)} 件")
    
    # 重複URLを削除
    unique_jobs = []
    seen_urls = set()
    for job in all_jobs:
        if job["url"] not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(job["url"])
    
    print(f"重複削除後: {len(unique_jobs)} 件")
    
    # データベースに保存
    if unique_jobs:
        print("\n=== データベースに保存中 ===")
        save_to_db(unique_jobs)
    
    print("\n=== スクレイピング完了 ===")

if __name__ == "__main__":
    main()
