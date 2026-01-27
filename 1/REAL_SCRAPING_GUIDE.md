# 実際のWe Work Remotelyサイトからデータ取得

## 📋 事前準備

### 1. データベースを作成（初回のみ）
```bash
python create_db.py
```

### 2. 既存のテストデータを削除（オプション）
```bash
# 既存のデータベースを削除して新規作成
rm weworkremotely_jobs.db
python create_db.py
```

---

## 🌐 実際のスクレイピング実行

### 実行コマンド
```bash
python scrape_jobs_real.py
```

### 予想実行時間
- **20-30分程度**（ネットワーク速度による）
- 8カテゴリ × 約20件 = 約160件の求人を取得
- 各求人の詳細ページも取得するため時間がかかります

### 実行中の画面表示例
```
============================================================
We Work Remotely 求人スクレイピング開始
============================================================
開始時刻: 2026-01-27 20:45:00

============================================================
カテゴリ: /categories/remote-programming-jobs
============================================================

スクレイピング中: https://weworkremotely.com/categories/remote-programming-jobs
  15 件の求人要素を発見
  15 件の求人を発見

このカテゴリで 15 件取得
累計: 15 件

[1/15] 処理中: Senior Software Engineer...
    詳細取得: https://weworkremotely.com/remote-jobs/...
  ✓ 保存完了

[2/15] 処理中: Full Stack Developer...
    詳細取得: https://weworkremotely.com/remote-jobs/...
  ✓ 保存完了

...
```

---

## 📊 取得されるデータ

### カテゴリ（8つ）
1. Programming（プログラミング）
2. DevOps/SysAdmin（システム管理）
3. Design（デザイン）
4. Product（プロダクト）
5. Marketing（マーケティング）
6. Customer Support（カスタマーサポート）
7. Sales（営業）
8. Writing（ライティング）

### 各求人の情報
- **基本情報**: タイトル、会社名、カテゴリ、地域、URL
- **詳細情報**: 求人詳細、雇用形態、投稿日、給与情報
- **分析フラグ**: 
  - 福利厚生（MacBook、Company Retreat、Unlimited PTO）
  - 職位レベル（Senior、Lead、Junior、Entry）

---

## ⚠️ 注意事項

### 1. レート制限の遵守
- 各リクエスト間に2秒の待機
- カテゴリ間に5秒の待機
- サイトに負荷をかけないよう配慮

### 2. エラー対処
スクレイピング中にエラーが出ても、既に取得したデータは保存されています。

**途中で中断した場合:**
```bash
# 再度実行すると、重複は自動的にスキップされます
python scrape_jobs_real.py
```

### 3. サイト構造の変更
We Work Remotelyのサイト構造が変更された場合、スクリプトが動作しない可能性があります。

**確認方法:**
```
スクレイピング中: https://weworkremotely.com/categories/...
  0 件の求人要素を発見  ← これが表示されたら構造が変わった可能性
```

---

## 🔍 実行後の確認

### 1. データベースの確認
```bash
# Pythonで確認
python -c "import sqlite3; conn = sqlite3.connect('weworkremotely_jobs.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM jobs'); print(f'総求人数: {cur.fetchone()[0]}'); conn.close()"
```

### 2. データ分析の実行
```bash
python analyze_data_fixed.py
```

### 3. 結果の確認
- **job_analysis.png** - 分析グラフ
- **analysis_summary.csv** - サマリーデータ

---

## 💡 よくある質問

### Q: どのくらいのデータが必要ですか？
A: 統計的に有意な結果を得るには、最低50-100件程度が望ましいです。

### Q: もっと多くのデータを取得したい
A: `scrape_jobs_real.py` の `max_jobs=20` を増やしてください（例: `max_jobs=50`）

```python
# scrape_jobs_real.pyの76行目付近
jobs = scrape_category(category_url, max_jobs=50)  # 20から50に変更
```

### Q: 特定のカテゴリだけ取得したい
A: `CATEGORY_URLS` リストを編集してください

```python
# scrape_jobs_real.pyの13-22行目
CATEGORY_URLS = [
    "/categories/remote-programming-jobs",  # これだけ残す
    # 他はコメントアウト
]
```

### Q: エラーが多発する
A: 待機時間を長くしてください

```python
# scrape_jobs_real.py内
time.sleep(5)  # 2から5に変更
```

---

## 🛠️ トラブルシューティング

### エラー1: `requests.exceptions.ConnectionError`
**原因**: ネットワーク接続の問題

**解決策:**
1. インターネット接続を確認
2. VPNを使用している場合はオフにする
3. 少し時間を置いて再実行

### エラー2: `HTTPError: 429 Too Many Requests`
**原因**: リクエストが多すぎる

**解決策:**
1. 待機時間を長くする
2. `max_jobs` を減らす
3. 時間を置いて再実行

### エラー3: 求人が0件
**原因**: サイト構造が変更された可能性

**解決策:**
1. ブラウザでサイトを確認
2. セレクタが変更されていないか確認
3. エラーメッセージを確認

---

## 📈 期待される結果

### 取得データ例
```
============================================================
保存完了: 145 件の新規求人
スキップ: 12 件の重複求人
エラー: 3 件
============================================================
```

### 分析結果例（実データ）
実際のデータでは以下のような結果が期待されます：

- **福利厚生あり**: 20-30%程度の求人
- **Senior/Lead職**: 40-50%程度
- **福利厚生ありのSenior/Lead率**: 60-80%程度
- **Junior/Entryでの福利厚生**: 5-10%程度

---

## 🚀 実行の流れ（まとめ）

```bash
# ステップ1: データベース作成（初回のみ）
python create_db.py

# ステップ2: 実際のサイトからスクレイピング（20-30分）
python scrape_jobs_real.py

# ステップ3: データ分析
python analyze_data_fixed.py

# ステップ4: 結果確認
# - job_analysis.png をプレビュー
# - analysis_summary.csv を開く
```

---

## 📝 実行ログの保存（オプション）

実行ログを保存したい場合：

```bash
# 標準出力とエラー出力の両方をファイルに保存
python scrape_jobs_real.py 2>&1 | tee scraping_log.txt
```

---

**準備完了！** 🎉

`python scrape_jobs_real.py` を実行して、実際のデータを取得しましょう！
