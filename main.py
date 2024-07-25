import string
import time
import random
import flet as ft
import telebot
import sqlite3

def manage_data(password):
   conn = sqlite3.connect('database.db')
   c = conn.cursor()

   # Создание таблицы, если она еще не существует
   c.execute("""CREATE TABLE IF NOT EXISTS my_table (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               password TEXT,
               prompt TEXT,
               tg TEXT
               )""")

   # Вставка только пароля в таблицу
   c.execute("INSERT INTO my_table (password) VALUES (?)", (password,))

   # Получаем ID последней вставленной записи
   last_id = c.lastrowid

   conn.commit()
   conn.close()

   return last_id

def update_additional_data(id, tg):
   conn = sqlite3.connect('database.db')
   c = conn.cursor()

   c.execute("UPDATE my_table SET tg = ? WHERE id = ?", (tg, id))

   conn.commit()
   conn.close()

def update_prompt_data(e, prompt_value, id):
    # Реализуйте логику обновления данных в базе данных
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE my_table SET prompt = ? WHERE id = ?", (prompt_value, id))
    conn.commit()
    conn.close()
    print(f"Данные обновлены для ID: {id}")



def get_tg_data():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Проверяем, существует ли таблица my_table
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='my_table'")
        table_exists = c.fetchone()[0] > 0

        if table_exists:
            # Выполняем запрос для получения id и tg, где tg равен '1'
            c.execute("SELECT id, tg FROM my_table WHERE tg = '1'")

            # Получаем все результаты
            results = c.fetchall()

            if results:
                print("Успех")
                print("Записи, где tg равен '1':")
                for row in results:
                    print(f"ID: {row[0]}, TG: {row[1]}")
                return True
            else:
                print("Нет записей, где tg равен '1'")
                return False
        else:
            print("Таблица my_table не найдена в базе данных.")
            return False
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return False
    finally:
        pass

def main(page: ft.Page):
    id_container = [None]

    success = get_tg_data()

    if success:
        page.title = "Регистрация"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        prompt = ft.TextField(
            label="Введите ваш текст",
            width=300,
        )

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Выполняем запрос для получения id и tg, где tg равен '1'
        c.execute("SELECT id, tg FROM my_table WHERE tg = '1'")

        # Получаем все результаты
        results = c.fetchall()

        conn.close()

        if results:
            for row in results:
                print(f"ID: {row[0]}")
                confirm_button = ft.ElevatedButton(
                    text="сохранить",
                    on_click=lambda e: update_prompt_data(e, prompt.value, row[0])
                )
                page.add(prompt, confirm_button)
        else:
            page.add(ft.Text("Нет данных для отображения."))
    else:
        page.title = "Регистрация"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        password1 = ft.TextField(
            label="Введите пароль",
            password=True,
            can_reveal_password=True,
            width=300,
        )

        password2 = ft.TextField(
            label="Введите пароль повторно",
            password=True,
            can_reveal_password=True,
            width=300,
        )

        result = ft.Text()

        def save_password(e):
            password = password1.value
            id_container[0] = manage_data(password)
            print(id_container[0])
            result.value = f"Пароль сохранен в базе данных. ID: {id_container[0]}"
            page.update()

        def diss_window(e):
            save_password(e)
            dlg = ft.AlertDialog(
                title=ft.Text("Вы успешно зарегестрировались"),
            )
            page.open(dlg)
            time.sleep(1)
            page.close(dlg)

        def accept_window(e):
            if password1.value == password2.value:
                page.close(dlg_modal)
                save_password(e)
                time.sleep(0.1)
                show_window2()
            else:
                page.close(dlg_modal)

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Выберите"),
            content=ft.Text("Хотите привязать доп защиту телеграмм?"),
            actions=[
                ft.TextButton("Да", on_click=accept_window),
                ft.TextButton("Нет", on_click=diss_window),
            ],
        )

        confirm_button = ft.ElevatedButton(text="Подтвердить", on_click=lambda e: page.open(dlg_modal))

        page.add(password1, password2, confirm_button, result)

        def show_window2():
            page.clean()
            time.sleep(0.1)
            page.add(tg_window())

        def tg_window():
            token_field = ft.TextField(label="Токен", width=200)
            id_field = ft.TextField(label="Айди", width=200)
            send_code_button = ft.ElevatedButton("Получить код", on_click=lambda _: show_window3(token_field, id_field))

            return ft.Column([
                ft.Text("Телеграмм защита"),
                token_field,
                id_field,
                send_code_button
            ])

        def show_window3(token_field, id_field):
            page.clean()
            time.sleep(0.1)
            page.add(code_window(token_field, id_field))

        def generate_random_code(length=6):
            characters = string.ascii_uppercase + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        def update_data():
            print(id_container[0])
            if id_container[0] is None:
                print("Сначала сохраните пароль!")
            else:
                tg = 1
                update_additional_data(id_container[0], tg)
                print(f"Дополнительные данные обновлены для ID {id_container[0]}.")
            page.update()

        def check_code(code_field, code):
            if code_field == code:
                print("Код введён верно!")
                update_data()
                dlg = ft.AlertDialog(
                    title=ft.Text("Вы успешно зарегестрировались, перезапустите программу!"),
                )
                page.open(dlg)
            else:
                print("Пароль неверный!")

        def code_window(token_field, id_field):
            print("123")
            code = generate_random_code()
            bot = telebot.TeleBot(token_field.value)
            bot.send_message(int(id_field.value), code)
            code_field = ft.TextField(label="Код", width=200)
            accept_button = ft.ElevatedButton("Подтверидть", on_click=lambda _: check_code(code_field.value, code))
            return ft.Column([
                code_field,
                accept_button,
                ft.Text("Third Window"),
                ft.Text(f"Token: {token_field.value}"),
                ft.Text(f"ID: {id_field.value}")
            ])


ft.app(target=main)
