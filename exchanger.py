import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Exchanger:
    def __init__(self):
        self.db = sqlite3.connect('exchanger.db')
        self.cur = self.db.cursor()
        self.create_database()
        self.exchange_rates = self.get_exchange_rates()
        self.want_currency = None
        self.have_currency = None
        self.sum_exchange = None

    def create_database(self):
        """Метод создания базы данных и вноса баланса"""
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users_balance (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Balance_RUB FLOAT,
            Balance_USD FLOAT,
            Balance_EUR FLOAT
        );""")
        self.db.commit()

        self.cur.execute("SELECT 1 FROM users_balance WHERE UserID=?", (1,))
        if not self.cur.fetchone():
            self.cur.execute("""INSERT INTO users_balance (Balance_RUB, Balance_USD, Balance_EUR)
            VALUES (?, ?, ?);""", (100000, 1000, 1000))
            self.db.commit()

    def get_exchange_rates(self):
        """Метод для сбора курса валют с сайта"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

        rates = {}

        rate_urls = {
            "usd_rub": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=RUB",
            "eur_rub": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=EUR&To=RUB",
            "rub_usd": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=RUB&To=USD",
            "rub_eur": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=RUB&To=EUR",
            "usd_eur": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=EUR",
            "eur_usd": "https://www.xe.com/currencyconverter/convert/?Amount=1&From=EUR&To=USD"
        }

        rate_locator = "//p[@class='sc-63d8b7e3-1 bMdPIi']"

        for key, url in rate_urls.items():
            driver.get(url)
            rate_element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, rate_locator)))
            rate_value = rate_element.text.split(' ')[0]
            rates[key] = round(float(rate_value), 2)

        driver.quit()
        return rates

    def get_want_currency(self):
        """Метод для вывода курсов валют и определения желаемой валюты"""
        # Вывод курсов валют
        print(f"Добро пожаловать в наш обменный пункт, курс валют следующий:")
        print(f"1 USD = {self.exchange_rates['usd_rub']} RUB")
        print(f"1 EUR = {self.exchange_rates['eur_rub']} RUB")
        print(f"1 USD = {self.exchange_rates['usd_eur']} EUR")
        print(f"1 EUR = {self.exchange_rates['eur_usd']} USD")

        currency_options = {1: "RUB", 2: "USD", 3: "EUR"}

        while True:
            try:
                num_currency = int(input("Введите какую валюту желаете получить:\n1. RUB\n2. USD\n3. EUR\n"))
                if num_currency in currency_options:
                    return currency_options[num_currency]
                else:
                    print("Вы ввели некорректный номер. Выберите валюту снова")
            except ValueError:
                print("Вы ввели некорректный символ. Попробуйте снова")

    def input_sum(self):
        """Метод для ввода суммы желаемой валюты"""
        while True:
            try:
                sum_exchange = float(input("Какая сумма Вас интересует?\n"))
                return sum_exchange
            except ValueError:
                print("Вы ввели некорректное значение. Попробуйте снова")

    def get_have_currency(self):
        """Метод для определения имеющейся валюты"""
        currency_options = {1: "RUB", 2: "USD", 3: "EUR"}

        while True:
            try:
                num_have_currency = int(input("Какую валюту готовы предложить взамен?\n1. RUB\n2. USD\n3. EUR\n"))
                if num_have_currency in currency_options:
                    return currency_options[num_have_currency]
                else:
                    print("Вы ввели некорректный номер. Выберите валюту снова")
            except ValueError:
                print("Вы ввели некорректный символ. Попробуйте снова")

    def do_exchange(self):
        """Метод для обмена валют"""
        # Получаем данные о желаемой волюте, сумме и валюты на обмен
        self.want_currency = self.get_want_currency()
        self.sum_exchange = self.input_sum()
        self.have_currency = self.get_have_currency()

        if self.want_currency == self.have_currency:
            print("Ошибка. Невозможно производить обмен двух одинаковых валют")
            return

        # Словарь для сопоставления валют с колонками в бд
        balance_columns = {"RUB": "Balance_RUB", "USD": "Balance_USD", "EUR": "Balance_EUR"}

        # Получение текущих балансов
        self.cur.execute(f"SELECT {balance_columns[self.have_currency]} FROM users_balance WHERE UserID = 1")
        have_balance = self.cur.fetchone()[0]
        self.cur.execute(f"SELECT {balance_columns[self.want_currency]} FROM users_balance WHERE UserID = 1")
        want_balance = self.cur.fetchone()[0]

        # Расчет обмена
        exchange_key = f"{self.have_currency.lower()}_{self.want_currency.lower()}"
        if exchange_key not in self.exchange_rates:
            print("Ошибка: обмен между указанными валютами невозможен.")
            return

        amount_needed = self.sum_exchange / self.exchange_rates[exchange_key]

        # Проверка баланса
        if have_balance < amount_needed:
            print(f"Ошибка, на балансе недостаточно средств для обмена. "
                  f"Требуется {amount_needed} {self.have_currency}, доступно: {have_balance} {self.have_currency}.")
            return

        # Обновление балансов
        self.cur.execute(
            f"""
            UPDATE users_balance 
            SET {balance_columns[self.have_currency]} = {balance_columns[self.have_currency]} - ?, 
                {balance_columns[self.want_currency]} = {balance_columns[self.want_currency]} + ? 
            WHERE UserID = 1
            """, (amount_needed, self.sum_exchange)
        )

        # Сохраняем изменения
        self.db.commit()
        print(f"Успешный обмен {amount_needed:.2f} {self.have_currency} на {self.sum_exchange:.2f} {self.want_currency}.")


test = Exchanger()
test.do_exchange()