import asyncio
import json
import random

import aiohttp
from aiohttp import web


def load_quotes() :
	with open('quotes.json', 'r', encoding='utf-8') as f :
		data = json.load(f)
		return data


async def index(request) :
	with open("./templates/index.html", 'r', encoding='utf-8') as f :
		return web.Response(text=f.read(), content_type='text/html')


async def send_random_quote(quotes, web_socket):
	while True:
		_, quote = random.choice(list(quotes.items()))
		await web_socket.send_str(quote)
		await asyncio.sleep(10)


async def websocket_handler(request) :
	web_socket = web.WebSocketResponse()
	await web_socket.prepare(request)
	quotes = load_quotes()
	loop = asyncio.get_event_loop()

	task = None

	async for msg in web_socket :
		if msg.type == aiohttp.WSMsgType.TEXT :
			if msg.data == 'subscribe' :
				task = loop.create_task(send_random_quote(quotes, web_socket))
			elif msg.data == 'unsubscribe' :
				if task:
					task.cancel()

		elif msg.type == aiohttp.WSMsgType.ERROR :
			print('ws connection closed with exception %s' % web_socket.exception())

	print('websocket connection closed')

	return web_socket


app = web.Application()
app.add_routes([
	web.get('/', index),
	web.get('/ws', websocket_handler),
])

if __name__ == '__main__' :
	web.run_app(app)
