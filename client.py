import aiohttp
import asyncio

user = 'masha'
registr = 'subscribe'


async def main():
    async with aiohttp.ClientSession() as session:
        name_session = await name(session)
        subscribe_session = await server_request(session, 'subscribe')
        quotes_session = await server_request(session, 'send_quotes')
        # print(name_session)
        # print(subscribe_session)
        # print(quotes_session)


async def name(session):
    async with session.get(f'http://0.0.0.0:8080/{user}') as response:
        print("Status:", response.status)
        html = await response.text()
        print(html[:255], "...")


async def server_request(session, param):
    async with session.get(f'http://0.0.0.0:8080/{user}/{param}') as response:
        print("Status:", response.status)
        quotes = await response.text()
        print(quotes[:255], "...")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
