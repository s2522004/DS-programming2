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
    page.theme_mode = ft.ThemeMode.LIGHT

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

    def get_bg_gradient(weather):
        if weather == "rainy":
            return ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#37474F", "#546E7A"],
            )
        elif weather == "sunny":
            return ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=["#29B6F6", "#B3E5FC"],
            )
        else:
            return ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#9E9E9E", "#EEEEEE"],
            )

    # ============================
    # UI構築
    # ============================
    
    background_container = ft.Container(
        expand=True,
        gradient=get_bg_gradient("sunny"),
    )

    status_text = ft.Text(
        value="読込中...", 
        size=20, 
        weight="bold", 
        color="white"
    )

    # 最新バージョンなので ft.Wrap が使えます（これが一番きれいに並びます）
    areas_wrap = ft.Wrap(
        spacing=10,
        run_spacing=10,
    )
    
    # スクロール用コンテナ
    scroll_container = ft.Column(
        controls=[areas_wrap],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def update_ui():
        my_region = load_my_region()
        
        # 背景とステータス更新
        if my_region:
            w = get_weather(my_region)
            background_container.gradient = get_bg_gradient(w)
            icon_char = "☀️" if w == "sunny" else "☔" if w == "rainy" else "☁️"
            status_text.value = f"My地域: {my_region}  {icon_char}"
        else:
            background_container.gradient = get_bg_gradient("default")
            status_text.value = "My地域は未設定です"

        # グリッドの再描画
        current_region_name = region_names[rail.selected_index]
        areas = REGION_DATA[current_region_name]
        
        areas_wrap.controls.clear()
        
        for area in areas:
            w = get_weather(area)
            is_my = (area == my_region)
            
            # アイコンとテキスト
            btn_icon_name = "check" if is_my else "add"
            btn_label = "設定済" if is_my else "My地域"
            btn_bg_color = "grey" if is_my else "blue"

            # ボタンの中身
            button_content = ft.Row(
                controls=[
                    ft.Icon(btn_icon_name, color="white"),
                    ft.Text(btn_label, color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )

            # カードの中身
            card_col = ft.Column(
                controls=[
                    ft.Text(area, size=18, weight="bold", color="black"),
                    ft.Text(f"天気: {w}", color="#555555"),
                    ft.Container(height=5),
                    
                    ft.ElevatedButton(
                        content=button_content,
                        disabled=is_my,
                        on_click=on_register_click,
                        data=area,
                        bgcolor=btn_bg_color,
                        color="white"
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

            card = ft.Container(
                width=160,  # カードの幅を固定
                height=130, # 高さも少し確保
                content=card_col,
                bgcolor="white",
                border_radius=10,
                padding=10,
            )
            areas_wrap.controls.append(card)
        
        page.update()

    def on_register_click(e):
        area_name = e.control.data
        save_my_region_to_file(area_name)
        page.open(ft.SnackBar(ft.Text(f"{area_name} を登録しました！")))
        update_ui()

    def on_nav_change(e):
        update_ui()

    region_names = list(REGION_DATA.keys())
    rail = ft.NavigationRail(
        selected_index=0,
        label_type="all",
        min_width=100,
        destinations=[
            ft.NavigationRailDestination(
                icon="map_outlined", 
                selected_icon="map", 
                label=name
            ) for name in region_names
        ],
        on_change=on_nav_change,
        bgcolor="#DDFFFFFF", 
    )

    layout_row = ft.Row(
        controls=[
            rail,
            ft.VerticalDivider(width=1, color="transparent"),
            ft.Column([
                ft.Container(padding=20, content=status_text),
                ft.Container(content=scroll_container, padding=20, expand=True)
            ], expand=True)
        ],
        expand=True,
        spacing=0
    )

    background_container.content = layout_row
    page.add(background_container)

    update_ui()

ft.app(target=main)