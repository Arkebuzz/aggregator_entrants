import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def mai_parser():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def free(url):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

                direction = page.find('h4', {'class': 'mt-5 mb-3'}).text
                places = 0 if page.find('span').text == 'М' else page.find('span').text
                n = 1

                h4 = [i.text.split()[-3] for i in page.find_all('h4')[1:]]

                bvi = []
                ok = []

                for p in h4:
                    if p == 'без':
                        bvi = page.find_all('table')[h4.index(p)].find_all('tr')[1:]
                    if p == 'конкурсу':
                        ok = page.find_all('table')[h4.index(p)].find_all('tr')[1:]

                for abit in bvi:
                    abit = abit.contents

                    snils = abit[3].text.replace('-', '').replace(' ', '')
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    priority = abit[9].text

                    ranked_lists.append(('МАИ', direction, 0, n, snils, 0, 1, 0, priority))

                    n += 1

                for abit in ok:
                    abit = abit.contents

                    snils = abit[3].text.replace('-', '').replace(' ', '')
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    score = abit[5].text
                    original = 0 if 'Копия' in abit[13].text else 1
                    priority = abit[17].text

                    ranked_lists.append(('МАИ', direction, 0, n, snils, score, 0, original, priority))

                    n += 1

                universities.append(('МАИ', direction, 0, places))

        async def paid(url):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

                direction = page.find('h4', {'class': 'mt-5 mb-3'}).text
                places = page.find('b').text
                n = 1

                abits = page.find('table').find_all('tr')[1:]

                for abit in abits:
                    abit = abit.contents

                    snils = abit[3].text.replace('-', '').replace(' ', '')
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    score = abit[5].text
                    original = 0 if 'Копия' in abit[13].text else 1
                    priority = abit[17].text

                    ranked_lists.append(('МАИ', direction, 1, n, snils, score, 0, original, priority))

                    n += 1

                universities.append(('МАИ', direction, 1, places))

        async with session.get('https://priem.mai.ru/rating/') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            direct = soup.find_all('option')[1]['value']

        async with session.get('https://public.mai.ru/priem/rating/data/' + direct + '_l1_p1_f1.html') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser').find_all('option')[1:]
            urls_ok = ['https://public.mai.ru/priem/rating/data/' + url['value'] + '.html' for url in soup]

        async with session.get('https://public.mai.ru/priem/rating/data/' + direct + '_l1_p2_f1.html') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser').find_all('option')[1:]
            urls_pl = ['https://public.mai.ru/priem/rating/data/' + url['value'] + '.html' for url in soup]

        async with session.get('https://public.mai.ru/priem/rating/data/' + direct + '_l2_p1_f1.html') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser').find_all('option')[1:]
            urls_ok += ['https://public.mai.ru/priem/rating/data/' + url['value'] + '.html' for url in soup]

        async with session.get('https://public.mai.ru/priem/rating/data/' + direct + '_l2_p2_f1.html') as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser').find_all('option')[1:]
            urls_pl += ['https://public.mai.ru/priem/rating/data/' + url['value'] + '.html' for url in soup]

        tasks = []

        for url in urls_ok:
            tasks.append(asyncio.create_task(free(url)))

        for url in urls_pl:
            tasks.append(asyncio.create_task(paid(url)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(*loop.run_until_complete(mai_parser()), sep='\n')
