# We Work Remotely 求人分析プロジェクト

## プロジェクト概要

このプロジェクトは、We Work Remotelyという求人サイトから求人データをスクレイピングし、以下の仮説を検証します。

### 仮説
**「『MacBook支給』『Company Retreat（社員旅行）』『Unlimited PTO（無制限有給）』などの魅力的な福利厚生が明記されている求人は、タイトルに『Senior』や『Lead』が含まれる割合が、そうでない求人に比べて有意に高い。」**

### 予想される結論
未経験（Junior/Entry）可の求人では、このような待遇はほとんど見られない。

## ファイル構成

```
.
├── README.md                 # このファイル
├── requirements.txt          # 必要なPythonパッケージ
├── main.py                   # メインの実行スクリプト
├── create_db.py              # データベース作成
├── scrape_jobs.py            # 求人データスクレイピング
├── analyze_data.py           # データ分析と仮説検証
├── weworkremotely_jobs.db    # 求人データベース（実行後に生成）
├── job_analysis.png          # 分析結果グラフ（実行後に生成）
└── analysis_summary.csv      # 分析サマリー（実行後に生成）
```

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

または個別にインストール:

```bash
pip install requests beautifulsoup4 pandas matplotlib seaborn scipy
```

### 2. データベースの作成

```bash
python create_db.py
```

## 使用方法

### 方法1: すべて自動実行（推奨）

```bash
python main.py
```

このコマンドは以下を順番に実行します:
1. データベース作成
2. 求人データのスクレイピング（20-30分程度）
3. データ分析と仮説検証
4. グラフとサマリーの生成

### 方法2: 個別に実行

#### ステップ1: データベース作成
```bash
python create_db.py
```

#### ステップ2: 求人データのスクレイピング
```bash
python scrape_jobs.py
```

**注意**: スクレイピングには20-30分程度かかります。途中で中断しても、既に収集したデータはデータベースに保存されています。

#### ステップ3: データ分析
```bash
python analyze_data.py
```

### オプション

- `--skip-scraping`: スクレイピングをスキップして既存データで分析
  ```bash
  python main.py --skip-scraping
  ```

- `--db-only`: データベース作成のみ実行
  ```bash
  python main.py --db-only
  ```

## データベーススキーマ

### テーブル: jobs

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INTEGER | 主キー（自動採番） |
| title | TEXT | 求人タイトル |
| company | TEXT | 会社名 |
| category | TEXT | カテゴリ |
| job_type | TEXT | 雇用形態 |
| location | TEXT | 勤務地 |
| posted_date | TEXT | 投稿日 |
| url | TEXT | 求人URL（ユニーク） |
| description | TEXT | 求人詳細 |
| has_macbook | BOOLEAN | MacBook支給フラグ |
| has_company_retreat | BOOLEAN | Company Retreatフラグ |
| has_unlimited_pto | BOOLEAN | Unlimited PTOフラグ |
| has_premium_benefits | BOOLEAN | 魅力的福利厚生フラグ（上記いずれか） |
| is_senior | BOOLEAN | Seniorレベルフラグ |
| is_lead | BOOLEAN | Lead/Managerレベルフラグ |
| is_junior | BOOLEAN | Juniorレベルフラグ |
| is_entry | BOOLEAN | Entry/Internレベルフラグ |
| salary_info | TEXT | 給与情報 |
| scraped_at | TIMESTAMP | スクレイピング日時 |

## 分析内容

### 1. 記述統計
- 各福利厚生の出現頻度
- 各職位レベルの出現頻度
- 福利厚生あり/なし別のSenior/Lead割合

### 2. 統計的検定
- カイ二乗検定による有意差の検証
- p値による統計的有意性の判定

### 3. 可視化
生成される `job_analysis.png` には以下のグラフが含まれます:
- 福利厚生の分布
- 職位レベルの分布
- 福利厚生の有無別Senior/Lead割合
- 職位レベル別福利厚生保有率

## スクレイピングに関する注意事項

### 1. レート制限
- 各リクエスト間に2秒の待機時間を設定
- カテゴリ間に3秒の待機時間を設定
- サイトに負荷をかけないよう配慮

### 2. ロボット排除プロトコル
- We Work Remotelyの利用規約を遵守
- 教育目的の使用に限定
- 商用利用は禁止

### 3. エラーハンドリング
- ネットワークエラー時の自動リトライ
- 不完全なデータのスキップ
- 重複URLの自動除外

## データ分析の実行例

```python
import sqlite3
import pandas as pd

# データベースに接続
conn = sqlite3.connect('weworkremotely_jobs.db')

# カスタムクエリの例
query = """
SELECT 
    CASE WHEN has_premium_benefits = 1 THEN '福利厚生あり' ELSE '福利厚生なし' END as benefits,
    COUNT(*) as total,
    SUM(CASE WHEN is_senior = 1 OR is_lead = 1 THEN 1 ELSE 0 END) as senior_lead_count
FROM jobs
GROUP BY has_premium_benefits
"""

df = pd.read_sql_query(query, conn)
print(df)

conn.close()
```

## トラブルシューティング

### スクレイピングが失敗する場合

1. **ネットワーク接続を確認**
   ```bash
   ping weworkremotely.com
   ```

2. **User-Agentの更新**
   `scrape_jobs.py` の `headers` セクションを更新

3. **セレクタの更新**
   サイトの構造が変更された場合、CSSセレクタを更新

### データが少ない場合

- `scrape_jobs.py` の `max_pages` を増やす
- `CATEGORIES` リストにカテゴリを追加

### メモリ不足の場合

- バッチ処理を実装
- 一度に処理するページ数を減らす

## ライセンスと免責事項

このプロジェクトは教育目的で作成されています。

- We Work Remotelyの利用規約を遵守してください
- スクレイピングしたデータの商用利用は禁止
- データの正確性は保証されません
- サイトの構造変更により動作しなくなる可能性があります

## 参考資料

- We Work Remotely: https://weworkremotely.com/
- BeautifulSoup Documentation: https://www.crummy.com/software/BeautifulSoup/
- Pandas Documentation: https://pandas.pydata.org/
- SciPy Stats: https://docs.scipy.org/doc/scipy/reference/stats.html

## 貢献

改善提案やバグ報告は歓迎します。

## 作成者

授業プロジェクトとして作成
