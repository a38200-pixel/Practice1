import flet as ft
import re
import sqlite3

# [전화번호부 DB 관리]
class TelephoneBook:
    def __init__(self):
        self.conn = sqlite3.connect("phonebook.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, birthday TEXT, gender TEXT, 
                phone_number TEXT, email TEXT, workplace TEXT
            )
        """)
        self.conn.commit()

    def add_contact(self, name, birthday, gender, phone_number, email, workplace):
        query = "INSERT INTO contacts (name, birthday, gender, phone_number, email, workplace) VALUES (?, ?, ?, ?, ?, ?)"
        self.conn.execute(query, (name, birthday, gender, phone_number, email, workplace))
        self.conn.commit()

    def update_contact(self, db_id, **kwargs):
        keys = [f"{key} = ?" for key in kwargs.keys()]
        query = f"UPDATE contacts SET {', '.join(keys)} WHERE id = ?"
        self.conn.execute(query, list(kwargs.values()) + [db_id])
        self.conn.commit()

    def delete_contact(self, db_id):
        self.conn.execute("DELETE FROM contacts WHERE id = ?", (db_id,))
        self.conn.commit()

    def search_contact(self, name):
        cursor = self.conn.execute("SELECT * FROM contacts WHERE name LIKE ? ORDER BY name", (f"%{name}%",))
        return cursor.fetchall()

    def get_all_contacts(self):
        cursor = self.conn.execute("SELECT * FROM contacts ORDER BY name")
        return cursor.fetchall()

# [메인 UI 및 핸들러]
def main(page: ft.Page):
    page.title = "전화번호부 관리 시스템"
    page.padding = 20
    book = TelephoneBook()
    state = {"selected_id": None}

    # --- 입력 부품 ---
    name_in = ft.TextField(label="이름", hint_text="한글 2~10자", width=230)
    birth_in = ft.TextField(label="생년월일", hint_text="1999-01-01", width=230)
    gender_in = ft.Dropdown(label="성별", hint_text="선택", width=120, options=[ft.dropdown.Option("남"), ft.dropdown.Option("여")])
    phone_in = ft.TextField(label="전화번호", hint_text="010-1234-5678", width=230)
    email_in = ft.TextField(label="이메일", hint_text="example@mail.com", width=230)
    work_in = ft.TextField(label="직장명", hint_text="직장 또는 학교", width=230)
    
    search_in = ft.TextField(label="검색할 이름 입력", expand=True)
    list_view = ft.Column(expand=True)

    # --- 통합 안내 메시지 영역 ---
    info_msg_area = ft.Text("", weight="bold")

    def set_info_msg(text, is_error=False):
        info_msg_area.value = text
        info_msg_area.color = ft.Colors.RED if is_error else ft.Colors.BLUE
        page.update()

    # --- 입력값 검증 ---
    def validate():
        if not re.match(r'^[가-힣]{2,10}$', name_in.value):
            set_info_msg("오류: 이름 형식을 확인하세요 (한글 2~10자).", True)
            return False
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', birth_in.value):
            set_info_msg("오류: 생년월일 형식을 확인하세요 (YYYY-MM-DD).", True)
            return False
        if not gender_in.value:
            set_info_msg("오류: 성별을 선택해주세요.", True)
            return False
        if not re.match(r'^010-\d{4}-\d{4}$', phone_in.value):
            set_info_msg("오류: 전화번호 형식을 확인하세요.", True)
            return False
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_in.value):
            set_info_msg("오류: 이메일 형식을 확인하세요.", True)
            return False
        return True

    # --- 카드 생성 ---
    def create_card(row):
        db_id, name, birthday, gender, phone, email, workplace = row
        
        name_txt = ft.Text(f"{name} ({gender})", size=16, weight="bold")
        info_txt = ft.Text(f"{phone} | {birthday}")
        work_txt = ft.Text(f"{email} | {workplace}", color=ft.Colors.GREY_700)
        
        info_col = ft.Column([name_txt, info_txt, work_txt], expand=True, spacing=2)
        
        btn_edit = ft.TextButton("수정", on_click=lambda e: load_for_edit(row))
        btn_del = ft.TextButton("삭제", on_click=lambda e: handle_delete(db_id))
        button_row = ft.Row([btn_edit, btn_del])
        
        return ft.Card(content=ft.Container(padding=15, content=ft.Row([info_col, button_row])))

    # --- 핸들러 함수들 ---
    def refresh_list(data=None):
        list_view.controls.clear()
        items = data if data is not None else book.get_all_contacts()
        for row in items:
            list_view.controls.append(create_card(row))
        page.update()

    def handle_save(e):
        if not validate(): return
        book.add_contact(
            name_in.value, birth_in.value, gender_in.value, 
            phone_in.value, email_in.value, work_in.value or "없음"
        )
        set_info_msg("정상적으로 저장되었습니다.")
        handle_clear(is_internal=True); refresh_list()

    def load_for_edit(row):
        state["selected_id"] = row[0]
        name_in.value, birth_in.value, gender_in.value = row[1], row[2], row[3]
        phone_in.value, email_in.value, work_in.value = row[4], row[5], row[6]
        set_info_msg("수정할 내용을 입력 중입니다...")
        btn_add.visible, btn_update.visible = False, True
        page.update()

    def handle_update(e):
        if not validate(): return
        book.update_contact(
            state["selected_id"], 
            name=name_in.value, birthday=birth_in.value, gender=gender_in.value, 
            phone_number=phone_in.value, email=email_in.value, workplace=work_in.value
        )
        set_info_msg("수정 사항이 반영되었습니다.")
        handle_clear(is_internal=True); refresh_list()

    def handle_delete(db_id):
        book.delete_contact(db_id)
        set_info_msg("연락처가 삭제되었습니다.", True)
        refresh_list()

    def handle_clear(e=None, is_internal=False):
        name_in.value = birth_in.value = phone_in.value = email_in.value = work_in.value = ""
        gender_in.value = None
        if not is_internal:
            info_msg_area.value = ""
        btn_add.visible, btn_update.visible = True, False
        page.update()

    # --- 레이아웃 조립 ---
    btn_add = ft.ElevatedButton("새 연락처 등록", on_click=handle_save)
    btn_update = ft.ElevatedButton("수정 내용 저장", on_click=handle_update, visible=False)
    
    action_row = ft.Row([
        btn_add, 
        btn_update, 
        ft.TextButton("초기화", on_click=handle_clear),
        info_msg_area
    ], alignment=ft.MainAxisAlignment.START)

    input_box = ft.Container(
        padding=20, bgcolor=ft.Colors.GREY_100, border_radius=10,
        content=ft.Column([
            ft.Text("정보 입력 및 관리", size=18, weight="bold"),
            ft.Row([name_in, birth_in, gender_in], spacing=10),
            ft.Row([phone_in, email_in, work_in], spacing=10),
            action_row
        ], spacing=10)
    )

    search_box = ft.Row([
        search_in,
        ft.ElevatedButton("검색", on_click=lambda e: refresh_list(book.search_contact(search_in.value))),
        ft.TextButton("전체보기", on_click=lambda e: refresh_list())
    ])

    page.add(input_box, ft.Divider(height=20), search_box, list_view)
    refresh_list()

if __name__ == "__main__":
    ft.app(target=main)