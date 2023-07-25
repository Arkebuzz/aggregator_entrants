import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def mtuci_parser():
    connector = aiohttp.TCPConnector(limit=50, force_close=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        ranked_lists = []
        universities = []

        async def foo(url):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

            info = page.find_all('h4')[1].text
            tp = 0 if 'Бюджетное финансирование' in info else 1
            place = info.split()[-2].split('(')[-1]
            direction = page.find('h3', {'style': 'text-align: center; margin-top: 8px;'}).text
            abits = page.find('tbody').find_all('tr')

            for abit in abits:
                n = abit.contents[1].text
                snils = abit.contents[3].text.replace('-', '').replace(' ', '')
                snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)

                if len(abit.contents) == 9:
                    bvi = 1
                    score = None
                else:
                    bvi = 0
                    score = abit.contents[-5].text.split()[0]

                original = 1 if abit.contents[-4].text == 'Да' else 0
                priority = abit.contents[-3].text.split()[0]

                ranked_lists.append(('МТУСИ', direction, tp, n, snils, score, bvi, original, priority))

            universities.append(('МТУСИ', direction, tp, place))

        async with session.get('https://lk.abitur.mtuci.ru/mtuci-lists/view/concurs?id=83') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            contents = soup.find('div', {'class': 'body-content'}).find_all('a')
        async with session.get('https://lk.abitur.mtuci.ru/mtuci-lists/view/concurs?id=87') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            contents += soup.find('div', {'class': 'body-content'}).find_all('a')

        tasks = []

        for content in contents:
            tasks.append(asyncio.create_task(foo('https://lk.abitur.mtuci.ru/' + content['href'])))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(*loop.run_until_complete(mtuci_parser()), sep='\n')
