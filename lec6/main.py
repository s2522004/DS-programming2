import flet as ft
import json
import httpx
import os
import sqlite3

# ============================
# データベース設定・操作関数
# ============================
DB_NAME = "weather.db"

def init_db():
    """テーブルが存在しない場合に作成する初期化関数"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. 地域マスタ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL
        )
    """)
    
    # 2. 天気予報データ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            weather TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(area_code, forecast_date),
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        )
    """)
    conn.commit()
    conn.close()

def save_areas_to_db(area_data):
    """area.json の内容を DB に保存する"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. 地方 (centers) を保存
    centers = area_data.get("centers", {})
    for code, info in centers.items():
        cursor.execute("INSERT OR REPLACE INTO areas (area_code, area_name) VALUES (?, ?)", 
                       (code, info["name"]))

    # 2. 府県 (offices) を保存
    offices = area_data.get("offices", {})
    for code, info in offices.items():
        cursor.execute("INSERT OR REPLACE INTO areas (area_code, area_name) VALUES (?, ?)", 
                       (code, info["name"]))
    
    conn.commit()
    conn.close()
    print("エリア情報をDBに保存しました")

def save_forecasts_to_db(area_code, json_data):
    """取得した天気予報JSONを分解して DB に保存する"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    time_defines = json_data.get("timeDefines", [])
    
    areas = json_data.get("areas", [])
    if not areas:
        return

    weathers = areas[0].get("weathers", [])

    for date_str, weather_str in zip(time_defines, weathers):
        # 日付を "2023-01-01" の形式にする
        simple_date = date_str.split("T")[0]
        
        cursor.execute("""
            INSERT OR REPLACE INTO forecasts (area_code, forecast_date, weather)
            VALUES (?, ?, ?)
        """, (area_code, simple_date, weather_str))

    conn.commit()
    conn.close()
    print(f"{area_code} の予報をDBに保存しました")

def get_forecasts_from_db(area_code):
    """DBから指定したエリアの天気予報を取得する"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 日付順に取得
    cursor.execute("""
        SELECT forecast_date, weather 
        FROM forecasts 
        WHERE area_code = ? 
        ORDER BY forecast_date
    """, (area_code,))
    
    rows = cursor.fetchall() # List of (date, weather)
    conn.close()
    return rows

# ============================
# 定数定義
# ============================
AREA_JSON_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_BASE = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
SETTINGS_FILE = "my_region_data.json"

# ============================
# APIデータ取得関数
# ============================
def fetch_area_data():
    """気象庁から地域リストを取得"""
    try:
        response = httpx.get(AREA_JSON_URL, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"地域データ取得エラー: {e}")
        return None

def fetch_weather_data(area_code):
    """気象庁から天気予報データを取得"""
    try:
        url = f"{FORECAST_URL_BASE}{area_code}.json"
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        # jmaの予報jsonはリスト形式で返るため、最初の要素[0]["timeSeries"][0]を返すように調整
        data = response.json()
        return data[0]["timeSeries"][0]
    except Exception as e:
        print(f"天気データ取得エラー: {e}")
        return None

