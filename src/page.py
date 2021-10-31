import asyncio

from playwright.async_api import async_playwright


def limpar_codigo(elemento):
    elemento = elemento.split('\n', maxsplit=1)
    cabeca = elemento[0]
    texto = elemento[-1].replace('\n', " ").strip()
    resp = {'header': cabeca, 'body': texto}
    return resp


async def crawler(page):
    inscricao = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[2]/tbody/tr/td[1]")
    abertura = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[2]/tbody/tr/td[3]")
    nome = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[3]/tbody/tr/td")
    fantasia = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[4]/tbody/tr/td[1]")
    porta = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[4]/tbody/tr/td[3]")
    atividade_principal = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[5]/tbody/tr/td")
    atividade_secundaria = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[6]/tbody/tr/td")
    natureza = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[7]/tbody/tr/td")
    logradouro = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[8]/tbody/tr/td[1]")
    numero = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[8]/tbody/tr/td[3]")
    complemento = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[8]/tbody/tr/td[5]")
    cep = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[9]/tbody/tr/td[1]")
    bairro = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[9]/tbody/tr/td[3]")
    municipio = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[9]/tbody/tr/td[5]")
    uf = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[9]/tbody/tr/td[7]")
    email = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[10]/tbody/tr/td[1]")
    telefone = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[10]/tbody/tr/td[3]")
    efr = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[11]/tbody/tr/td[3]")
    cadastral = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[12]/tbody/tr/td[1]")
    data_cadastral = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[12]/tbody/tr/td[3]")
    situacao_cadastral = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[13]/tbody/tr/td")
    situacao_especial = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[14]/tbody/tr/td[1]")
    data_situacao_especial = await page.query_selector("xpath = //table[1]/tbody/tr/td/table[14]/tbody/tr/td[3]")

    elementos = [inscricao, abertura, nome, fantasia,
                 porta, atividade_principal, atividade_secundaria,
                 natureza, logradouro, numero, complemento,
                 cep, bairro, municipio, uf, email, telefone,
                 efr, cadastral, data_cadastral, situacao_cadastral,
                 situacao_especial, data_situacao_especial]
    response = []
    for elemento in elementos:
        try:
            _elemento = await elemento.inner_text()
        except AttributeError:
            breakpoint()
        response.append(limpar_codigo(_elemento))
    return response


async def break_captcha(page, captcha, _id):
    await page.click("#captchaSonoro")
    element_handle = await page.query_selector("#imgCaptcha")
    await element_handle.screenshot(path=f"screenshot{_id}.png")
    token = await captcha(f"screenshot{_id}.png")
    await page.fill('#txtTexto_captcha_serpro_gov_br', token)
    return page


async def run(fila, captcha, _id) -> None:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    # Open new page
    page = await context.new_page()
    page.set_default_timeout(1000000)
    await page.goto("https://servicos.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp")
    while True:
        await asyncio.sleep(_id / 2)
        while not fila.empty():
            resposta = await fila.get()
            print(f" O navegador {_id} vai processar o cnpj {resposta.cnpj}")
            await break_captcha(page, captcha, _id)
            await page.fill("id=cnpj", resposta.cnpj)
            await page.click("button:has-text(\"Consultar\")")
            text = await crawler(page)
            print(text)
            await page.click('//*[@id="app"]/div/div/div/div/div[3]/div/div/div/button[2]')
            break
