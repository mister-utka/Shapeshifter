import random
import string

from flask import Flask, abort, send_file
import smtplib
from email.mime.text import MIMEText


config_url = {
    "prefics_url":"media="                              # Статичный префикс фишинговой ссылки, после него идет радномно сгенерированная строка
}
config_file_upload = {
    "filename":"test.txt"                               # Файл, который будет отгружаться пользователю (следующиая идея -> уникальный файл для каждой ссылки)
}
config_mail = {
    "username":"user1@exemple.com",                     # От имени кого будет отправляться сообщение
    "password":"password",                              # Пароль от данного пользователя
    "server":"192.168.1.1",                             # Адрес почтового сервера
    "fishing_server":"192.168.1.2",                     # Web сервер, откуда будет скачиваться файл (будет указан в фишинговой ссылке)
    "fishing_url":"/download",                          # Адрес url для фишинговых файлов
}
fishing_user_mail = [
    "user2@exemple.com"                                 # Пользователи, которым будут отправлены фишинговые письма
]

random_urls = {}


app = Flask(__name__)               # Создаем экземпляр приложения Flask
                                    # __name__ специальная переменная, которая содержит имя текущего модуля


def send_email(subject, message, mail_server, from_addr, to_addr, password):
    msg['Subject'] = subject                        # Заголовок письма
    msg = MIMEText(message)                         # Текст письма
    msg['From'] = from_addr                         # От кого письмо        
    msg['To'] = to_addr                             # Кому письмо
    server = smtplib.SMTP(mail_server, 587)         # Указываем параметры сервера
    
    server.starttls()                               # Устанавливаем коннект с сервером
    server.login(from_addr, password)               # Логинимся  
    server.send_message(msg)                        # Отправляем сообщение
    server.quit()                                   # разрываем соединение


def generate_random_string(length_string_output: int) -> str:
    letters = string.ascii_lowercase                                                # Получаем строку со всеми маленькими буквами английского алфавита
    random_letters = [random.choice(letters) for _ in range(length_string_output)]  # Генерируем список случайных букв указанной длины (random.choice() выбирает случайный элемент из строки letters)
    result = ''.join(random_letters)                                                # Собираем буквы в одну строку
    return result


def generate_random_url(number_random_url: int):
    for i in range(number_random_url):
        random_postfix_url = generate_random_string(50)                         # Получаем радномный постфикс url адреса
        result_random_url = config_url["prefics_url"] + random_postfix_url      # Добавдяем перед ним префикс
        random_urls[result_random_url] = 1                                      # Сохраняем его с префиком в словарь. 1 - значит что url активен и обрабатыает запрос


@app.route("/download/<password_url>")
def download(password_url):

    urls = list(random_urls.keys())             # Получаем все url адреса из словаря
    
    if password_url in urls:                    # Если запрошенный url является одним из сгенерированных, то идем дальше
        
        if random_urls[password_url] == 1:      # Если статут этого url адреса активен, то идем дальше
            random_urls[password_url] = 0       # После это деактивируем его, чтобы второй запрос не прошел
            #return(password_url)
            return send_file(
                config_file_upload["filename"],
                as_attachment=True,                             # Автоматически добавляет Content-Disposition: attachment
                download_name=config_file_upload["filename"]    # Указывает имя для скачивания
            )
        else:
            abort(404)                          # Если url адрес деактивирован
    else:
        abort(404)                              # Если url адрес впринципе не нашелся


def start_fishing():
    
    generate_random_url(len(fishing_user_mail)) # Получаем словарь с рандомными url и их статусом активен/не активен
    
    urls = list(random_urls.keys())             # Получаем все url адреса из словаря
    i = 0                                       # Счетчик, чтобы у каждого пользователя была уникальная ссылка

    for user_mail in fishing_user_mail:

        send_email(
            "Test massage",
            f"Hello! The test massage! http://{config_mail['fishing_server']}{config_mail['fishing_url']}/{urls[i]}",
            config_mail["server"],
            config_mail["username"],
            user_mail,
            config_mail["password"]
        )
        i += 1


if __name__ == "__main__":

    print("[i] Start WEB server")
    app.run(host='127.0.0.1', port=80) #, debug=True)

    print("[i] Start Fishaing...")
    start_fishing()
    
















# @app.route("/")                     # В данном случае маршрутизация, это связывание url с функциями обработки
#                                     # Декоратор указывает, что функция ниже обрабатывает get запросы к корневому url
# def home():
#     return("Hello World!")

# @app.route("/hello/<name>")
# def hello_name(name):
#     return f"Привет, {name}!"
