import flet as ft
import sys
import json
import os
from datetime import datetime, timedelta
from mart_db import db_list

# --- 파일 경로 설정 ---
INVENTORY_FILE = "inventory_data.json"
SALES_FILE = "sales_history.json"

# --- 데이터 로드 및 저장 함수 ---
def load_all_data():
    # 재고 데이터 로드: 파일 없으면 mart_db.db_list 사용
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            inventory = json.load(f)
    else:
        inventory = db_list.copy() # 초기값 복사
    
    # 매출 데이터 로드: 파일 없으면 빈 딕셔너리 생성
    if os.path.exists(SALES_FILE):
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            sales = json.load(f)
    else:
        sales = {}
        
    return inventory, sales

def save_all_data(inventory, sales):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=4)
    with open(SALES_FILE, "w", encoding="utf-8") as f:
        json.dump(sales, f, ensure_ascii=False, indent=4)

# --- 실행 시 데이터 불러오기 ---
current_db, sales_history = load_all_data()
num_to_item = {}

def update_num_to_item():
    num_to_item.clear()
    for i, item_name in enumerate(current_db.keys(), start=1):
        num_to_item[i] = item_name

def add_sales_record(amount):
    now = datetime.now()
    y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    if y not in sales_history: sales_history[y] = {}
    if m not in sales_history[y]: sales_history[y][m] = {}
    if d not in sales_history[y][m]: sales_history[y][m][d] = 0
    sales_history[y][m][d] += amount
    save_all_data(current_db, sales_history) # 매출 기록 저장

update_num_to_item()

