import asyncio
import json
import random

import aiohttp
from aiohttp import web


subscribers = []


class ClientStatuMessages:
	ERROR = 'error'
	SUBSCRIBED = 'subscribed'
	UNSUBSCRIBED = 'unsubscribed'

async def send_quotes(quotes):
	"""
	Short desc
	:param quotes: quotes as list of dicts
	"""
	while True:
		_, quote = random.choice(list(quotes.items()))
		message = {'quote': quote}
		for websocket in subscribers:
			try :
				await websocket.send_str(json.dumps(message))
			except ConnectionError:
				subscribers.remove(websocket)
				print('Subscriber removed.')

		await asyncio.sleep(10)



"""
Объявляем функцию load_quotes, 
которая загружает цитаты из файла JSON и возвращает их в виде словаря.
"""



def load_quotes():
	with open('quotes.json', 'r', encoding='utf-8') as f :
		data = json.load(f)
		return data


"""
Обьявляем асинхронную функцию index, 
которая обрабатывает запрос на главную страницу и возвращает содержимое файла index.html.
"""


async def index(request):
	with open("templates/index.html", 'r', encoding='utf-8') as f :
		return web.Response(text=f.read(), content_type='text/html')



"""
Обьявляем асинхронную функцию websocket_handler, 
которая обрабатывает запрос на подключение к веб-сокету.
"""

async def websocket_handler(request):
	websocket = web.WebSocketResponse()
	await websocket.prepare(request)


	"""Запускаем цикл асинхронной итерации для чтения сообщений из веб-сокета."""
	async for msg in websocket:
		status_message = {
			'status': ClientStatuMessages.UNSUBSCRIBED
		}
		if websocket in subscribers:
			status_message['status'] = ClientStatuMessages.SUBSCRIBED
		if msg.type == aiohttp.WSMsgType.TEXT:
			message_data = json.loads(msg.data)
			if message_data.get('status') == ClientStatuMessages.SUBSCRIBED:
				subscribers.append(websocket)
				status_message['status'] = ClientStatuMessages.SUBSCRIBED
			elif message_data.get('status') == ClientStatuMessages.UNSUBSCRIBED:
				subscribers.remove(websocket)
				status_message['status'] = ClientStatuMessages.UNSUBSCRIBED
			await websocket.send_str(json.dumps(status_message))
		elif msg.type == aiohttp.WSMsgType.ERROR :
			status_message['status'] = ClientStatuMessages.ERROR
			await websocket.send_str(json.dumps(status_message))
			print('ws connection closed with exception %s' % websocket.exception())

	print('websocket connection closed')

	return websocket


async def main():
	quotes = load_quotes()
	app = web.Application()
	app.add_routes([
		web.get('/', index),
		web.get('/ws', websocket_handler),
	])
	loop = asyncio.get_event_loop()
	asyncio.run_coroutine_threadsafe(send_quotes(quotes), loop)
	return app



if __name__ == '__main__':
	web.run_app(main())
