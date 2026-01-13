import flet as ft

import json

import httpx

import os




# ============================

# データ定義

# ============================

AREA_JSON_URL = "https://www.jma.go.jp/bosai/common/const/area.json"

FORECAST_URL_BASE = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

SETTINGS_FILE = "my_region_data.json"



# ============================

# データ取得関数

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

        return response.json()

    except Exception as e:

        print(f"天気データ取得エラー: {e}")

        return None



def main(page: ft.Page):

    # アプリ全体の設定

    page.title = "気象庁 天気予報アプリ"

    page.padding = 0

    page.bgcolor = "white"



    # グローバル変数

    area_data = None

    selected_center = None

    

    # ============================

    # 関数群

    # ============================

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



    # ============================

    # UI構築

    # ============================

    

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



    def show_weather_forecast(area_code, area_name):

        """天気予報を表示"""

        weather_display.controls.clear()

        weather_display.visible = True

        

        # ローディング表示

        weather_display.controls.append(

            ft.Text(f"{area_name}の天気予報を取得中...", size=18, color="#666666")

        )

        page.update()

        

        # 天気データ取得

        weather_data = fetch_weather_data(area_code)

        

        if not weather_data:

            weather_display.controls.clear()

            weather_display.controls.append(

                ft.Text("天気予報の取得に失敗しました", size=18, color="red")

            )

            page.update()

            return

        

        weather_display.controls.clear()

        

        # タイトル

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

        

        try:

            # 天気予報データを解析

            for forecast in weather_data:

                publishing_office = forecast.get("publishingOffice", "")

                report_datetime = forecast.get("reportDatetime", "")

                

                weather_display.controls.append(

                    ft.Text(f"発表: {publishing_office} ({report_datetime})", size=14, color="#666666")

                )

                

                time_series = forecast.get("timeSeries", [])

                

                for series in time_series:

                    time_defines = series.get("timeDefines", [])

                    areas_data = series.get("areas", [])

                    

                    for area in areas_data:

                        area_name_in_data = area.get("area", {}).get("name", "")

                        

                        # 天気情報

                        weathers = area.get("weathers", [])

                        winds = area.get("winds", [])

                        waves = area.get("waves", [])

                        

                        for i, time_define in enumerate(time_defines):

                            if i < len(weathers):

                                card = ft.Container(

                                    content=ft.Column([

                                        ft.Text(f"日時: {time_define}", size=16, weight="bold", color="#333333"),

                                        ft.Text(f"地域: {area_name_in_data}", size=14, color="#666666"),

                                        ft.Text(f"天気: {weathers[i]}", size=14, color="#333333"),

                                        ft.Text(f"風: {winds[i] if i < len(winds) else '情報なし'}", size=14, color="#666666") if winds else ft.Container(),

                                        ft.Text(f"波: {waves[i] if i < len(waves) else '情報なし'}", size=14, color="#666666") if waves else ft.Container(),

                                    ], spacing=5),

                                    bgcolor="white",

                                    padding=15,

                                    border_radius=8,

                                    border=ft.Border.all(1, "#E0E0E0")

                                )

                                weather_display.controls.append(card)

                

                weather_display.controls.append(ft.Divider())

        

        except Exception as e:

            weather_display.controls.append(

                ft.Text(f"データ解析エラー: {str(e)}", size=14, color="red")

            )

        

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

        

        # 選択された地方の都道府県リストを取得

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

            

            # カード行を作成

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



    # 初期化処理

    def initialize():

        nonlocal area_data, selected_center

        

        status_text.value = "地域データを取得中..."

        page.update()

        

        area_data = fetch_area_data()

        

        if not area_data:

            status_text.value = "地域データの取得に失敗しました"

            page.update()

            return

        

        # NavigationRailの設定

        centers = area_data.get("centers", {})

        center_codes = list(centers.keys())

        center_names = [centers[code]["name"] for code in center_codes]

        

        rail.destinations = [

            ft.NavigationRailDestination(

                icon="map_outlined", 

                selected_icon="map", 

                label=name

            ) for name in center_names

        ]

        

        selected_center = center_codes[0]

        update_status()

        update_areas_list()



    center_codes = []

    rail = ft.NavigationRail(

        selected_index=0,

        label_type="all",

        min_width=120,

        destinations=[],

        on_change=on_nav_change,

        bgcolor="#EEEEEE",

    )



    # コンテンツエリア

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



    # 全体レイアウト

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

    

    # データ取得と初期化

    initialize()



# ブラウザ起動モード

ft.app(target=main, view=ft.AppView.WEB_BROWSER)