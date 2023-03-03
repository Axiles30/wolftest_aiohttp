import asyncio
import json
import random

import aiohttp
from aiohttp import web


def register_user() :
	with open("users.json", "r") as f :
		users = json.load(f)

	while True :
		login = input("Введите логин: ")
		if login in users :
			print("Пользователь с таким логином уже зарегистрирован")
		else :
			break

	password = input("Введите пароль: ")
	user = {"login" : login, "password" : hash(password)}
	users[login] = user

	with open("users.json", "w") as f :
		json.dump(users, f)

	print("Пользователь успешно зарегистрирован")

"""
Объявляем функцию load_quotes, 
которая загружает цитаты из файла JSON и возвращает их в виде словаря.
"""
def load_quotes() :
	with open('quotes.json', 'r', encoding='utf-8') as f :
		data = json.load(f)
		return data

"""
Обьявляем асинхронную функцию index, 
которая обрабатывает запрос на главную страницу и возвращает содержимое файла index.html.
"""
async def index(request) :
	with open("./templates/index.html", 'r', encoding='utf-8') as f :
		"""Создаем объект Response из модуля web и возвращает его как ответ на запрос. 
			Объект Response содержит текстовое содержимое файла index.html и тип содержимого 'text/html'."""
		return web.Response(text=f.read(), content_type='text/html')


"""
Обьявляем асинхронную функцию send_random_quote, 
которая отправляет случайно выбранную цитату из словаря quotes по веб-сокету web_socket.
"""
async def send_random_quote(quotes, web_socket):
	while True:
		"""выбираем случайную цитату из словаря quotes и присваивает ее переменной quote."""
		_, quote = random.choice(list(quotes.items()))
		"""отправляем цитату на web_socket в виде строки."""
		await web_socket.send_str(quote)
		"""приостанавливаем выполнение функции на 10 секунд перед выбором следующей случайной цитаты."""
		await asyncio.sleep(10)


"""
Обьявляем асинхронную функцию websocket_handler, 
которая обрабатывает запрос на подключение к веб-сокету.
"""
async def websocket_handler(request) :
	"""создаем объект веб-сокета."""
	web_socket = web.WebSocketResponse()
	"""подготавливаем веб-сокет к работе."""
	await web_socket.prepare(request)
	"""загружаем цитаты из файла JSON."""
	quotes = load_quotes()
	"""получаем текущий цикл событий asyncio."""
	loop = asyncio.get_event_loop()

	task = None
	"""запускаем цикл асинхронной итерации для чтения сообщений из веб-сокета."""
	async for msg in web_socket :
		"""проверяем, является ли сообщение текстовым."""
		if msg.type == aiohttp.WSMsgType.TEXT :
			"""проверяем, была ли отправлена команда подписаться на рассылку цитат."""
			if msg.data == 'subscribe' :
				"""создаем задачу asyncio для отправки случайной цитаты через определенный интервал времени."""
				task = loop.create_task(send_random_quote(quotes, web_socket))
				"""проверяем, была ли отправлена команда отписаться от рассылки цитат."""
			elif msg.data == 'unsubscribe' :
				"""отменяем задачу отправки цитат, если она была создана."""
				if task:
					task.cancel()
			"""проверяем, является ли сообщение ошибкой веб-сокета."""
		elif msg.type == aiohttp.WSMsgType.ERROR :
			print('ws connection closed with exception %s' % web_socket.exception())

	print('websocket connection closed')

	return web_socket

"""создаем объект приложения веб-сервера из модуля web."""
app = web.Application()
"""
	Добавляем маршруты веб-страниц для приложения, 
	используя метод add_routes объекта приложения. 
	Маршруты определяются в виде списка и передаются в качестве аргумента в виде списка кортежей, 
	каждый из которых содержит путь маршрута и функцию-обработчик запроса.
"""
app.add_routes([
	web.get('/', index),
	web.get('/ws', websocket_handler),
])

if __name__ == '__main__' :
	web.run_app(app)
