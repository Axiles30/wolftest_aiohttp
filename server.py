import asyncio
import json
import random
from pprint import pprint

import aiohttp
from aiohttp import web


subscribers = []


async def send_quotes(quotes) :
	while True :
		_, quote = random.choice(list(quotes.items()))
		for websocket in subscribers :
			try :
				await websocket.send_str(quote)
			except ConnectionError:
				subscribers.remove(websocket)
				print('Subscriber removed.')

		await asyncio.sleep(10)




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


async def send_random_quote(quotes, web_socket) :
	while True :
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
	websocket = web.WebSocketResponse()
	"""подготавливаем веб-сокет к работе."""
	await websocket.prepare(request)

	"""запускаем цикл асинхронной итерации для чтения сообщений из веб-сокета."""
	async for msg in websocket :
		"""проверяем, является ли сообщение текстовым."""
		if msg.type == aiohttp.WSMsgType.TEXT :
			"""проверяем, была ли отправлена команда подписаться на рассылку цитат."""
			if msg.data == 'subscribe' :
				"""создаем задачу asyncio для отправки случайной цитаты через определенный интервал времени."""
				subscribers.append(websocket)
				"""проверяем, была ли отправлена команда отписаться от рассылки цитат."""
			elif msg.data == 'unsubscribe' :
				"""отменяем задачу отправки цитат, если она была создана."""
				subscribers.remove(websocket)
			"""проверяем, является ли сообщение ошибкой веб-сокета."""
		elif msg.type == aiohttp.WSMsgType.ERROR :
			print('ws connection closed with exception %s' % websocket.exception())

	print('websocket connection closed')

	return websocket


async def main() :
	quotes = load_quotes()
	#loop = asyncio.get_event_loop()
	#loop.run_until_complete(send_quotes(quotes))
	#task =


	app = web.Application()
	app.add_routes([
		web.get('/', index),
		web.get('/ws', websocket_handler),
	])
	loop = asyncio.get_event_loop()

	asyncio.run_coroutine_threadsafe(send_quotes(quotes), loop)
	return app


"""создаем объект приложения веб-сервера из модуля web."""

"""
	Добавляем маршруты веб-страниц для приложения, 
	используя метод add_routes объекта приложения. 
	Маршруты определяются в виде списка и передаются в качестве аргумента в виде списка кортежей, 
	каждый из которых содержит путь маршрута и функцию-обработчик запроса.
"""

if __name__ == '__main__' :
	web.run_app(main())
