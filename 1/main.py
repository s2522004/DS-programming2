#!/usr/bin/env python3
"""
We Work Remotely 求人スクレイピング・分析パイプライン

このスクリプトは以下の手順を実行します:
1. データベースの作成
2. 求人データのスクレイピング
3. データの分析と仮説検証
4. 結果の可視化とエクスポート

使用方法:
    python main.py [オプション]

オプション:
    --skip-scraping  スクレイピングをスキップして分析のみ実行
    --db-only        データベース作成のみ実行
"""

import sys
import subprocess
import os

def run_script(script_name, description):
    """Pythonスクリプトを実行"""
    print("\n" + "=" * 80)
    print(f"{description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ エラー: {description} 失敗")
        print(f"エラー詳細: {e}")
        return False
    except FileNotFoundError:
        print(f"\n✗ エラー: {script_name} が見つかりません")
        return False

def main():
    """メイン実行関数"""
    print("=" * 80)
    print("We Work Remotely 求人分析パイプライン")
    print("=" * 80)
    print("\n仮説:")
    print("『MacBook支給』『Company Retreat』『Unlimited PTO』などの")
    print("魅力的な福利厚生が明記されている求人は、Senior/Leadの")
    print("割合が高い（Junior/Entryでは少ない）")
    print("=" * 80)
    
    # コマンドライン引数の処理
    skip_scraping = "--skip-scraping" in sys.argv
    db_only = "--db-only" in sys.argv
    
    # ステップ1: データベース作成
    if not run_script("create_db.py", "ステップ1: データベース作成"):
        return
    
    if db_only:
        print("\n--db-only オプションが指定されているため、ここで終了します。")
        return
    
    # ステップ2: スクレイピング
    if not skip_scraping:
        print("\n注意: We Work Remotely のスクレイピングには時間がかかります（20-30分程度）")
        response = input("スクレイピングを開始しますか？ (y/n): ")
        
        if response.lower() != 'y':
            print("スクレイピングをスキップします。")
            skip_scraping = True
        else:
            if not run_script("scrape_jobs.py", "ステップ2: 求人データのスクレイピング"):
                print("\nスクレイピングに失敗しましたが、既存のデータで分析を続行します。")
    else:
        print("\n--skip-scraping オプションが指定されているため、スクレイピングをスキップします。")
    
    # ステップ3: データ分析
    if not run_script("analyze_data.py", "ステップ3: データ分析と仮説検証"):
        return
    
    # 完了メッセージ
    print("\n" + "=" * 80)
    print("すべての処理が完了しました！")
    print("=" * 80)
    print("\n生成されたファイル:")
    
    files = [
        ("weworkremotely_jobs.db", "求人データベース"),
        ("job_analysis.png", "分析グラフ"),
        ("analysis_summary.csv", "分析サマリー（CSV）")
    ]
    
    for filename, description in files:
        if os.path.exists(filename):
            print(f"  ✓ {filename} - {description}")
        else:
            print(f"  ✗ {filename} - {description} (未作成)")
    
    print("\n次のステップ:")
    print("  1. job_analysis.png を確認して視覚的な分析結果を確認")
    print("  2. analysis_summary.csv で詳細な数値を確認")
    print("  3. SQLiteで weworkremotely_jobs.db を直接クエリして詳細分析")

if __name__ == "__main__":
    main()
