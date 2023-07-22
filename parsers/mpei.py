import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def mpei_parser():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def paid(url, n=1, tp=1):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

            direction = page.find('div', {'class': 'competitive-group'}).text
            place = page.find('div', {'class': 'title1'}).contents[4].text.split()[-1]
            abits = page.find_all('tr', {'class': 'accepted'})

            for n, abit in enumerate(abits, n):
                snils = abit.contents[0].text
                if snils[0] == 'С':
                    snils = 'С' + snils[-11:]
                else:
                    snils = 'Н' + snils[-7:]

                score = abit.contents[1].text
                original = 1 if abit.contents[-6].text == 'да' else 0
                priority = abit.contents[-4].text

                ranked_lists.append(('МЭИ', direction, tp, n, snils, score, 0, original, priority))

            universities.append(('МЭИ', direction, tp, place))

        async def budget(url1, url2):
            async with session.get(url1) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

            direction = page.find('div', {'class': 'competitive-group'}).text
            abits = page.find_all('tr', {'class': 'accepted'})

            n = 0

            for n, abit in enumerate(abits, 1):
                snils = abit.contents[0].text
                if snils[0] == 'С':
                    snils = 'С' + snils[-11:]
                else:
                    snils = 'Н' + snils[-7:]

                score = abit.contents[2].text
                original = 1 if abit.contents[-5].text == 'да' else 0
                priority = abit.contents[-4].text

                ranked_lists.append(('МЭИ', direction, 0, n, snils, score, 1, original, priority))

            await paid(url2, n + 1, 0)

        async with session.get('https://pk.mpei.ru/inform/list.html') as resp:
            contents = await resp.text()

        soup = BeautifulSoup(contents, 'html.parser').find('tbody', {'class': 'groupFilterMoscow'})

        tasks = []
        contents = soup.find_all('a', {'class': 'competitive-group listFilterBudget'})

        for i in range(0, len(contents), 2):
            tasks.append(asyncio.create_task(budget(
                'https://pk.mpei.ru/' + contents[i]['href'],
                'https://pk.mpei.ru/' + contents[i + 1]['href']
            )))

        contents = soup.find_all('a', {'class': 'competitive-group listFilterContract'})

        for content in contents:
            tasks.append(asyncio.create_task(paid('https://pk.mpei.ru/' + content['href'])))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(*loop.run_until_complete(mpei_parser()), sep='\n')