def main(page: ft.Page):
    page.title = "마트 POS v2.6 (Auto-Save)"
    page.window.width = 1100
    page.window.height = 850
    page.theme_mode = "light"
    
    total_sales = 0
    cart = []
    cart_total = 0

    # --- UI 컴포넌트 ---
    sales_text = ft.Text("총 누적 매출: 0원", size=18, weight="bold", color="blue")
    cart_total_text = ft.Text("장바구니 합계: 0원", size=18, weight="bold", color="green")
    log_text = ft.Text("상품을 선택해 주세요.", size=14, color="grey700")
    
    product_grid = ft.GridView(expand=True, max_extent=150, child_aspect_ratio=2.0, spacing=10)
    cart_list_view = ft.ListView(expand=True, spacing=5)
    db_viewer_list = ft.ListView(expand=True)

    name_input = ft.TextField(label="물품명", width=200)
    price_input = ft.TextField(label="가격", width=120)
    stock_input = ft.TextField(label="재고", width=120)

    # --- 공통 알림 ---
    def show_msg(title, msg):
        res_dlg = ft.AlertDialog(
            title=ft.Text(title), content=ft.Text(msg), 
            actions=[ft.TextButton("확인", on_click=lambda _: setattr(res_dlg, "open", False))]
        )
        page.overlay.append(res_dlg); res_dlg.open = True; page.update()

    # --- POS 기능 ---
    def update_product_grid():
        product_grid.controls.clear()
        for name in current_db.keys():
            price = current_db[name][0]
            product_grid.controls.append(ft.ElevatedButton(
                content=ft.Text(f"{name}\n{price:,}원", text_align="center", size=12),
                on_click=lambda e, n=name: add_to_cart(n),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2))
            ))
        page.update()

    def add_to_cart(item_name):
        nonlocal cart_total
        if current_db[item_name][1] >= 1:
            cart.append(item_name)
            current_db[item_name][1] -= 1 
            cart_total += current_db[item_name][0]
            save_all_data(current_db, sales_history) # 재고 변경 즉시 저장
            update_cart_view(); page.update()
        else:
            log_text.value = f"[{item_name}] 재고 부족!"; page.update()

    def update_cart_view():
        cart_list_view.controls.clear()
        for item in sorted(list(set(cart))):
            count = cart.count(item)
            cart_list_view.controls.append(ft.ListTile(title=ft.Text(f"{item} x {count}"), subtitle=ft.Text(f"{current_db[item][0]*count:,}원")))
        cart_total_text.value = f"장바구니 합계: {cart_total:,}원"

    def handle_payment(e):
        nonlocal cart_total, total_sales
        if not cart: return
        add_sales_record(cart_total)
        total_sales += cart_total
        sales_text.value = f"총 누적 매출: {total_sales:,}원"
        show_msg("결제 완료", f"{cart_total:,}원 결제")
        cart.clear(); cart_total = 0; update_cart_view(); page.update()

    # --- DB 관리 ---
    def update_db_viewer():
        db_viewer_list.controls.clear()
        for i, (name, val) in enumerate(current_db.items(), 1):
            db_viewer_list.controls.append(ft.Container(
                content=ft.Row([ft.Text(f"{i:02d}."), ft.Text(name, expand=True), ft.Text(f"{val[0]:,}원"), ft.Text(f"재고: {val[1]}개")]),
                padding=10, border=ft.border.only(bottom=ft.border.BorderSide(1, "grey300"))
            ))
        page.update()

    def save_item(e):
        try:
            name = name_input.value.strip()
            current_db[name] = [int(price_input.value), int(stock_input.value)]
            update_num_to_item(); update_db_viewer()
            save_all_data(current_db, sales_history) 
            show_msg("저장 완료", f"[{name}] 정보가 반영되었습니다.")
        except: show_msg("오류", "숫자 형식을 확인하세요.")

    # --- 매출 통계 조회 ---
    def get_day_sales(e):
        def on_change(e):
            sel = e.control.value + timedelta(hours=12) 
            y, m, d = sel.strftime("%Y"), sel.strftime("%m"), sel.strftime("%d")
            amt = sales_history.get(y, {}).get(m, {}).get(d, 0)
            show_msg("일 매출", f"{y}-{m}-{d} 매출액: {amt:,}원")
        dp = ft.DatePicker(on_change=on_change)
        page.overlay.append(dp); dp.open = True; page.update()

    def get_month_sales(e):
        y_in, m_in = ft.TextField(label="연도", value=datetime.now().strftime("%Y")), ft.TextField(label="월", value=datetime.now().strftime("%m"))
        def calc(e):
            total = sum(sales_history.get(y_in.value, {}).get(m_in.value, {}).values())
            show_msg("월 매출", f"{y_in.value}년 {m_in.value}월 합계: {total:,}원")
        dlg = ft.AlertDialog(title=ft.Text("월 매출 조회"), content=ft.Row([y_in, m_in]), actions=[ft.FilledButton("조회", on_click=calc)])
        page.overlay.append(dlg); dlg.open = True; page.update()

    def get_year_sales(e):
        y_in = ft.TextField(label="연도", value=datetime.now().strftime("%Y"))
        def calc_y(e):
            y_dict = sales_history.get(y_in.value, {})
            total = sum(sum(m.values()) for m in y_dict.values())
            show_msg("연 매출", f"{y_in.value}년 총 합계: {total:,}원")
        dlg = ft.AlertDialog(title=ft.Text("연 매출 조회"), content=y_in, actions=[ft.FilledButton("조회", on_click=calc_y)])
        page.overlay.append(dlg); dlg.open = True; page.update()

    # --- 레이아웃 조립 ---
    main_container = ft.Container(expand=True)
    pos_layout = ft.Column([
        ft.Row([ft.TextButton("메뉴로", on_click=lambda _: show_menu()), sales_text], alignment="space_between"),
        ft.Row([ft.Container(product_grid, expand=3), ft.VerticalDivider(), ft.Column([cart_total_text, ft.Container(cart_list_view, height=450, border=ft.border.all(1, "grey300")), ft.FilledButton("결제", on_click=handle_payment, width=300)], expand=2)], expand=True)
    ], expand=True)

    db_layout = ft.Column([
        ft.TextButton("메뉴로", on_click=lambda _: show_menu()),
        ft.Row([name_input, price_input, stock_input, ft.FilledButton("저장/수정", on_click=save_item)]),
        ft.Container(db_viewer_list, expand=True, border=ft.border.all(1, "grey300"))
    ], expand=True)

    def show_menu(e=None):
        main_container.content = ft.Column([
            ft.Text("마트 POS 시스템", size=30, weight="bold"),
            ft.FilledButton("1. POS 계산기", on_click=lambda _: setattr(main_container, "content", pos_layout) or update_product_grid() or page.update(), width=400, height=60),
            ft.FilledButton("2. 재고 관리", on_click=lambda _: setattr(main_container, "content", db_layout) or update_db_viewer() or page.update(), width=400, height=60),
            ft.FilledButton("3. 매출 통계", on_click=open_report_menu, width=400, height=60),
            ft.FilledButton("4. 종료", on_click=lambda _: sys.exit(), width=400, height=60),
        ], alignment="center", horizontal_alignment="center", spacing=20)
        page.update()

    def open_report_menu(e):
        report_dlg = ft.AlertDialog(
            title=ft.Text("매출 통계 센터"),
            content=ft.Column([
                ft.FilledButton("금일 매출", on_click=lambda _: show_msg("오늘", f"{sales_history.get(datetime.now().strftime('%Y'), {}).get(datetime.now().strftime('%m'), {}).get(datetime.now().strftime('%d'), 0):,}원"), width=300),
                ft.FilledButton("일 매출(달력)", on_click=get_day_sales, width=300),
                ft.FilledButton("월 매출", on_click=get_month_sales, width=300),
                ft.FilledButton("연 매출", on_click=get_year_sales, width=300),
            ], tight=True, spacing=10),
            actions=[ft.TextButton("닫기", on_click=lambda _: setattr(report_dlg, "open", False))]
        )
        page.overlay.append(report_dlg); report_dlg.open = True; page.update()

    page.add(main_container)
    show_menu()

if __name__ == "__main__":
    ft.app(main)