import flet as ft
import math  # 【追加】科学計算用の数学関数ライブラリ


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


# 【追加】科学計算ボタン用のクラス（緑色で表示）
class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.GREEN_700
        self.color = ft.Colors.WHITE


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        # 【追加】科学計算モードのフラグ
        self.scientific_mode = False

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        
        # 【編集】基本計算ボタンのレイアウト
        self.basic_content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
                # 【追加】科学計算モード切り替えボタン
                ft.Row(
                    controls=[
                        ExtraActionButton(text="科学計算モード", button_clicked=self.toggle_mode),
                    ]
                ),
            ]
        )
        
        # 【追加】科学計算モードのレイアウト
        self.scientific_content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                # 科学計算ボタン行1: sin, cos, tan, π, e
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                        ScientificButton(text="e", button_clicked=self.button_clicked),
                    ]
                ),
                # 科学計算ボタン行2: log, ln, sqrt, x², x³
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                        ScientificButton(text="x²", button_clicked=self.button_clicked),
                        ScientificButton(text="x³", button_clicked=self.button_clicked),
                    ]
                ),
                # 基本ボタン行
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
                # モード切り替えボタン
                ft.Row(
                    controls=[
                        ExtraActionButton(text="基本モード", button_clicked=self.toggle_mode),
                    ]
                ),
            ]
        )
        
        # 初期表示は基本モード
        self.content = self.basic_content

    # 【追加】モード切り替え関数
    def toggle_mode(self, e):
        """基本モードと科学計算モードを切り替える"""
        self.scientific_mode = not self.scientific_mode
        if self.scientific_mode:
            self.content = self.scientific_content
        else:
            self.content = self.basic_content
        self.update()

    # 【編集】ボタンクリック時の処理に科学計算機能を追加
    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.reset()

        elif data in ("%"):
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(self.format_number(abs(float(self.result.value))))

        # 【追加】科学計算機能の処理
        elif data == "sin":
            # 三角関数sin（ラジアン）
            try:
                self.result.value = self.format_number(math.sin(float(self.result.value)))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "cos":
            # 三角関数cos（ラジアン）
            try:
                self.result.value = self.format_number(math.cos(float(self.result.value)))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "tan":
            # 三角関数tan（ラジアン）
            try:
                self.result.value = self.format_number(math.tan(float(self.result.value)))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "log":
            # 常用対数（底10）
            try:
                val = float(self.result.value)
                if val <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.log10(val))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "ln":
            # 自然対数（底e）
            try:
                val = float(self.result.value)
                if val <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.log(val))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "√":
            # 平方根
            try:
                val = float(self.result.value)
                if val < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.sqrt(val))
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "x²":
            # 2乗
            try:
                self.result.value = self.format_number(float(self.result.value) ** 2)
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "x³":
            # 3乗
            try:
                self.result.value = self.format_number(float(self.result.value) ** 3)
            except:
                self.result.value = "Error"
            self.reset()
        
        elif data == "π":
            # 円周率π
            self.result.value = self.format_number(math.pi)
            self.reset()
        
        elif data == "e":
            # 自然対数の底e
            self.result.value = self.format_number(math.e)
            self.reset()

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"  # 【編集】タイトル変更
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)