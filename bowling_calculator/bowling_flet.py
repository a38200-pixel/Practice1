import flet as ft

class bowling_score_calculator:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.frames = []
        for i in range (10):
            if i < 9:
                self.frames.append({"roll_1": None, "roll_2" : None})
            else:
                self.frames.append({"roll_1": None, "roll_2" : None, "roll_3" : None})

        self.current_frame_idx = 0
        print("새 게임 시작")
    
    def add_score(self, pins, foul=False):
        if foul:
            actual_score = 0
        else:
            actual_score = pins
        current_frame = self.frames[self.current_frame_idx]

        if current_frame["roll_1"] is None:
            current_frame["roll_1"] = actual_score
        elif current_frame["roll_2"] is None:
            current_frame["roll_2"] = actual_score 
        elif "roll_3" in current_frame and current_frame["roll_3"] is None:
            current_frame["roll_3"] = actual_score

        #프레임 이동 및 해당 프레임 점수리셋
        return self.move_frame(actual_score)


    def move_frame(self, pins):
        current_frame = self.frames[self.current_frame_idx]

        # 1~9프레임 처리 (인덱스 0~8)
        if self.current_frame_idx < 9:
            #스트라이크(10점)면 즉시 이동, 아니면 2구까지 던졌을 때 이동
            if current_frame["roll_1"] == 10 or current_frame["roll_2"] is not None:
                self.current_frame_idx += 1

        # 마지막 10프레임 처리 (인덱스 9)
        else:
            reset_needed = False
            # 2구까지 던진 후 판정
            if current_frame["roll_2"] is not None and current_frame["roll_3"] is None:
                # 1, 2구 합이 10미만이면 보너스 없이 종료
                if (current_frame["roll_1"] + current_frame["roll_2"]) < 10:
                    reset_needed = True
            # 3구까지 다 던졌으면 종료
            elif current_frame["roll_3"] is not None:
                reset_needed = True

            if reset_needed:
                print(f"최종점수: {self.total_score()}")
                self.reset_game()

    def total_score(self, to_frame=9):
        total = 0
        all_rolls=[]
        for f in self.frames:
            for key in ["roll_1", "roll_2", "roll_3"]:
                if key in f and f[key] is not None:
                    all_rolls.append(f[key])

        roll_ptr = 0
        for idx in range(to_frame + 1):
            if idx >= 10:
                break
            #스트라이크 보너스
            if self.strike(idx):
                total += 10 + self._get_bonus(all_rolls, roll_ptr, 2)
                roll_ptr += 1
            #스페어 보너스
            elif self.spare(idx):
                total += 10 + self._get_bonus(all_rolls, roll_ptr, 1)
                roll_ptr += 2
            #일반 프레임 합산
            else:
                f = self.frames[idx]
                total += (f["roll_1"] or 0) + (f["roll_2"] or 0)
                roll_ptr += 2 if idx < 9 else 3
        return total
    
    # --- 보조 연산 로직 ---
    def strike(self, idx):
        return self.frames[idx]["roll_1"] == 10
    
    def spare(self, idx):
        r1 = self.frames[idx]["roll_1"]
        r2 = self.frames[idx]["roll_2"]
        if r1 is not None and r2 is not None:
            return r1 < 10 and (r1 + r2 == 10)
        return False
    
    def _get_bonus(self, all_rolls, ptr, count):
        bonus = 0
        try:
            for i in range(1, count + 1):
                bonus += all_rolls[ptr + i]
        except (IndexError, TypeError):
            pass
        return bonus

def main(page: ft.Page):
    page.title = "SS Bowling Calculator"
    page.bgcolor = "white"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    calc = bowling_score_calculator()

    roll1_texts = [ft.Text("", size=12, weight="bold") for _ in range(10)]
    roll2_texts = [ft.Text("", size=12, weight="bold") for _ in range(10)]
    roll3_texts = [ft.Text("", size=12, weight="bold") for _ in range(10)]

    accum_texts = [ft.Text("", size=16, weight="bold", color="blue") for _ in range(11)]

    def create_frame_ui(idx):

        roll_row = ft.Row(
            [
                ft.Container(roll1_texts[idx], width=22, height=22, alignment="center", border=ft.border.all(1)),
                ft.Container(roll2_texts[idx], width=22, height=22, alignment="center", border=ft.border.all(1)),
                ft.Container(
                    roll3_texts[idx] if idx == 9 else ft.Text(""),
                    width=22,
                    height=22,
                    alignment="center",
                    border=ft.border.all(1),
                ),
            ],
            spacing=0
        )

        return ft.Container(
            content=ft.Column(
                [
                    roll_row,
                    ft.Container(accum_texts[idx],height=35,alignment="center",border=ft.border.only(top=ft.border.BorderSide(1)))
                ],
                spacing=0
            ),
            width=70,
            height=70, 
            border=ft.border.all(1)
        )

    scoreboard=ft.Row(
        [create_frame_ui(i) for i in range(10)] +
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(ft.Text("TOTAL",color="white"),bgcolor="#555",height=30,alignment="center"),
                        ft.Container(accum_texts[10],height=40,alignment="center")
                    ],
                    spacing=0
                ),
                width=75,
                height=70,
                border=ft.border.all(1),
                bgcolor="#FFF9C4"
            )
        ],
        spacing=3,
        alignment=ft.MainAxisAlignment.CENTER
    )

    def update_ui():

        for i in range(10):

            f = calc.frames[i]

            r1 = ""
            r2 = ""
            r3 = ""

            if f["roll_1"] is not None:
                r1 = "X" if f["roll_1"] == 10 else ("-" if f["roll_1"] == 0 else str(f["roll_1"]))

            if f["roll_2"] is not None:
                if (f["roll_1"] or 0) + (f["roll_2"] or 0) == 10 and f["roll_1"] != 10:
                    r2 = "/"
                else:
                    r2 = "-" if f["roll_2"] == 0 else str(f["roll_2"])

            if i == 9 and f.get("roll_3") is not None:
                r3 = "X" if f["roll_3"] == 10 else ("-" if f["roll_3"] == 0 else str(f["roll_3"]))

            roll1_texts[i].value = r1
            roll2_texts[i].value = r2
            roll3_texts[i].value = r3

            if f["roll_1"] is not None:
                accum_texts[i].value = str(calc.total_score(i))
            else:
                accum_texts[i].value = ""

        accum_texts[10].value = str(calc.total_score(9))

        page.update()

    # 버튼 클릭 이벤트
    def button_click(e):

        t=e.control.data

        if t=="X":
            val=10
        elif t=="/":
            r1=calc.frames[calc.current_frame_idx]["roll_1"] or 0
            val=10-r1
        elif t=="-":
            val=0
        else:
            val=int(t)

        calc.add_score(val)
        update_ui()

    def b(text):
        return ft.FilledButton(text, width=70, height=70, data=text, on_click=button_click)

    #--- UI ---
    page.add(
        ft.Column(
            [
                ft.Text("BOWLING SCORE BOARD",size=28,weight="bold"),
                ft.Container(height=20),
                scoreboard,
                ft.Container(height=40),

                ft.Row([b("1"),b("2"),b("3"),b("-")],alignment="center"),
                ft.Row([b("4"),b("5"),b("6"),b("/")],alignment="center"),
                ft.Row([b("7"),b("8"),b("9"),b("X")],alignment="center"),

                ft.Row(
                    [
                        ft.FilledButton("CANCEL",width=150),
                        ft.FilledButton("SAVE",width=150)
                    ],
                    alignment="center"
                )
            ],
            horizontal_alignment="center"
        )
    )

ft.app(target=main)