import sqlite3
import re


class UsersData:
    def __init__(self):
        self.db = sqlite3.connect('registration.db')
        self.cur = self.db.cursor()
        self.create_database()
        self.choosing_action()

    def create_database(self):
        """Создание базы данных"""
        # Создаем таблицу
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users_data (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT,
            Password TEXT,
            Code TEXT)""")
        print("Создание и подключение к базе данных users_data")

        # Проверяем, если ли пользователь с логином Ivan
        self.cur.execute("""SELECT 1 FROM users_data WHERE Login = (?) OR Login = (?)""", ("Ivan", "ivan"))
        # Если нет, добавляем в базу данных
        if not self.cur.fetchone():
            self.cur.execute("""INSERT INTO users_data(Login, Password, Code) VALUES(?,?,?)""",
                             ("Ivan", "qwer1234", "1234"))
            self.db.commit()

    def choosing_action(self):
        """Предлагаем сделать выбор одного из действия"""
        print(
            "Выберите одно из следующих действий:\n1.регистрация нового пользователя\n2.авторизация в системе\n3.восстановление пароля по коду")
        try:
            num_action = int(input())
            if num_action == 1:
                self.get_registration()
            elif num_action == 2:
                self.authorization()
            elif num_action == 3:
                self.recovery_password()
            else:
                print("Такого действия нет. Попробуйте еще раз")
                self.choosing_action()
        except ValueError:
            print("Вы ввели недопустимое значение. Попробуйте снова")
            self.choosing_action()

    def get_registration(self):
        """Регистрация нового пользователя"""
        while True:
            login = input("Введите логин: ").strip()  # Удаляем лишние пробелы
            # Проверяем, что поле логин заполнено
            if not login or re.match(r'^[^a-zA-Z]', login):
                print("Ошибка. Логин должен начинаться с буквы и не должен быть пустым")
                continue
            # Проверяем, есть ли пользователь с логином в базе данных
            self.cur.execute("""SELECT 1 FROM users_data WHERE LOWER(Login) = LOWER(?)""", (login,))
            if self.cur.fetchone():
                print("Ошибка. Логин уже существует, попробуйте снова.")
                continue
            break  # Если логина нет в базе данных, выходим из цикла

        while True:
            password = input("Введите пароль: ")
            # Проверяем, что пароль введен
            if not password:
                print("Ошибка. Пароль не может быть пустым. попробуйте снова")
                continue
            break  # Если пароль введен, выходим из цикла

        while True:
            code = input("Введите код: ")
            # Проверяем, что код введен и состоит из 4 цифр
            if not code.isdigit() or len(code) != 4:
                print("Ошибка. введите четырехзначный цифровой код")
                continue
            break  # Если код введен и состоит из 4 цифр, выходим из цикла
        new_user = (login, password, code)
        # Если все данные введены корректно, добавляем нового пользователя в базу данных
        self.cur.execute("""INSERT INTO users_data(Login, Password, Code) VALUES(?,?,?)""", new_user)
        self.db.commit()
        print("Вы успешно зарегистрировались!")

    def authorization(self):
        """Авторизация"""
        while True:
            login = input("Введите логин: ")
            # Проверяем, что ввели не пустой логин
            if not login:
                print("Логин не может быть пустым")
                continue

            password = input("Введите пароль: ")
            # Проверяем, что ввели не пустой пароль
            if not password:
                print("Пароль не может быть пустым")
                continue
            auth_data = (login, password)
            # Проверяем, есть ли пользователь с введенными логином и паролем в базе данных
            self.cur.execute(
                """SELECT 1 FROM users_data 
                WHERE LOWER(Login) = Lower(?) AND Password = (?)""", auth_data)

            # Если пользователя с таким логином и пароля нет, выдаем ошибку и просим ввести заново
            if not self.cur.fetchone():
                print("Ошибка. Неправильный логин или пароль. Попробуйте снова.")
                continue
            print("Успешная авторизация!")
            break  # Если пользователь существует, останавливаем цикл

    def recovery_password(self):
        while True:
            # Проверяем что логин не пустой
            login = input("Введите логин: ")
            if not login:
                print("Логин не может быть пустым")
                continue
            # Проверяем что код не пустой
            code = input("Введите код: ")
            if not code:
                print("Код не должен быть пустым")
                continue

            recovery_data = (login, code)
            # Запрос в базу данных который ищет пользователя с введенными логином и кодом
            self.cur.execute(
                """SELECT 1 FROM users_data 
                WHERE LOWER(Login) = LOWER(?) AND Code = (?)""", recovery_data)
            # Если такого пользователя с таким кодом нет, то вводим заново
            if not self.cur.fetchone():
                print("Неправильно введены логин или код. Попробуйте снова")
                continue
            # Если такой пользователь с таким кодом есть, останавливаем цикл и идем дальше
            break

        while True:
            print("Что вы хотите сделать?\n1.Восстановить пароль\n2.Изменить пароль")

            # Если выбрали восстановить пароль, то его показываем
            try:
                answer = int(input())
                if answer == 1:
                    self.cur.execute(
                        """SELECT Password FROM users_data
                        WHERE LOWER(Login) = LOWER(?)""", (login,)
                    )
                    value_recovery_password, = self.cur.fetchone()
                    print(f"Ваш пароль: {value_recovery_password}")
                    break
                # Если выбрали изменить пароль, то меняем
                elif answer == 2:
                    while True:
                        new_password = input("Введите новый пароль: ")
                        if not new_password:
                            print("Ошибка. Пароль не может быть пустым")
                            continue
                        break
                    # Запрос в бд для замены пароля новым
                    self.cur.execute(
                        """UPDATE users_data SET Password = (?)
                        WHERE LOWER(Login) = LOWER(?)""", (new_password, login)
                    )
                    self.db.commit()
                    print("Ваш пароль успешно изменен!")
                    break
                else:
                    print("Такого дейстия не существует. Попробуйте снова.")
                    continue
            except ValueError:
                print("Вы ввели недопустимое значение. Попробуйте снова")
                continue


test = UsersData()