import asyncio
import functools

from aiohttp import web
from playwright.async_api import async_playwright
from captcha_breaker import Breakers

fila = asyncio.Queue()


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


@run_in_executor
def captcha(image):
    captcha = Breakers()
    token = captcha.image_captcha(image=image)
    return token


async def index(request):
    body = await request.json()
    cnpj = body['cnpj']
    await fila.put(cnpj)
    fila.task_done()
    return web.Response(text="OK")


async def run(name) -> None:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    # Open new page
    page = await context.new_page()
    page.set_default_timeout(1000000)
    await page.goto("https://servicos.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp")
    quebrado = False
    while True:
        if not quebrado:
            await page.click("#captchaSonoro")
            element_handle = await page.query_selector("#imgCaptcha")
            await element_handle.screenshot(path=f"screenshot{name}.png")
            token = await captcha(f"screenshot{name}.png")
            await page.fill('#txtTexto_captcha_serpro_gov_br', token)
            quebrado = True
        await asyncio.sleep(name/2)
        while not fila.empty():
            cnpj = await fila.get()
            print(name, cnpj)
            await page.fill("id=cnpj", cnpj)
            await page.click("button:has-text(\"Consultar\")")
            handle = await page.query_selector("xpath=/html/body/div[1]/div/div/div/div/div[2]/div/div/table["
                                               "1]/tbody/tr/td/table[3]/tbody/tr/td/font[2]/b")
            try:
                print(await handle.inner_text())
            except:
                pass
            await page.click('//*[@id="app"]/div/div/div/div/div[3]/div/div/div/button[2]')
            quebrado = False
            break


async def aio():
    server = web.Server(index)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print("======= Serving on http://127.0.0.1:8080/ ======")

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    await asyncio.sleep(100 * 3600)


async def main():
    await asyncio.gather(aio(), *[run(name=i) for i in range(1, 4)])


loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    pass
loop.close()

