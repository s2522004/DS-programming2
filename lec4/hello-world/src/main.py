import flet as ft


def main(page: ft.Page):

    # カウンター表示用テキスト
    counter = ft.Text("0", size=50, data=0)
    hoge = ft.Text("Hallo,Flet!", size=50)

    # ボタンクリック時の処理
    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    # ボタンクリック時の処理
    def decrement_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        counter.update()

    # カウンターボタンの追加
    page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=increment_click)

    # カウンター表示の追加
    page.add(
        ft.SafeArea(
            ft.Container(
                content=ft.Column([counter,hoge]),
                alignment=ft.alignment.center,
            ),
            expand=True,
        ),
        ft.FloatingActionButton(icon=ft.Icons.REMOVE, on_click=decrement_click),
    )


ft.app(main)
