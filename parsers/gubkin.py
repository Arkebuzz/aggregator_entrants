import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def gubkin_parser():
    """Парсим РГУ Губкина."""

    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def foo(direct, tp=0):
            fin = '1' if not tp else '6'

            async with session.get(
                    f'https://transfer.priem.gubkin.ru/abiturients_list/api/api.php?act=search&method=get&educationTypeId={fin}&contestGroupId={direct[0]}'
            ) as rsp:
                abits = await rsp.json()
                abits = abits['data']

                direction = direct[1]
                places = direct[3] if tp else direct[2]
                n = 1

                for abit in abits:
                    snils = abit['snils'].replace('-', '').replace(' ', '')
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    score = abit['totalBalls'] if abit['totalBalls'] else 0
                    bvi = 1 if abit['benefit'] else 0
                    original = 1 if abit['originalExistence'] else 0
                    priority = abit['priority']

                    ranked_lists.append(('РГУ Губкина', direction, tp, n, snils, score, bvi, original, priority))

                    n += 1

                if n != 1:
                    universities.append(('РГУ Губкина', direction, tp, places))

        async with session.get('https://transfer.priem.gubkin.ru/live/') as resp1:
            name_dir = await resp1.text()
            soup = BeautifulSoup(name_dir, 'html.parser').find('table').find_all('tr', {'bgcolor': True})

            name_dir = {}
            for direct in soup:
                dt = direct.find_all('td')
                if len(dt) != 2:
                    name_dir[dt[0].text.split()[-1]] = dt[1].text[:-3]

        async with session.get(
                'https://transfer.priem.gubkin.ru/abiturients_list/api/api.php?act=search&method=getGroups&educationFormId=1&facultyId=666'
        ) as resp:
            data = await resp.json()
            data = [
                (i['id'],
                 'КГ ' + i['name'].split()[-1] + ' ' + name_dir[i['name'].split()[-1]],
                 i['budget_places'] - i['special_places'] - i['separate_places'] - i['target_places'],
                 i['commerce_places'])
                for i in data['data'] if 'Конкурсная группа' in i['name']
            ]

        tasks = []

        for direction in data:
            tasks.append(asyncio.create_task(foo(direction)))

        for direction in data:
            tasks.append(asyncio.create_task(foo(direction, 1)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(*loop.run_until_complete(gubkin_parser()), sep='\n')
