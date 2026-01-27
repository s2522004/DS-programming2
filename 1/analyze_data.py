import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

DB_NAME = "weworkremotely_jobs.db"

def load_data():
    """データベースからデータを読み込む"""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM jobs"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def analyze_hypothesis(df):
    """仮説を検証する"""
    print("=" * 80)
    print("仮説検証: 魅力的な福利厚生と職位レベルの関係")
    print("=" * 80)
    
    # データの基本情報
    print(f"\n総求人数: {len(df)}")
    print(f"\n--- 福利厚生の分布 ---")
    print(f"MacBook支給: {df['has_macbook'].sum()} 件 ({df['has_macbook'].mean()*100:.1f}%)")
    print(f"Company Retreat: {df['has_company_retreat'].sum()} 件 ({df['has_company_retreat'].mean()*100:.1f}%)")
    print(f"Unlimited PTO: {df['has_unlimited_pto'].sum()} 件 ({df['has_unlimited_pto'].mean()*100:.1f}%)")
    print(f"いずれかの魅力的福利厚生あり: {df['has_premium_benefits'].sum()} 件 ({df['has_premium_benefits'].mean()*100:.1f}%)")
    
    print(f"\n--- 職位レベルの分布 ---")
    print(f"Senior/Principal/Staff: {df['is_senior'].sum()} 件 ({df['is_senior'].mean()*100:.1f}%)")
    print(f"Lead/Manager/Director: {df['is_lead'].sum()} 件 ({df['is_lead'].mean()*100:.1f}%)")
    print(f"Junior/Associate: {df['is_junior'].sum()} 件 ({df['is_junior'].mean()*100:.1f}%)")
    print(f"Entry/Intern: {df['is_entry'].sum()} 件 ({df['is_entry'].mean()*100:.1f}%)")
    
    # 仮説検証: 福利厚生あり vs なし での Senior/Lead の割合比較
    print("\n" + "=" * 80)
    print("【仮説検証結果】")
    print("=" * 80)
    
    # 魅力的福利厚生がある求人とない求人を分類
    premium_jobs = df[df['has_premium_benefits'] == 1]
    standard_jobs = df[df['has_premium_benefits'] == 0]
    
    print(f"\n魅力的福利厚生あり: {len(premium_jobs)} 件")
    print(f"魅力的福利厚生なし: {len(standard_jobs)} 件")
    
    if len(premium_jobs) == 0 or len(standard_jobs) == 0:
        print("\n警告: データが不十分のため統計検定を実行できません")
        return
    
    # Senior または Lead の割合を計算
    premium_senior_or_lead = ((premium_jobs['is_senior'] == 1) | (premium_jobs['is_lead'] == 1)).mean()
    standard_senior_or_lead = ((standard_jobs['is_senior'] == 1) | (standard_jobs['is_lead'] == 1)).mean()
    
    print(f"\n【Senior/Leadの割合】")
    print(f"福利厚生あり: {premium_senior_or_lead*100:.1f}%")
    print(f"福利厚生なし: {standard_senior_or_lead*100:.1f}%")
    print(f"差: {(premium_senior_or_lead - standard_senior_or_lead)*100:.1f} ポイント")
    
    # カイ二乗検定
    contingency_table = pd.crosstab(
        df['has_premium_benefits'],
        ((df['is_senior'] == 1) | (df['is_lead'] == 1))
    )
    print(f"\n【クロス集計表】")
    print(contingency_table)
    
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"\n【カイ二乗検定】")
    print(f"χ² 統計量: {chi2:.4f}")
    print(f"p値: {p_value:.4f}")
    print(f"自由度: {dof}")
    
    if p_value < 0.05:
        print(f"\n結論: p値 < 0.05 のため、有意差あり（統計的に有意）")
        print("→ 魅力的福利厚生とSenior/Lead職位には統計的に有意な関係がある")
    else:
        print(f"\n結論: p値 ≥ 0.05 のため、有意差なし（統計的に有意でない）")
        print("→ 魅力的福利厚生とSenior/Lead職位には統計的に有意な関係が見られない")
    
    # Junior/Entryでの福利厚生の有無
    print(f"\n【Junior/Entry職での福利厚生】")
    junior_or_entry = df[(df['is_junior'] == 1) | (df['is_entry'] == 1)]
    print(f"Junior/Entry職の総数: {len(junior_or_entry)} 件")
    if len(junior_or_entry) > 0:
        junior_with_benefits = junior_or_entry[junior_or_entry['has_premium_benefits'] == 1]
        print(f"魅力的福利厚生あり: {len(junior_with_benefits)} 件 ({len(junior_with_benefits)/len(junior_or_entry)*100:.1f}%)")
        print(f"魅力的福利厚生なし: {len(junior_or_entry) - len(junior_with_benefits)} 件 ({(1-len(junior_with_benefits)/len(junior_or_entry))*100:.1f}%)")
    
    # 詳細な分析: 各福利厚生ごと
    print(f"\n【福利厚生別のSenior/Lead割合】")
    for benefit_col, benefit_name in [
        ('has_macbook', 'MacBook支給'),
        ('has_company_retreat', 'Company Retreat'),
        ('has_unlimited_pto', 'Unlimited PTO')
    ]:
        with_benefit = df[df[benefit_col] == 1]
        if len(with_benefit) > 0:
            senior_lead_ratio = ((with_benefit['is_senior'] == 1) | (with_benefit['is_lead'] == 1)).mean()
            print(f"{benefit_name}あり ({len(with_benefit)}件): Senior/Lead率 {senior_lead_ratio*100:.1f}%")

