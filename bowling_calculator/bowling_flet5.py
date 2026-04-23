import flet as ft

class BowlingScoreCalculator:
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
        self.game_over = False

    def current_frame(self):
        return self.frames[self.current_frame_idx]

    def add_score(self, pins, foul=False):
        if self.game_over:
            return False
        if foul:
            actual_score = 0
        else:
            actual_score = pins
        cf = self.current_frame()

        if self.current_frame_idx < 9:
            if cf["roll_1"] is None:
                if actual_score > 10:
                    return False
                cf["roll_1"] = actual_score
            #1투구, 2투구 합이 10 못넘게 체크
            else:
                if cf["roll_1"] + actual_score > 10:
                    return False
                cf["roll_2"] = actual_score
        #10프레임 처리
        else:
            r1, r2 = cf["roll_1"], cf["roll_2"]
            if r1 is None:
                if actual_score > 10:
                    return False
                cf["roll_1"] = actual_score
            elif r2 is None:
                if r1 == 10:
                    if actual_score > 10:
                        return False
                else:
                    if r1 + actual_score > 10:
                        return False
                cf["roll_2"] = actual_score
            elif cf["roll_3"] is None:
                #스트라이크시
                if r1 == 10:
                    if r2 == 10:
                        if actual_score > 10:
                            return False
                #스페어시
                elif r1 + r2 == 10:
                    if actual_score > 10:
                        return False
                    
                cf["roll_3"] = actual_score

        self._move_frame()
        return True

    def _move_frame(self):
        cf = self.current_frame()
        if self.current_frame_idx < 9:
            #스트라이크 or 2구까지 던지면 프레임 이동
            if cf["roll_1"] == 10 or cf["roll_2"] is not None:
                if self.current_frame_idx < 9:
                    self.current_frame_idx += 1
        else:
            r1, r2, r3 = cf["roll_1"], cf["roll_2"], cf["roll_3"]
            #3구 보너스 던질 수 있는지 확인
            if r2 is not None:
                bonus_earned = (r1 == 10) or ((r1 or 0) + (r2 or 0) >= 10)
                #3구 보너스 못얻으면 종료
                if not bonus_earned:
                    self.game_over = True
                #3구 던지면 종료
                elif r3 is not None:
                    self.game_over = True

    def total_score(self, to_frame=9):
        total = 0
        all_rolls = []  #모든 프레임 투구 점수 리스트

        #모든 프레임 투구 기록 확인 후 값이 있는 것만 리스트에 담음
        for f in self.frames:
            for key in ["roll_1", "roll_2", "roll_3"]:
                if key in f and f[key] is not None:
                    all_rolls.append(f[key])
        roll_ptr = 0  #roll_ptr = all_rolls=[]의 몇번째 값을 읽고 있는지 가리키는 인덱스

        for idx in range(min(to_frame + 1, 10)):
            f = self.frames[idx]

            # 1~9 프레임 - 스트라이크시 10점에 다음 2개의 투구 점수 더함 + 1반 던졌으니 ptr 1칸 이동
            if self.strike(idx) and idx < 9:
                total += 10 + self._get_bonus(all_rolls, roll_ptr, 2)
                roll_ptr += 1

            #스페어시 10점에 다음 1개의 투구 점수 더함 + 2번 던졌으니 ptr 두칸 이동
            elif self.spare(idx) and idx < 9:
                total += 10 + self._get_bonus(all_rolls, roll_ptr, 1)
                roll_ptr += 2

            #스트라이크 or 스페어 아닌 경우, 10번 프레임인 경우
            else:
                if idx < 9:
                    total += (f["roll_1"] or 0) + (f["roll_2"] or 0)
                    roll_ptr += 2
                else:
                    total += (f["roll_1"] or 0) + (f["roll_2"] or 0) + (f.get("roll_3") or 0)
                    roll_ptr += 3

        return total

    # --- 보조 로직 ---
    def strike(self, idx):
        return self.frames[idx]["roll_1"] == 10

    def spare(self, idx):
        r1 = self.frames[idx]["roll_1"]
        r2 = self.frames[idx]["roll_2"]
        if r1 is not None and r2 is not None:
            return r1 < 10 and (r1 + r2 == 10)
        return False
    
    #스트라이크, 스페어 보너스 점수 계산
    def _get_bonus(self, all_rolls, ptr, count):  #count = 몇개의 다음 투구를 더할지, 스트라이크는 2, 스페어는 1
        bonus = 0
        for i in range(1, count + 1):
            if ptr + i < len(all_rolls):
                bonus += all_rolls[ptr + i]
        return bonus
    #이렇게도 사용 가능
    '''def _get_bonus(self, all_rolls, ptr, count):
            return sum(all_rolls[ptr+1 : ptr+1+count])'''

    #화면 출력 변환
    def frame_display(self, idx):
        f = self.frames[idx]
        r1, r2, r3 = f["roll_1"], f["roll_2"], f.get("roll_3")
        
        def display_roll(val, prev=None):  #val = 현재 투구 점수, prev = 이전 투구 점수
            if val is None:
                return ""
            if val == 0:
                return "-"
            if val == 10 and prev is None:
                return "X"
            if prev is not None and prev + val == 10:
                return "/"
            return str(val)

        if idx < 9:
            s1 = display_roll(r1)

            if r1 != 10:
                s2 = display_roll(r2, r1)
            else:
                s2 = display_roll(r2)
            # 누적 점수 표시, cum = 누적점수
            if r2 is not None or r1 == 10:
                cum = str(self.total_score(idx))
            #아직 프레임 진행 중일 때는 점수 안나오게
            else:
                cum = ""

            return s1, s2, None, cum
        # 10프레임 일 때
        else:
            s1 = display_roll(r1)

            if r1 == 10:
                s2 = display_roll(r2)

                if r2 is not None:
                    s3 = display_roll(r3, r2)
                else:
                    s3 = ""

            else:
                s2 = display_roll(r2, r1)

                if r3 is not None:
                    s3 = display_roll(r3)
                else:
                    s3 = ""

            if self.game_over:
                cum = str(self.total_score(9))
            else:
                cum = ""

            return s1, s2, s3, cum


