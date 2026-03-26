import flet as ft
import random

def main(page: ft.Page):
    # 페이지 설정
    page.title = "5전 3승 가위바위보"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    choices = ["가위", "바위", "보"]
    user_win = [0] 
    com_win = [0]
    
    # UI 요소 생성
    title_text = ft.Text("5전 3승 가위바위보", size=40, weight="bold")
    score_text = ft.Text("사용자 0 : 0 컴퓨터", size=30)
    result_text = ft.Text("버튼을 누르면 시작합니다.", size=16, color=ft.Colors.BLUE_800)
    final_result = ft.Text("", size=24, weight="bold", color=ft.Colors.GREEN_800)

    #승패 판정
    def check_winner(user, com):
        result = (user - com + 3) % 3
        if result == 0:
            return "무승부"
        elif result == 1:
            return "승리"
        else:
            return "패배"
    def disable_buttons():
        for btn in btn_row.controls:
            btn.disabled = True

    def play(e):
            if user_win[0] >= 3 or com_win[0] >= 3:
                return
            user_input = e.control.data
            user = choices.index(user_input)
            com = random.randint(0, 2)
            com_input = choices[com]

            판정 = check_winner(user, com)


             #승리 횟수 누적
            if 판정 == '승리':
                user_win[0] = user_win[0] + 1
                result_text.value = f"사용자가 승리했습니다(사용자 승리횟수: {user_win[0]})"
            elif 판정 == '패배':
                com_win[0] = com_win[0] + 1
                result_text.value = f"컴퓨터가 승리했습니다(컴퓨터 승리횟수: {com_win[0]})"
            else:
                result_text.value = "무승부 입니다"

            score_text.value = f"사용자 {user_win[0]} : {com_win[0]} 컴퓨터"

            #최종 판정
            if user_win[0] == 3:
                final_result.value = "축하합니다. 승리했습니다."
                disable_buttons()
            elif com_win[0] == 3:
                final_result.value = "패배했습니다. 다시 도전하세요."
                disable_buttons()

            page.update()
        
    btn_row = ft.Row(
        [
            ft.ElevatedButton("가위", on_click=play, icon=ft.Icons.CONTENT_CUT, data="가위"),
            ft.ElevatedButton("바위", on_click=play, icon=ft.Icons.CIRCLE, data="바위"),
            ft.ElevatedButton("보", on_click=play, icon=ft.Icons.PAN_TOOL, data="보"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        title_text,
        ft.Divider(height=20, color="transparent"),
        score_text,
        result_text,
        ft.Divider(height=40),
        btn_row,
        ft.Divider(height=20, color="transparent"),
        final_result
    )
ft.run(main)