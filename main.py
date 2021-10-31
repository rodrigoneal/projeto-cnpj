import asyncio
import uuid

from aiohttp import web

from src.page import run
from src.captcha import captcha
from src.server import server
from src.resposta import Resposta

fila = asyncio.Queue()


def response(cnpj):
    _id = str(uuid.uuid4().int)
    return Resposta(_id, cnpj)


async def index(request):
    body = await request.json()
    cnpj = body['cnpj']
    await fila.put(response(cnpj))
    fila.task_done()
    return web.json_response(response(cnpj).to_json())


async def main():
    await asyncio.gather(server(index), *[run(fila, captcha, i) for i in range(1, 4)])


loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    pass
loop.close()
