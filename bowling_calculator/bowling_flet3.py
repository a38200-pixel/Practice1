import flet as ft


class BowlingGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rolls = []

    def add_roll(self, pins):
        self.rolls.append(pins)

    def delete(self):
        if self.rolls:
            self.rolls.pop()

    def score(self):
        score = 0
        roll_idx = 0
        frame_scores = []

        for frame in range(10):
            if roll_idx >= len(self.rolls):
                frame_scores.append("")
                continue

            if self.rolls[roll_idx] == 10:  # strike
                if roll_idx + 2 < len(self.rolls):
                    score += 10 + self.rolls[roll_idx+1] + self.rolls[roll_idx+2]
                    frame_scores.append(str(score))
                else:
                    frame_scores.append("")
                roll_idx += 1

            elif roll_idx + 1 < len(self.rolls):

                if self.rolls[roll_idx] + self.rolls[roll_idx+1] == 10:  # spare
                    if roll_idx + 2 < len(self.rolls):
                        score += 10 + self.rolls[roll_idx+2]
                        frame_scores.append(str(score))
                    else:
                        frame_scores.append("")
                else:
                    score += self.rolls[roll_idx] + self.rolls[roll_idx+1]
                    frame_scores.append(str(score))

                roll_idx += 2

            else:
                frame_scores.append("")
                roll_idx += 1

        return frame_scores


def main(page: ft.Page):

    page.title = "Bowling Scoreboard"
    page.bgcolor = "#222"
    page.window_width = 1000
    page.window_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    game = BowlingGame()

    roll_text = [[ft.Text("", color="white") for _ in range(3)] for _ in range(10)]
    frame_score = [ft.Text("", color="yellow", size=16) for _ in range(10)]

    # -------------------------
    # 프레임 UI
    # -------------------------

    def create_frame(i):

        rolls = [
            ft.Container(
                roll_text[i][0],
                width=30,
                height=30,
                alignment="center",
                border=ft.border.all(1, "white"),
            ),
            ft.Container(
                roll_text[i][1],
                width=30,
                height=30,
                alignment="center",
                border=ft.border.all(1, "white"),
            ),
        ]

        if i == 9:
            rolls.append(
                ft.Container(
                    roll_text[i][2],
                    width=30,
                    height=30,
                    alignment="center",
                    border=ft.border.all(1, "white"),
                )
            )

        roll_row = ft.Row(rolls, spacing=0)

        score_box = ft.Container(
            frame_score[i],
            width=95 if i == 9 else 65,
            height=40,
            alignment="center",
            border=ft.border.all(1, "white"),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(str(i+1), size=12, color="grey"),
                    roll_row,
                    score_box,
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=5,
        )

    scoreboard = ft.Row(
        [create_frame(i) for i in range(10)],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # -------------------------
    # 표시
    # -------------------------

    def display_symbol(pins, second=False, prev=0):

        if pins == 10 and not second:
            return "X"

        if second and prev + pins == 10:
            return "/"

        if pins == 0:
            return "-"

        return str(pins)

    # -------------------------
    # UI 업데이트
    # -------------------------

    def update_ui():

        rolls = game.rolls
        ptr = 0

        for i in range(10):
            for j in range(3):
                roll_text[i][j].value = ""

        for i in range(10):

            if ptr < len(rolls):

                p1 = rolls[ptr]
                roll_text[i][0].value = display_symbol(p1)
                ptr += 1

                if i < 9:

                    if p1 < 10 and ptr < len(rolls):

                        p2 = rolls[ptr]
                        roll_text[i][1].value = display_symbol(p2, True, p1)
                        ptr += 1

                else:

                    if ptr < len(rolls):

                        p2 = rolls[ptr]
                        roll_text[i][1].value = display_symbol(p2, True, p1)
                        ptr += 1

                    if ptr < len(rolls):

                        p3 = rolls[ptr]
                        roll_text[i][2].value = display_symbol(p3, True, p2)
                        ptr += 1

        scores = game.score()

        for i in range(10):
            frame_score[i].value = scores[i]

        page.update()

    # -------------------------
    # 버튼 클릭
    # -------------------------

    def click(label):

        if label == "X":
            game.add_roll(10)

        elif label == "/":
            if game.rolls:
                game.add_roll(10 - game.rolls[-1])

        elif label == "-":
            game.add_roll(0)

        else:
            game.add_roll(int(label))

        update_ui()

    # -------------------------
    # 버튼 생성
    # -------------------------

    def make_btn(text):

        return ft.Button(
            text,
            width=80,
            height=60,
            on_click=lambda e: click(text),
        )

    keypad = ft.Column(
        [
            ft.Row([make_btn("1"), make_btn("2"), make_btn("3")]),
            ft.Row([make_btn("4"), make_btn("5"), make_btn("6")]),
            ft.Row([make_btn("7"), make_btn("8"), make_btn("9")]),
            ft.Row([make_btn("-"), make_btn("0"), make_btn("/")]),
            ft.Row(
                [
                    make_btn("X"),
                    ft.Button("DEL", on_click=lambda e: (game.delete(), update_ui())),
                    ft.Button("RESET", on_click=lambda e: (game.reset(), update_ui())),
                ]
            ),
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # -------------------------
    # 페이지 추가 (핵심 수정)
    # -------------------------

    page.add(
        ft.Column(
            [
                ft.Text(
                    "BOWLING SCORE BOARD",
                    size=30,
                    weight="bold",
                    color="white",
                ),
                scoreboard,
                keypad,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=40,
        )
    )


ft.run(main)