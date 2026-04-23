import flet as ft
import re

# --- 연산 로직 ---
class MYCalculator:
    def __init__(self):
        self.number_list = []

    def calculate_expression(self, expression):
        try:
            # 표시용 기호를 연산용 기호로 치환 후 계산
            calc_expr = expression.replace('×', '*').replace('÷', '/')
            #eval 사용해서 +, -, *, / 연산처리
            result = eval(calc_expr)
            return result
        except Exception:
            return "Error"

    def get_list_stats(self, raw_input, stat_type):
        try:
            numbers = [float(x) for x in raw_input.split()]
            if not numbers: return "데이터 없음"
            if stat_type == "평균": return sum(numbers) / len(numbers)
            if stat_type == "최대": return max(numbers)
            if stat_type == "최소": return min(numbers)
        except (ValueError, ZeroDivisionError):
            return "형식 오류"

# --- 메인 UI 및 핸들러 ---
def main(page: ft.Page):
    page.title = "통합 계산기 시스템"
    page.window.width = 400
    page.window.height = 700
    page.bgcolor = "#F3F3F3"
    
    calculator_logic = MYCalculator()

    # --- 메인 화면 변수 ---
    display_text = ft.Text("0", size=40, weight="bold")
    current_expression = "0"

    # --- 리스트 연산용 모달 변수 ---
    modal_input = ft.TextField(label="숫자들을 입력하세요 (공백 구분)", hint_text="예: 10.5 20.3 30")
    modal_result = ft.Text("결과: -", size=20, weight="bold", color="blue")
    modal_title = ft.Text("통계 연산")

    # --- 숫자 패드 입력 처리 ---
    def on_click_digit(e):
        nonlocal current_expression
        clicked_value = str(e.control.data)
        
        # 초기 상태가 "0"인 경우 처리
        if current_expression == "0":
            if clicked_value == ".":
                current_expression = "0."
            elif clicked_value in ["+", "-", "*", "/"]:
                current_expression = "0" + clicked_value
            else:
                current_expression = clicked_value
        # 소수점 중복 방지
        elif clicked_value == ".":
            last_part = re.split(r'[\+\-\*\/]', current_expression)[-1]
            if "." in last_part: return # 이미 소수점이 있으면 무시
            current_expression += clicked_value
        #  일반적인 숫자/연산자 추가
        else:
            current_expression += clicked_value
            
        display_text.value = current_expression
        page.update()

    def on_click_equal(e):
        nonlocal current_expression
        result = calculator_logic.calculate_expression(current_expression)
        
        if result == "Error":
            display_text.value = "Error"
            current_expression = "0"
        else:
            # 결과가 정수면 소수점 제거, 실수면 유지 (:g 포맷)
            display_text.value = f"{result:g}"
            current_expression = display_text.value
        page.update()

    def on_click_clear(e):
        nonlocal current_expression
        current_expression = "0"
        display_text.value = "0"
        page.update()

    # --- 리스트 연산 모달 제어 ---
    def close_modal(e):
        stats_modal.open = False
        page.update()

    def run_list_calc(stat_type):
        res = calculator_logic.get_list_stats(modal_input.value, stat_type)
        modal_result.value = f"{stat_type} 결과: {res if isinstance(res, str) else f'{res:g}'}"
        page.update()

    stats_modal = ft.AlertDialog(
        title=modal_title,
        content=ft.Column([modal_input, modal_result], tight=True),
        actions=[ft.TextButton("닫기", on_click=close_modal)]
    )
    page.overlay.append(stats_modal)

    def open_stats_window(stat_type):
        modal_title.value = f"리스트 {stat_type} 구하기"
        modal_input.value = ""
        modal_result.value = "결과: -"
        stats_modal.actions = [
            ft.FilledButton(f"{stat_type} 계산", on_click=lambda e: run_list_calc(stat_type)),
            ft.TextButton("닫기", on_click=close_modal)
        ]
        stats_modal.open = True
        page.update()

    # --- UI 조립용 버튼 함수 ---
    def make_btn(text, on_click_fn, data=None, color="black", bgcolor="white", expand=1):
        return ft.Container(
            content=ft.TextButton(
                content=ft.Container(ft.Text(text, size=20, color=color), alignment=ft.Alignment(0, 0)),
                on_click=on_click_fn,
                data=data
            ),
            bgcolor=bgcolor, border_radius=8, expand=expand, height=70
        )

    # --- 레이아웃 조립 ---
    display_container = ft.Container(
        content=ft.Column([display_text], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END),
        padding=20, height=150
    )

    pad_rows = [
        ft.Row([make_btn("C", on_click_clear, bgcolor="#FFCDD2"), make_btn("÷", on_click_digit, data="/", bgcolor="#EBEBEB")]),
        ft.Row([make_btn("7", on_click_digit, data="7"), make_btn("8", on_click_digit, data="8"), make_btn("9", on_click_digit, data="9"), make_btn("×", on_click_digit, data="*", bgcolor="#EBEBEB")]),
        ft.Row([make_btn("4", on_click_digit, data="4"), make_btn("5", on_click_digit, data="5"), make_btn("6", on_click_digit, data="6"), make_btn("-", on_click_digit, data="-", bgcolor="#EBEBEB")]),
        ft.Row([make_btn("1", on_click_digit, data="1"), make_btn("2", on_click_digit, data="2"), make_btn("3", on_click_digit, data="3"), make_btn("+", on_click_digit, data="+", bgcolor="#EBEBEB")]),
        ft.Row([make_btn("0", on_click_digit, data="0", expand=2), make_btn(".", on_click_digit, data="."), make_btn("=", on_click_equal, bgcolor="#2196F3", color="white")]),
    ]

    special_row = ft.Row([
        make_btn("평균값", lambda e: open_stats_window("평균"), bgcolor="#E3F2FD"),
        make_btn("최댓값", lambda e: open_stats_window("최대"), bgcolor="#E3F2FD"),
        make_btn("최솟값", lambda e: open_stats_window("최소"), bgcolor="#E3F2FD"),
    ], spacing=5)

    page.add(
        display_container,
        ft.Column(pad_rows, spacing=5),
        ft.Divider(height=20),
        special_row
    )

if __name__ == "__main__":
    ft.app(target=main)