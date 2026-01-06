import flet as ft
import json
import os

# ============================
# データ定義
# ============================
REGION_DATA = {
    "北海道・東北": ["北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島"],
    "関東": ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"],
    "関西": ["大阪", "京都", "兵庫", "奈良", "三重", "滋賀", "和歌山"],
    "九州・沖縄": ["福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]
}

WEATHER_MOCK = {
    "東京": "sunny",
    "大阪": "rainy",
    "北海道": "cloudy",
    "福岡": "rainy",
    "沖縄": "sunny"
}

SETTINGS_FILE = "my_region_data.json"

def main(page: ft.Page):
    # アプリ全体の設定
    page.title = "Flet 天気アプリ"
    page.padding = 0
    page.bgcolor = "white"

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

    def save_my_region_to_file(area_name):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"my_region": area_name}, f, ensure_ascii=False)

    def get_weather(area_name):
        return WEATHER_MOCK.get(area_name, "sunny")

    def get_bg_color(weather):
        if weather == "rainy":
            return "#E1F5FE"
        elif weather == "sunny":
            return "#FFF9C4"
        else:
            return "#F5F5F5"

    # ============================
    # UI構築
    # ============================
    
    background_container = ft.Container(
        expand=True,
        bgcolor="white",
    )

    status_text = ft.Text(
        value="読込中...", 
        size=24, 
        weight="bold", 
        color="black"
    )

    # シンプルなColumnでカードを縦に並べる
    areas_column = ft.Column(
        spacing=15,
        scroll="auto",
    )

    def update_ui():
        my_region = load_my_region()
        
        # 背景色とステータス更新
        if my_region:
            w = get_weather(my_region)
            background_container.bgcolor = get_bg_color(w)
            icon_char = "☀️" if w == "sunny" else "☔" if w == "rainy" else "☁️"
            status_text.value = f"My地域: {my_region}  {icon_char}"
        else:
            background_container.bgcolor = "#F5F5F5"
            status_text.value = "My地域は未設定です"

        # ナビゲーションのインデックス取得
        idx = rail.selected_index if rail.selected_index is not None else 0
        current_region_name = region_names[idx]
        areas = REGION_DATA[current_region_name]
        
        areas_column.controls.clear()
        
        for area in areas:
            w = get_weather(area)
            is_my = (area == my_region)
            
            btn_label = "設定済" if is_my else "My地域に設定"
            btn_icon = "check" if is_my else "add"
            btn_bg_color = "#9E9E9E" if is_my else "#1976D2"

            # カードの中身
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(area, size=20, weight="bold", color="black"),
                                ft.Text(f"天気: {w}", size=14, color="#757575"),
                            ],
                            spacing=5,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(btn_icon, color="white", size=18),
                                    ft.Text(btn_label, color="white", size=14)
                                ],
                                spacing=5,
                            ),
                            disabled=is_my,
                            on_click=lambda e, a=area: on_register_click(a),
                            bgcolor=btn_bg_color,
                        )
                    ],
                    alignment="spaceBetween",
                ),
                bgcolor="white",
                border_radius=10,
                padding=20,
                border=ft.border.all(1, "#E0E0E0"),
            )
            areas_column.controls.append(card)
        
        page.update()

    def on_register_click(area_name):
        save_my_region_to_file(area_name)
        page.snack_bar = ft.SnackBar(ft.Text(f"{area_name} を登録しました！"))
        page.snack_bar.open = True
        update_ui()

    def on_nav_change(e):
        update_ui()

    region_names = list(REGION_DATA.keys())
    rail = ft.NavigationRail(
        selected_index=0,
        label_type="all",
        min_width=120,
        destinations=[
            ft.NavigationRailDestination(
                icon="map_outlined", 
                selected_icon="map", 
                label=name
            ) for name in region_names
        ],
        on_change=on_nav_change,
        bgcolor="#F5F5F5",
    )

    layout_row = ft.Row(
        controls=[
            rail,
            ft.VerticalDivider(width=1, color="#E0E0E0"),
            ft.Column(
                controls=[
                    ft.Container(padding=20, content=status_text),
                    ft.Container(
                        content=areas_column,
                        padding=20,
                        expand=True,
                    )
                ],
                expand=True,
            )
        ],
        expand=True,
        spacing=0
    )

    background_container.content = layout_row
    page.add(background_container)
    update_ui()

ft.app(target=main)