def create_visualizations(df):
    """データの可視化"""
    print("\n" + "=" * 80)
    print("グラフを生成中...")
    print("=" * 80)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('We Work Remotely 求人分析: 福利厚生と職位レベルの関係', fontsize=16)
    
    # 1. 福利厚生の分布
    ax1 = axes[0, 0]
    benefits_data = pd.DataFrame({
        '福利厚生': ['MacBook', 'Company\nRetreat', 'Unlimited\nPTO', 'いずれか\nあり'],
        '件数': [
            df['has_macbook'].sum(),
            df['has_company_retreat'].sum(),
            df['has_unlimited_pto'].sum(),
            df['has_premium_benefits'].sum()
        ]
    })
    ax1.bar(benefits_data['福利厚生'], benefits_data['件数'], color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    ax1.set_title('福利厚生の分布')
    ax1.set_ylabel('求人数')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. 職位レベルの分布
    ax2 = axes[0, 1]
    level_data = pd.DataFrame({
        '職位': ['Senior', 'Lead', 'Junior', 'Entry'],
        '件数': [
            df['is_senior'].sum(),
            df['is_lead'].sum(),
            df['is_junior'].sum(),
            df['is_entry'].sum()
        ]
    })
    ax2.bar(level_data['職位'], level_data['件数'], color=['#9b59b6', '#1abc9c', '#34495e', '#95a5a6'])
    ax2.set_title('職位レベルの分布')
    ax2.set_ylabel('求人数')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. 福利厚生の有無によるSenior/Lead割合
    ax3 = axes[1, 0]
    premium_jobs = df[df['has_premium_benefits'] == 1]
    standard_jobs = df[df['has_premium_benefits'] == 0]
    
    comparison_data = pd.DataFrame({
        '求人タイプ': ['福利厚生あり', '福利厚生なし'],
        'Senior/Lead率': [
            ((premium_jobs['is_senior'] == 1) | (premium_jobs['is_lead'] == 1)).mean() * 100 if len(premium_jobs) > 0 else 0,
            ((standard_jobs['is_senior'] == 1) | (standard_jobs['is_lead'] == 1)).mean() * 100 if len(standard_jobs) > 0 else 0
        ]
    })
    bars = ax3.bar(comparison_data['求人タイプ'], comparison_data['Senior/Lead率'], color=['#e74c3c', '#3498db'])
    ax3.set_title('福利厚生の有無別 Senior/Lead割合')
    ax3.set_ylabel('割合 (%)')
    ax3.set_ylim(0, 100)
    ax3.grid(axis='y', alpha=0.3)
    
    # バーの上に数値を表示
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    # 4. 職位レベル別の福利厚生保有率
    ax4 = axes[1, 1]
    level_benefit_data = []
    
    for level_col, level_name in [
        ('is_senior', 'Senior'),
        ('is_lead', 'Lead'),
        ('is_junior', 'Junior'),
        ('is_entry', 'Entry')
    ]:
        level_jobs = df[df[level_col] == 1]
        if len(level_jobs) > 0:
            benefit_rate = level_jobs['has_premium_benefits'].mean() * 100
            level_benefit_data.append({
                '職位': level_name,
                '福利厚生保有率': benefit_rate
            })
    
    if level_benefit_data:
        level_benefit_df = pd.DataFrame(level_benefit_data)
        bars = ax4.bar(level_benefit_df['職位'], level_benefit_df['福利厚生保有率'], 
                      color=['#9b59b6', '#1abc9c', '#34495e', '#95a5a6'])
        ax4.set_title('職位レベル別 魅力的福利厚生保有率')
        ax4.set_ylabel('割合 (%)')
        ax4.set_ylim(0, 100)
        ax4.grid(axis='y', alpha=0.3)
        
        # バーの上に数値を表示
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('/home/claude/job_analysis.png', dpi=300, bbox_inches='tight')
    print("グラフを保存しました: job_analysis.png")

def export_summary(df):
    """分析結果のサマリーをCSVでエクスポート"""
    summary_data = []
    
    # 福利厚生あり vs なし
    premium_jobs = df[df['has_premium_benefits'] == 1]
    standard_jobs = df[df['has_premium_benefits'] == 0]
    
    summary_data.append({
        'カテゴリ': '全体',
        'サブカテゴリ': '福利厚生あり',
        '求人数': len(premium_jobs),
        'Senior/Lead率': ((premium_jobs['is_senior'] == 1) | (premium_jobs['is_lead'] == 1)).mean() * 100 if len(premium_jobs) > 0 else 0
    })
    
    summary_data.append({
        'カテゴリ': '全体',
        'サブカテゴリ': '福利厚生なし',
        '求人数': len(standard_jobs),
        'Senior/Lead率': ((standard_jobs['is_senior'] == 1) | (standard_jobs['is_lead'] == 1)).mean() * 100 if len(standard_jobs) > 0 else 0
    })
    
    # 各福利厚生別
    for benefit_col, benefit_name in [
        ('has_macbook', 'MacBook支給'),
        ('has_company_retreat', 'Company Retreat'),
        ('has_unlimited_pto', 'Unlimited PTO')
    ]:
        with_benefit = df[df[benefit_col] == 1]
        if len(with_benefit) > 0:
            summary_data.append({
                'カテゴリ': '個別福利厚生',
                'サブカテゴリ': benefit_name,
                '求人数': len(with_benefit),
                'Senior/Lead率': ((with_benefit['is_senior'] == 1) | (with_benefit['is_lead'] == 1)).mean() * 100
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('/home/claude/analysis_summary.csv', index=False, encoding='utf-8-sig')
    print("サマリーを保存しました: analysis_summary.csv")

def main():
    """メイン実行関数"""
    print("\n" + "=" * 80)
    print("We Work Remotely 求人データ分析")
    print("=" * 80)
    
    # データ読み込み
    df = load_data()
    
    if len(df) == 0:
        print("\nエラー: データベースに求人データがありません。")
        print("まず scrape_jobs.py を実行してデータを収集してください。")
        return
    
    # 仮説検証
    analyze_hypothesis(df)
    
    # 可視化
    create_visualizations(df)
    
    # サマリーエクスポート
    export_summary(df)
    
    print("\n" + "=" * 80)
    print("分析完了！")
    print("=" * 80)

if __name__ == "__main__":
    main()
