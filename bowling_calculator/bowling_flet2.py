import flet as ft

class bowling_score_calculator:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.frames = []
        for i in range(10):
            if i < 9:
                self.frames.append({"roll_1": None, "roll_2": None})
            else:
                self.frames.append({"roll_1": None, "roll_2": None, "roll_3": None})
        self.current_frame_idx = 0

    def add_score(self, pins):
        if self.current_frame_idx > 9: return # 게임 종료 후 클릭 방지
        
        current_frame = self.frames[self.current_frame_idx]

        if current_frame["roll_1"] is None:
            current_frame["roll_1"] = pins
        elif current_frame["roll_2"] is None:
            current_frame["roll_2"] = pins
        elif "roll_3" in current_frame and current_frame["roll_3"] is None:
            current_frame["roll_3"] = pins

        self.move_frame()

    def move_frame(self):
        f = self.frames[self.current_frame_idx]
        if self.current_frame_idx < 9:
            # 스트라이크거나 2구까지 던졌을 때 이동
            if f["roll_1"] == 10 or f["roll_2"] is not None:
                self.current_frame_idx += 1
        else:
            # 10프레임 종료 조건
            if f["roll_3"] is not None:
                pass # 종료 (리셋은 버튼으로 제어하는 것이 좋음)
            elif f["roll_2"] is not None:
                if (f["roll_1"] + f["roll_2"]) < 10:
                    pass # 종료

    def total_score(self, to_idx=9):
        total = 0
        for i in range(to_idx + 1):
            f = self.frames[i]
            total += (f.get("roll_1") or 0) + (f.get("roll_2") or 0) + (f.get("roll_3") or 0)
        return total

def main(page: ft.Page):
    page.title = "Bowling Score Board"
    page.window_width = 1100 # 너비를 충분히 확보
    page.window_height = 700
    page.bgcolor = "#2b2b2b"
    page.padding = 30
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    calc = bowling_score_calculator()

    # 텍스트 객체 생성 (글자색 흰색으로 고정)
    roll1 = [ft.Text("", color="white", size=12, weight="bold") for _ in range(10)]
    roll2 = [ft.Text("", color="white", size=12, weight="bold") for _ in range(10)]
    roll3 = [ft.Text("", color="white", size=12, weight="bold") for _ in range(10)]
    scores = [ft.Text("", color="white", size=14) for _ in range(11)]

    def create_frame(idx):
        roll_boxes = ft.Row(
            [
                ft.Container(roll1[idx], width=25, height=25, alignment="center", border=ft.border.only(right=ft.border.BorderSide(1, "white"), bottom=ft.border.BorderSide(1, "white"))),
                ft.Container(roll2[idx], width=25, height=25, alignment="center", border=ft.border.only(right=ft.border.BorderSide(1, "white"), bottom=ft.border.BorderSide(1, "white"))),
                ft.Container(roll3[idx] if idx == 9 else ft.Text(""), width=25, height=25, alignment="center", border=ft.border.only(bottom=ft.border.BorderSide(1, "white"))),
            ],
            spacing=0,
        )

        score_box = ft.Container(
            scores[idx], width=75, height=35, alignment="center"
        )

        return ft.Container(
            content=ft.Column([roll_boxes, score_box], spacing=0),
            width=77, height=65, border=ft.border.all(1, "white"),
        )

    scoreboard = ft.Row(
        [create_frame(i) for i in range(10)] + [
            ft.Container(
                content=ft.Column([
                    ft.Container(ft.Text("TOTAL", color="black", weight="bold", size=10), alignment="center", bgcolor="#FFD700", height=25),
                    ft.Container(scores[10], alignment="center", height=40)
                ], spacing=0),
                width=80, height=65, border=ft.border.all(1, "white"), bgcolor="#444444",
            )
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER
    )

    def update_ui():
        for i in range(10):
            f = calc.frames[i]
            roll1[i].value = "X" if f["roll_1"] == 10 else (str(f["roll_1"]) if f["roll_1"] is not None else "")
            roll2[i].value = str(f["roll_2"]) if f["roll_2"] is not None else ""
            roll3[i].value = str(f.get("roll_3", "")) if f.get("roll_3") is not None else ""
            
            # 누적 점수 표시
            if f["roll_1"] is not None:
                scores[i].value = str(calc.total_score(i))
            else:
                scores[i].value = ""

        scores[10].value = str(calc.total_score(9))
        page.update()

    def click(e):
        val = int(e.control.data)
        calc.add_score(val)
        update_ui()

    def btn(n):
        return ft.ElevatedButton(
            str(n), width=70, height=70, data=str(n), on_click=click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), bgcolor="#444444", color="white")
        )

    page.add(
        ft.Text("BOWLING SCORE BOARD", size=32, weight="bold", color="white"),
        ft.Container(height=20),
        scoreboard,
        ft.Container(height=40),
        ft.Column([
            ft.Row([btn(1), btn(2), btn(3), btn(0)], alignment="center"),
            ft.Row([btn(4), btn(5), btn(6), btn(10)], alignment="center"),
            ft.Row([btn(7), btn(8), btn(9)], alignment="center"),
            ft.Container(height=20),
            ft.ElevatedButton("RESET GAME", on_click=lambda _: (calc.reset_game(), update_ui()), width=230, height=50)
        ], horizontal_alignment="center")
    )

ft.app(target=main)