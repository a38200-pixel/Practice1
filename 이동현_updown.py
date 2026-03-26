import flet as ft
import random

def main(page: ft.Page):
    page.title = "up&down_game"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    updown_game = {
        "num": random.randint(1, 100),
        "game_over": False
    }
    # UI 요소 생성
    result_text = ft.Text(value="1부터 100 사이의 숫자를 맞춰보세요!", size=20)
    user_input = ft.TextField(label="숫자 입력 (1~100)", width=250)
    # 버튼 변수 이름을 미리 선언만 해둠
    check_button = ft.Button(content=ft.Text("확인"))
    restart_button = ft.Button(content=ft.Text("다시 시작"), visible=False)

    # 게임 재시작 함수
    def restart_game(e):
        updown_game["num"] = random.randint(1, 100)
        updown_game["game_over"] = False
        result_text.value = "새 게임 시작! 1부터 100 사이의 숫자를 맞춰보세요."
        user_input.disabled = False
        user_input.value = ""
        check_button.disabled = False
        restart_button.visible = False
        page.update()
    
    # 정답 확인 함수
    def check_guess(e):
        if updown_game["game_over"]:
            return

        if user_input.value.isdigit(): # 숫자로만 되어있는지 확인
            guess = int(user_input.value)
        else:
            result_text.value = "숫자를 입력해주세요!"
            page.update()
            return

        # 범위 확인
        if not (1 <= guess <= 100):
            result_text.value = "1에서 100 사이의 숫자만 입력하세요."
            page.update()
            return

        # 숫자 비교
        target = updown_game["num"]
        if guess == target:
            result_text.value = "정답입니다"
            updown_game["game_over"] = True
            check_button.disabled = True
            user_input.disabled = True
            restart_button.visible = True
        elif guess > target:
            result_text.value = "다운"
        else:
            result_text.value = "업"
            
        user_input.value = ""
        page.update()
   
    # UI연결
    user_input.on_submit = check_guess
    check_button.on_click = check_guess
    restart_button.on_click = restart_game

    #화면 배치
    page.add(
        ft.Column(
            [
                result_text,
                user_input,
                check_button,
                restart_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        )
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)