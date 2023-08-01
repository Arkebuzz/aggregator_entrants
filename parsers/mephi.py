import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def mephi_parser():
    async with (aiohttp.ClientSession() as session):
        ranked_lists = []
        universities = []

        async def foo(url, tp=0):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

                if 'Нет заявлений' in page.text:
                    return

                direction = page.find('tr').text.strip()
                places = 10000

                abits = page.find_all('tr', {'class': 'trPosBen'})
                n = 1

                for abit in abits:
                    abit = abit.find_all('td')

                    snils = abit[1].text.strip().replace('-', '').replace(' ', '')
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    score = abit[4].text if '-' not in abit[4].text else 0
                    original = 1 if 'Оригинал' in abit[5].text else 0
                    priority = abit[7].text

                    ranked_lists.append(('МИФИ', direction, tp, n, snils, score, 0, original, priority))

                    n += 1

                universities.append(('МИФИ', direction, tp, places))

        async with session.get(f'https://org.mephi.ru/pupil-rating') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')

            directs = soup.find('table', {'class': 'w100'}).find_all('tr')[2:]

            url_ok = []
            url_pl = []

            for direct in directs:
                direct = direct.find_all('td')

                if (('бакалавриат, бюджет, очная форма' in direct[0].text or
                     'специалитет, бюджет, очная форма' in direct[0].text) and not
                ('Особая квота' in direct[0].text or 'Отдельная квота' in direct[0].text or
                 'Целевой прием' in direct[0].text)):
                    url_ok += ['https://org.mephi.ru/' + direct[1].find('a')['href']]

                elif ('бакалавриат, платное, очная форма' in direct[0].text or 'специалитет, платное, очная форма' in
                      direct[0].text):
                    url_pl += ['https://org.mephi.ru/' + direct[1].find('a')['href']]

        tasks = []

        for url in url_ok:
            tasks.append(asyncio.create_task(foo(url)))

        for url in url_pl:
            tasks.append(asyncio.create_task(foo(url, 1)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(loop.run_until_complete(mephi_parser()))