# ============================
# Main アプリケーション
# ============================
def main(page: ft.Page):
    # アプリ全体の設定
    page.title = "気象庁 天気予報アプリ (DB版)"
    page.padding = 0
    page.bgcolor = "white"

    # グローバル変数
    area_data = None
    selected_center = None
    
    # DB初期化（テーブル作成）
    init_db()

    # ---------------------------
    # 設定ファイル関連関数
    # ---------------------------
    def load_my_region():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("my_region")
            except:
                return None
        return None

    def save_my_region_to_file(area_code, area_name):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"my_region": {"code": area_code, "name": area_name}}, f, ensure_ascii=False)

    # ---------------------------
    # UIコンポーネント
    # ---------------------------
    status_text = ft.Text(
        value="読込中...", 
        size=24, 
        weight="bold", 
        color="#333333"
    )

    # 地域リスト表示用
    areas_column = ft.Column(
        spacing=10,
        scroll="auto",
        expand=True
    )

    # 天気予報表示用
    weather_display = ft.Column(
        spacing=10,
        scroll="auto",
        expand=True,
        visible=False
    )

    # ---------------------------
    # ロジック関数
    # ---------------------------
    def show_weather_forecast(area_code, area_name):
        """天気予報を表示 (API -> DB -> 画面 の流れ)"""
        weather_display.controls.clear()
        weather_display.visible = True
        
        # ローディング表示
        weather_display.controls.append(
            ft.Text(f"{area_name}のデータを更新・取得中...", size=18, color="#666666")
        )
        page.update()
        
        # 1. APIから最新データを取得してDBに保存 (通信エラー時はスキップしてDB内の過去データを表示)
        try:
            raw_data = fetch_weather_data(area_code)
            if raw_data:
                save_forecasts_to_db(area_code, raw_data)
        except Exception as e:
            print(f"通信エラー (DBのデータを表示します): {e}")

        # 2. 画面表示は「DBのデータ」を使って行う
        db_rows = get_forecasts_from_db(area_code)

        weather_display.controls.clear()
        
        # ヘッダー作成
        weather_display.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon="arrow_back",
                        on_click=lambda e: hide_weather_forecast(),
                        tooltip="戻る"
                    ),
                    ft.Text(f"{area_name}の天気予報", size=24, weight="bold", color="#333333"),
                ]),
                padding=10
            )
        )

        if not db_rows:
            weather_display.controls.append(
                ft.Text("表示できるデータがありません（通信を確認してください）", size=18, color="red")
            )
            page.update()
            return

        # DBデータをループしてカードを作成
        for date_display, weather_str in db_rows:
            # アイコン判定
            icon_name = "help_outline"
            if "晴" in weather_str: icon_name = "wb_sunny"
            elif "曇" in weather_str: icon_name = "cloud"
            elif "雨" in weather_str: icon_name = "umbrella"
            elif "雪" in weather_str: icon_name = "ac_unit"
            
            icon_color = "orange" if "晴" in weather_str else "grey"

            card = ft.Container(
                content=ft.Row([
                    ft.Icon(icon_name, size=30, color=icon_color),
                    ft.Column([
                        ft.Text(f"日付: {date_display}", size=16, weight="bold", color="#333333"),
                        ft.Text(f"天気: {weather_str}", size=14, color="#333333"),
                    ], spacing=2)
                ], alignment="start"),
                bgcolor="white",
                padding=15,
                border_radius=8,
                border=ft.Border.all(1, "#E0E0E0")
            )
            weather_display.controls.append(card)
        
        page.update()

    def hide_weather_forecast():
        """天気予報表示を非表示にして地域リストに戻る"""
        weather_display.visible = False
        areas_column.visible = True
        page.update()

    def update_areas_list():
        """地域リストを更新"""
        if not area_data or not selected_center:
            return
        
        areas_column.controls.clear()
        areas_column.visible = True
        weather_display.visible = False
        
        center_info = area_data["centers"].get(selected_center, {})
        office_codes = center_info.get("children", [])
        
        my_region = load_my_region()
        my_region_code = my_region.get("code") if my_region else None
        
        for office_code in office_codes:
            office_info = area_data["offices"].get(office_code, {})
            office_name = office_info.get("name", "")
            
            is_my = (office_code == my_region_code)
            btn_label = "設定済" if is_my else "設定"
            btn_bg_color = "#9E9E9E" if is_my else "#1976D2"
            
            row = ft.Row(
                controls=[
                    ft.Column([
                        ft.Text(office_name, size=18, weight="bold", color="#333333"),
                        ft.Text(f"コード: {office_code}", size=12, color="#999999"),
                    ], spacing=2),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon("check" if is_my else "add", size=16, color="white"), 
                                ft.Text(btn_label, color="white")
                            ], 
                            alignment="center", 
                            spacing=5
                        ),
                        bgcolor=btn_bg_color,
                        on_click=lambda e, code=office_code, name=office_name: on_register_click(code, name),
                        disabled=is_my
                    ),
                    ft.IconButton(
                        icon="visibility",
                        tooltip="天気予報を見る",
                        on_click=lambda e, code=office_code, name=office_name: show_weather_forecast(code, name)
                    )
                ],
                alignment="center",
            )

            card = ft.Container(
                content=row,
                bgcolor="white",
                padding=15,
                border_radius=8,
                border=ft.Border.all(1, "#E0E0E0")
            )
            areas_column.controls.append(card)
        
        page.update()

    def on_register_click(area_code, area_name):
        save_my_region_to_file(area_code, area_name)
        page.snack_bar = ft.SnackBar(ft.Text(f"{area_name} を登録しました！"))
        page.snack_bar.open = True
        update_status()
        update_areas_list()

    def on_nav_change(e):
        nonlocal selected_center
        selected_center = center_codes[rail.selected_index]
        update_areas_list()

    def update_status():
        my_region = load_my_region()
        if my_region:
            status_text.value = f"My地域: {my_region['name']}"
        else:
            status_text.value = "My地域は未設定です"
        page.update()

    def initialize():
        nonlocal area_data, selected_center
        
        status_text.value = "地域データを取得中..."
        page.update()
        
        area_data = fetch_area_data()
        
        if not area_data:
            status_text.value = "地域データの取得に失敗しました"
            page.update()
            return
        
        # ★ここでエリア情報をDBに保存
        save_areas_to_db(area_data)
        
        centers = area_data.get("centers", {})
        # center_codes をグローバルに近いスコープで使えるようリスト化
        nonlocal center_codes
        center_codes = list(centers.keys())
        center_names = [centers[code]["name"] for code in center_codes]
        
        rail.destinations = [
            ft.NavigationRailDestination(
                icon="map_outlined", 
                selected_icon="map", 
                label=name
            ) for name in center_names
        ]
        
        if center_codes:
            selected_center = center_codes[0]
            
        update_status()
        update_areas_list()

    # ---------------------------
    # レイアウト構築
    # ---------------------------
    center_codes = [] # initializeで中身を入れる
    
    rail = ft.NavigationRail(
        selected_index=0,
        label_type="all",
        min_width=120,
        destinations=[],
        on_change=on_nav_change,
        bgcolor="#EEEEEE",
    )

    content_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(content=status_text, padding=20),
                ft.Container(
                    content=ft.Stack([
                        areas_column,
                        weather_display
                    ]),
                    padding=20,
                    expand=True
                )
            ],
            expand=True
        ),
        expand=True,
    )

    layout = ft.Row(
        controls=[
            rail,
            ft.VerticalDivider(width=1, color="#CCCCCC"),
            content_container
        ],
        expand=True,
        spacing=0
    )

    page.add(layout)
    
    # アプリ起動
    initialize()

# ブラウザ起動モード
ft.app(target=main, view=ft.AppView.WEB_BROWSER)