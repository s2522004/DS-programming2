import sqlite3
import time
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DB_NAME = "weworkremotely_jobs.db"
BASE_URL = "https://weworkremotely.com"

# 主要なカテゴリページ
CATEGORY_URLS = [
    "/categories/remote-programming-jobs",
    "/categories/remote-devops-sysadmin-jobs",
    "/categories/remote-design-jobs",
    "/categories/remote-product-jobs",
    "/categories/remote-marketing-jobs",
    "/categories/remote-customer-support-jobs",
    "/categories/remote-sales-jobs",
    "/categories/remote-writing-jobs",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_job_listings(soup, category):
    """求人リストからジョブ情報を抽出"""
    jobs = []
    
    # We Work Remotelyの求人リストセレクタ
    job_items = soup.select("li.feature, section#category-jobs article, li article")
    
    print(f"  {len(job_items)} 件の求人要素を発見")
    
    for item in job_items:
        try:
            # タイトルとURLを取得
            title_tag = item.select_one("span.title, h2 a, a.title")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            
            # URLを取得（親のaタグまたは直接のhref）
            link_tag = item.find_parent("a") or item.select_one("a")
            job_url = ""
            if link_tag and link_tag.get("href"):
                job_url = link_tag.get("href")
                if job_url and not job_url.startswith("http"):
                    job_url = BASE_URL + job_url
            
            if not job_url or not title:
                continue
            
            # 会社名を取得
            company_tag = item.select_one("span.company, .company-name, a.company")
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            
            # ロケーション/地域情報
            region_tag = item.select_one("span.region, .region-name")
            region = region_tag.get_text(strip=True) if region_tag else "Remote"
            
            jobs.append({
                "title": title,
                "company": company,
                "category": category,
                "region": region,
                "url": job_url,
            })
            
        except Exception as e:
            print(f"    ジョブアイテムの解析エラー: {e}")
            continue
    
    return jobs

def scrape_job_detail(job_url):
    """個別の求人詳細ページから情報を取得"""
    try:
        print(f"    詳細取得: {job_url}")
        response = requests.get(job_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 求人詳細を取得
        description_tag = soup.select_one(".listing-container, #job-listing-show-container, .job-description")
        description = description_tag.get_text(strip=True, separator=" ") if description_tag else ""
        
        # ジョブタイプ
        job_type_tag = soup.select_one(".job-type, .listing-tag")
        job_type = job_type_tag.get_text(strip=True) if job_type_tag else "Full-time"
        
        # 投稿日
        posted_tag = soup.select_one("time, .posted-date")
        posted_date = ""
        if posted_tag:
            posted_date = posted_tag.get("datetime", "") or posted_tag.get_text(strip=True)
        
        # 給与情報（説明文から抽出）
        salary_patterns = [
            r'\$[\d,]+\s*[-–]\s*\$?[\d,]+[kK]?',
            r'\$[\d,]+[kK]?',
            r'€[\d,]+\s*[-–]\s*€?[\d,]+[kK]?',
            r'£[\d,]+\s*[-–]\s*£?[\d,]+[kK]?'
        ]
        salary_info = ""
        for pattern in salary_patterns:
            match = re.search(pattern, description)
            if match:
                salary_info = match.group(0)
                break
        
        return {
            "description": description,
            "job_type": job_type,
            "posted_date": posted_date,
            "salary_info": salary_info,
        }
    except Exception as e:
        print(f"    詳細取得エラー: {e}")
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
    
    # 福利厚生の検出（より広範なキーワード）
    has_macbook = any(keyword in combined for keyword in [
        "macbook", "mac book", "apple laptop", "laptop provided",
        "company laptop", "equipment provided", "work equipment"
    ])
    
    has_company_retreat = any(keyword in combined for keyword in [
        "company retreat", "team retreat", "annual retreat", 
        "offsites", "team offsite", "company trip", "team gathering",
        "in-person gathering", "team meetup", "yearly gathering"
    ])
    
    has_unlimited_pto = any(keyword in combined for keyword in [
        "unlimited pto", "unlimited vacation", "unlimited time off",
        "unlimited paid time off", "flexible vacation", "unlimited leave",
        "flexible time off", "unlimited days off"
    ])
    
    # 包括的な福利厚生
    has_premium_benefits = has_macbook or has_company_retreat or has_unlimited_pto
    
    # タイトル分析（職位レベル）
    is_senior = any(keyword in title_lower for keyword in [
        "senior", "sr.", "sr ", "principal", "staff", "lead"
    ])
    
    is_lead = any(keyword in title_lower for keyword in [
        "lead", "head of", "director", "manager", "vp", "chief", "team lead"
    ])
    
    is_junior = any(keyword in title_lower for keyword in [
        "junior", "jr.", "jr ", "associate", "early career"
    ])
    
    is_entry = any(keyword in title_lower for keyword in [
        "entry", "entry-level", "entry level", "intern", "graduate", "trainee"
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

def scrape_category(category_url, max_jobs=30):
    """特定のカテゴリから求人を取得"""
    jobs = []
    category_name = category_url.split("/")[-1].replace("remote-", "").replace("-jobs", "")
    
    try:
        url = BASE_URL + category_url
        print(f"\nスクレイピング中: {url}")
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        page_jobs = extract_job_listings(soup, category_name)
        
        if not page_jobs:
            print(f"  求人が見つかりませんでした")
            return jobs
        
        print(f"  {len(page_jobs)} 件の求人を発見")
        
        # 最大数まで取得
        for job in page_jobs[:max_jobs]:
            jobs.append(job)
        
        # 丁寧な待機時間
        time.sleep(3)
        
    except Exception as e:
        print(f"カテゴリスクレイピングエラー: {e}")
    
    return jobs

def save_to_db(jobs):
    """求人データをデータベースに保存"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    saved_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, job in enumerate(jobs, 1):
        try:
            print(f"\n[{i}/{len(jobs)}] 処理中: {job['title'][:50]}...")
            
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
                job["region"],
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
                print(f"  ✓ 保存完了")
            else:
                skipped_count += 1
                print(f"  - スキップ（重複）")
            
            # 定期的にコミット
            if i % 10 == 0:
                conn.commit()
                print(f"\n--- 進捗: {saved_count}件保存, {skipped_count}件スキップ ---")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ エラー: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"保存完了: {saved_count} 件の新規求人")
    print(f"スキップ: {skipped_count} 件の重複求人")
    print(f"エラー: {error_count} 件")
    print(f"{'='*60}")

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("We Work Remotely 求人スクレイピング開始")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_jobs = []
    
    # 各カテゴリから求人を取得
    for category_url in CATEGORY_URLS:
        print(f"\n{'='*60}")
        print(f"カテゴリ: {category_url}")
        print(f"{'='*60}")
        
        jobs = scrape_category(category_url, max_jobs=20)
        all_jobs.extend(jobs)
        
        print(f"\nこのカテゴリで {len(jobs)} 件取得")
        print(f"累計: {len(all_jobs)} 件")
        
        # カテゴリ間の待機
        time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"総取得数: {len(all_jobs)} 件")
    print(f"{'='*60}")
    
    # 重複URLを削除
    unique_jobs = []
    seen_urls = set()
    for job in all_jobs:
        if job["url"] not in seen_urls and job["url"]:
            unique_jobs.append(job)
            seen_urls.add(job["url"])
    
    print(f"重複削除後: {len(unique_jobs)} 件")
    
    # データベースに保存
    if unique_jobs:
        print(f"\n{'='*60}")
        print("データベースに保存中...")
        print(f"{'='*60}")
        save_to_db(unique_jobs)
    else:
        print("\n警告: 取得できた求人がありません")
    
    print(f"\n{'='*60}")
    print("スクレイピング完了")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
