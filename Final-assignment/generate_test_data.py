import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "weworkremotely_jobs.db"

# テストデータのテンプレート
test_jobs = [
    # Senior職で福利厚生あり
    {
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "category": "Programming",
        "description": "We offer MacBook Pro for all engineers and unlimited PTO. Join our annual company retreat in Bali.",
        "is_senior": True,
        "has_benefits": True
    },
    {
        "title": "Lead Product Designer",
        "company": "DesignHub",
        "category": "Design",
        "description": "MacBook provided, flexible vacation policy with unlimited time off, and yearly team retreats.",
        "is_lead": True,
        "has_benefits": True
    },
    {
        "title": "Principal DevOps Engineer",
        "company": "CloudNine",
        "category": "DevOps",
        "description": "Top-tier equipment including MacBook, unlimited vacation, and amazing company retreats twice a year.",
        "is_senior": True,
        "has_benefits": True
    },
    # Senior職で福利厚生なし
    {
        "title": "Senior Data Analyst",
        "company": "DataCo",
        "category": "Data Analysis",
        "description": "Join our growing team. Competitive salary and standard benefits package.",
        "is_senior": True,
        "has_benefits": False
    },
    {
        "title": "Staff Engineer",
        "company": "EngineerPro",
        "category": "Programming",
        "description": "Work on cutting-edge projects. Standard benefits included.",
        "is_senior": True,
        "has_benefits": False
    },
    # Mid-level職で福利厚生あり
    {
        "title": "Full Stack Developer",
        "company": "WebDev Inc",
        "category": "Programming",
        "description": "We provide MacBook laptops and have unlimited PTO policy.",
        "is_senior": False,
        "has_benefits": True
    },
    {
        "title": "Product Manager",
        "company": "ProductFirst",
        "category": "Product",
        "description": "MacBook Pro, unlimited vacation, and annual team retreats to amazing destinations.",
        "is_lead": False,
        "has_benefits": True
    },
    # Mid-level職で福利厚生なし
    {
        "title": "Software Developer",
        "company": "CodeFactory",
        "category": "Programming",
        "description": "Build amazing products with our team. Competitive compensation package.",
        "is_senior": False,
        "has_benefits": False
    },
    {
        "title": "UX Designer",
        "company": "UXStudio",
        "category": "Design",
        "description": "Create beautiful user experiences. Standard benefits and 401k.",
        "is_senior": False,
        "has_benefits": False
    },
    # Junior職で福利厚生なし（予想通り）
    {
        "title": "Junior Developer",
        "company": "StartupXYZ",
        "category": "Programming",
        "description": "Great learning opportunity for new graduates. Standard benefits.",
        "is_junior": True,
        "has_benefits": False
    },
    {
        "title": "Entry Level Marketing Coordinator",
        "company": "MarketPro",
        "category": "Marketing",
        "description": "Perfect for recent graduates. Health insurance and paid time off.",
        "is_entry": True,
        "has_benefits": False
    },
    {
        "title": "Associate Designer",
        "company": "CreativeAgency",
        "category": "Design",
        "description": "Entry-level position with room for growth. Standard benefits package.",
        "is_junior": True,
        "has_benefits": False
    },
    # Junior職で福利厚生あり（稀なケース）
    {
        "title": "Junior Software Engineer",
        "company": "TechStartup",
        "category": "Programming",
        "description": "Even juniors get MacBooks! We believe in investing in our people with unlimited PTO.",
        "is_junior": True,
        "has_benefits": True
    },
]

def generate_test_data():
    """テストデータを生成してデータベースに挿入"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # 既存のデータをクリア（テスト用）
    cur.execute("DELETE FROM jobs")
    
    # より多くのテストデータを生成
    for i, job_template in enumerate(test_jobs):
        # 複数のバリエーションを生成
        for j in range(5):  # 各テンプレートから5つのジョブを生成
            title = job_template["title"]
            if j > 0:
                title = f"{title} #{j+1}"
            
            company = f"{job_template['company']} {j+1}" if j > 0 else job_template['company']
            
            description = job_template["description"]
            
            # 福利厚生の検出
            desc_lower = description.lower()
            has_macbook = "macbook" in desc_lower or "laptop provided" in desc_lower
            has_company_retreat = "retreat" in desc_lower or "company trip" in desc_lower
            has_unlimited_pto = "unlimited" in desc_lower and ("pto" in desc_lower or "vacation" in desc_lower or "time off" in desc_lower)
            has_premium_benefits = has_macbook or has_company_retreat or has_unlimited_pto
            
            # 職位レベルの検出
            title_lower = title.lower()
            is_senior = "senior" in title_lower or "principal" in title_lower or "staff" in title_lower
            is_lead = "lead" in title_lower or "manager" in title_lower or "director" in title_lower or "head" in title_lower
            is_junior = "junior" in title_lower or "associate" in title_lower
            is_entry = "entry" in title_lower or "intern" in title_lower or "graduate" in title_lower
            
            # ランダムな日付
            days_ago = random.randint(1, 60)
            posted_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            url = f"https://weworkremotely.com/remote-jobs/test-job-{i}-{j}"
            
            cur.execute("""
                INSERT INTO jobs (
                    title, company, category, job_type, location,
                    posted_date, url, description,
                    has_macbook, has_company_retreat, has_unlimited_pto, has_premium_benefits,
                    is_senior, is_lead, is_junior, is_entry
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                company,
                job_template["category"],
                "Full-time",
                "Remote",
                posted_date,
                url,
                description,
                has_macbook,
                has_company_retreat,
                has_unlimited_pto,
                has_premium_benefits,
                is_senior,
                is_lead,
                is_junior,
                is_entry
            ))
    
    conn.commit()
    
    # 統計情報を表示
    cur.execute("SELECT COUNT(*) FROM jobs")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE has_premium_benefits = 1")
    with_benefits = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE is_senior = 1 OR is_lead = 1")
    senior_lead = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE is_junior = 1 OR is_entry = 1")
    junior_entry = cur.fetchone()[0]
    
    conn.close()
    
    print("=" * 60)
    print("テストデータ生成完了")
    print("=" * 60)
    print(f"総求人数: {total}")
    print(f"魅力的福利厚生あり: {with_benefits} ({with_benefits/total*100:.1f}%)")
    print(f"Senior/Lead職: {senior_lead} ({senior_lead/total*100:.1f}%)")
    print(f"Junior/Entry職: {junior_entry} ({junior_entry/total*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    generate_test_data()