#  --- 색상 ---
BG        = "#EFEFEF"   #BackGroundcolor
CARD      = "#FFFFFF"   
SCORE_BG  = "#D8D8D8"   
BTN_LIGHT = "#FFFFFF"
BTN_DARK  = "#8E8E93"
BTN_TEXT  = "#1C1C1E"
ACCENT    = "#007AFF"
RED       = "#FF3B30"
BORDER    = "#BBBBBB"
TEXT_MAIN = "#1C1C1E"
TEXT_SUB  = "#636366"
STRIKE_C  = "#FF9500"
SPARE_C   = "#34C759"



#  --- 메인 UI ---
def main(page: ft.Page):
    page.title = "볼링 점수 계산기"
    page.bgcolor = BG
    page.window.width = 420
    page.window.height = 740
    page.window.resizable = False

    calc = BowlingScoreCalculator()
    input_buffer = []
    score_cells = []   # (roll1_txt, roll2_txt, roll3_txt|None, cum_txt)

    # --- 점수판 ---
    def build_scoreboard():
        frame_cols = []
        for i in range(10):
            is_last = (i == 9)

            r1 = ft.Text("", size=11, color=TEXT_MAIN, weight="bold", text_align="center")
            r2 = ft.Text("", size=11, color=TEXT_MAIN, weight="bold", text_align="center")
            r3 = ft.Text("", size=11, color=TEXT_MAIN, weight="bold", text_align="center") if is_last else None

            if is_last:
                # 10프레임: 작은 칸 3개 (각 20px)
                roll_row = ft.Row(
                    controls=[
                        ft.Container(r1, width=20, height=22, alignment=ft.Alignment(0, 0),
                                     border=ft.border.only(right=ft.BorderSide(1, BORDER))),
                        ft.Container(r2, width=20, height=22, alignment=ft.Alignment(0, 0),
                                     border=ft.border.only(right=ft.BorderSide(1, BORDER))),
                        ft.Container(r3, width=20, height=22, alignment=ft.Alignment(0, 0)),
                    ],
                    spacing=0, tight=True,
                )
                frame_w = 60
            else:
                # 1~9프레임: 작은 칸 2개 (각 15px), 프레임 전체 30px
                roll_row = ft.Row(
                    controls=[
                        ft.Container(r1, width=15, height=22, alignment=ft.Alignment(0, 0),
                                     border=ft.border.only(right=ft.BorderSide(1, BORDER))),
                        ft.Container(r2, width=15, height=22, alignment=ft.Alignment(0, 0)),
                    ],
                    spacing=0, tight=True,
                )
                frame_w = 30

            cum = ft.Text("", size=13, color=TEXT_MAIN, weight="bold", text_align="center")

            frame_box = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=roll_row,
                            bgcolor=SCORE_BG,
                            border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
                            height=22,
                            width=frame_w,
                        ),
                        ft.Container(
                            content=cum,
                            height=32,
                            width=frame_w,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    spacing=0,
                    tight=True,
                ),
                width=frame_w,
                border=ft.border.only(right=ft.BorderSide(1, BORDER) if i < 9 else None),
            )

            score_cells.append((r1, r2, r3, cum))
            frame_cols.append(frame_box)

        # 프레임 번호 행
        num_cells = []
        for i in range(10):
            is_last = (i == 9)
            w = 60 if is_last else 30
            num_cells.append(
                ft.Container(
                    content=ft.Text(str(i + 1), size=10, color=TEXT_SUB, text_align="center"),
                    width=w, height=18,
                    alignment=ft.Alignment(0, 0),
                    border=ft.border.only(right=ft.BorderSide(1, BORDER) if i < 9 else None),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(controls=num_cells, spacing=0, tight=True),
                        bgcolor=SCORE_BG,
                        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
                    ),
                    ft.Row(controls=frame_cols, spacing=0, tight=True),
                ],
                spacing=0,
                tight=True,
            ),
            bgcolor=CARD,
            border_radius=8,
            border=ft.border.all(1, BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    # --- 상태/입력 표시 ---
    status_txt = ft.Text("1프레임 1구", size=13, color=TEXT_SUB)
    input_disp = ft.Text("", size=36, color=TEXT_MAIN, weight="bold", text_align="right")

    def get_status():
        if calc.game_over:
            return f"게임 종료  최종: {calc.total_score()}점"
        idx = calc.current_frame_idx
        cf = calc.current_frame()
        roll_no = 1 if cf["roll_1"] is None else (2 if cf["roll_2"] is None else 3)
        return f"{idx + 1}프레임 {roll_no}구"

    def refresh_board():
        for i in range(10):
            s1, s2, s3, cum = calc.frame_display(i)
            r1t, r2t, r3t, cumt = score_cells[i]
            r1t.value = s1
            r1t.color = STRIKE_C if s1 == "X" else TEXT_MAIN
            r2t.value = s2
            r2t.color = SPARE_C if s2 == "/" else (STRIKE_C if s2 == "X" else TEXT_MAIN)
            if r3t is not None:
                r3t.value = s3 or ""
                r3t.color = SPARE_C if s3 == "/" else (STRIKE_C if s3 == "X" else TEXT_MAIN)
            cumt.value = cum
        status_txt.value = get_status()
        page.update()

    def update_disp():
        input_disp.value = "".join(input_buffer)
        page.update()

    # --- 버튼 동작 ---
    def on_digit(d):
        if calc.game_over:
            return

        # X: 스트라이크 → 즉시 10점 저장
        if d == 10:
            if calc.add_score(10):
                input_buffer.clear()
                refresh_board()
                update_disp()
            return

        # /: 스페어 → 남은 핀 계산 후 즉시 저장
        if d == "/":
            cf = calc.current_frame()
            idx = calc.current_frame_idx
            if idx < 9:
                # 1~9프레임: 2구에서만 유효
                if cf["roll_1"] is not None and cf["roll_2"] is None:
                    spare_pins = 10 - cf["roll_1"]
                    if calc.add_score(spare_pins):
                        input_buffer.clear()
                        refresh_board()
                        update_disp()
            else:
                # 10프레임: 2구 또는 3구에서 유효
                if cf["roll_1"] is not None and cf["roll_2"] is None:
                    spare_pins = 10 - cf["roll_1"]
                    if calc.add_score(spare_pins):
                        input_buffer.clear()
                        refresh_board()
                        update_disp()
                elif cf["roll_2"] is not None and cf["roll_3"] is None:
                    spare_pins = 10 - cf["roll_2"]
                    if calc.add_score(spare_pins):
                        input_buffer.clear()
                        refresh_board()
                        update_disp()
            return

        # - : 0점 → 버퍼에 표시, SAVE로 저장
        if d == "-":
            if not input_buffer:
                input_buffer.append("-")
                update_disp()
            return

        # 숫자 입력
        if len(input_buffer) >= 2:
            return
        if input_buffer == ["-"]:
            input_buffer.clear()
        input_buffer.append(str(d))
        update_disp()

    def on_save():
        if calc.game_over or not input_buffer:
            return
        raw = "".join(input_buffer)
        val = 0 if raw == "-" else int(raw)
        if calc.add_score(val):
            input_buffer.clear()
            refresh_board()
            update_disp()
        else:
            input_disp.color = RED
            page.update()
            import time; time.sleep(0.2)
            input_disp.color = TEXT_MAIN
            input_buffer.clear()
            update_disp()

    def on_cancel():
        input_buffer.clear()
        update_disp()

    def on_new_game(e):
        calc.reset_game()
        input_buffer.clear()
        for r1t, r2t, r3t, cumt in score_cells:
            r1t.value = r2t.value = cumt.value = ""
            if r3t:
                r3t.value = ""
        refresh_board()
        update_disp()

    # --- 버튼 빌더 ---
    def btn(label, fn, bg=BTN_LIGHT, fg=BTN_TEXT, w=74, h=60, fs=22):
        def _click(e):
            fn()
        return ft.Container(
            content=ft.Text(label, size=fs, color=fg, weight="w500", text_align="center"),
            width=w, height=h,
            bgcolor=bg,
            border_radius=16,
            alignment=ft.Alignment(0, 0),
            on_click=_click,
            ink=True,
        )

    GAP = 10
    BW  = 74
    BH  = 60

    keypad = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    btn("1", lambda: on_digit(1)),
                    btn("2", lambda: on_digit(2)),
                    btn("3", lambda: on_digit(3)),
                    btn("-", lambda: on_digit("-"), bg=BTN_DARK, fg=CARD),
                ],
                spacing=GAP,
                alignment="center",
            ),
            ft.Row(
                controls=[
                    btn("4", lambda: on_digit(4)),
                    btn("5", lambda: on_digit(5)),
                    btn("6", lambda: on_digit(6)),
                    btn("/", lambda: on_digit("/"), bg=BTN_DARK, fg=CARD),
                ],
                spacing=GAP,
                alignment="center",
            ),
            ft.Row(
                controls=[
                    btn("7", lambda: on_digit(7)),
                    btn("8", lambda: on_digit(8)),
                    btn("9", lambda: on_digit(9)),
                    btn("X", lambda: on_digit(10), bg=BTN_DARK, fg=CARD),
                ],
                spacing=GAP,
                alignment="center",
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text("CANCEL", size=16, color=BTN_TEXT, weight="w500", text_align="center"),
                        width=BW * 2 + GAP, height=BH,
                        bgcolor=BTN_LIGHT,
                        border_radius=16,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: on_cancel(),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("SAVE", size=16, color=CARD, weight="bold", text_align="center"),
                        width=BW * 2 + GAP, height=BH,
                        bgcolor=ACCENT,
                        border_radius=16,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: on_save(),
                        ink=True,
                    ),
                ],
                spacing=GAP,
                alignment="center",
            ),
        ],
        spacing=GAP,
        horizontal_alignment="center",
    )

    # --- 입력 영역 ---
    input_area = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        status_txt,
                        ft.Container(expand=True),
                        ft.TextButton("New Game", on_click=on_new_game),
                    ],
                ),
                ft.Container(
                    content=input_disp,
                    height=50,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
            ],
            spacing=0,
        ),
        bgcolor=CARD,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=14, vertical=8),
        border=ft.border.all(1, BORDER),
    )

    scoreboard = build_scoreboard()

    page.add(
        ft.Column(
            controls=[
                ft.Container(height=10),
                ft.Text(
                    "볼링 점수판",
                    size=22,
                    weight="bold",
                    color=TEXT_MAIN,
                    text_align="center",
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Row(
                        controls=[scoreboard],
                        scroll="auto",
                    ),
                    padding=ft.padding.symmetric(horizontal=12),
                ),
                ft.Container(height=10),
                ft.Container(
                    content=input_area,
                    padding=ft.padding.symmetric(horizontal=12),
                ),
                ft.Container(height=10),
                ft.Container(
                    content=keypad,
                    padding=ft.padding.symmetric(horizontal=12),
                ),
            ],
            horizontal_alignment="center",
            scroll="auto",
        )
    )

    refresh_board()


ft.app(target=main)