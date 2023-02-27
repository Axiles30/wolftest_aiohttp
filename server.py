import json
import random


from aiohttp import web

subscribed_clients = {}


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def registration(request):
    name = request.match_info.get('name', "Anonymous")
    reg = request.match_info.get('registration', '0')
    responttext = ''
    find = 0
    if reg == 'subscribe':
        for i in subscribed_clients:
            if i == name:
                find = 1
                responttext = 'user with this login is already subscribed'
        if find == 0:
            subscribed_clients[name] = reg
            responttext = 'Thank you for subscribe'

        print(f'find= {find}')
    if reg == 'unsubscribe':
        subscribed_clients.pop(name, None)
        responttext = 'User has been unsubscribed'
    if reg == 'send_quotes':
        with open("quotes.json", "r", encoding='utf-8') as file:
            quotes_open = json.load(file)
            index = str(random.randint(1, 20))
            random_quotes = quotes_open[index]
            # print(random_quotes)

            responttext = random_quotes
    print(subscribed_clients)
    return web.Response(text=f'{name}. {responttext}')


app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle),
                web.get('/{name}/{registration}', registration),
                ])

if __name__ == '__main__':
    web.run_app(app)
