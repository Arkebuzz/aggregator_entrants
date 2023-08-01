import asyncio
import os

import aiohttp
import aiofiles
from PyPDF2 import PdfReader


def pdf_reader(file, tp=0, name='МГТУ Баумана (Москва)'):
    rl = []

    reader = PdfReader(file)

    desc = reader.pages[0].extract_text().replace('\n', ' ')

    ind1 = desc.find(':')
    ind2 = desc.find('–')

    direction = desc[ind1 + 2: ind2 - 1]

    ind = desc.find('мест')

    if tp:
        place = desc[ind - 10: ind].split()[-1]
    else:
        place = desc[ind + 5: ind + 10].split()[0]

    flag = True

    for p in reader.pages:
        txt = p.extract_text()

        for line in txt.split('\n'):
            if 'Поступающие на места ' in line:
                flag = False
                continue

            if flag:
                continue

            line = line.split()

            if len(line) < 13:
                continue

            k1 = 0
            n = line[0]

            if '/' in n:
                snils = n[-11:].replace('-', '').replace(' ', '')
                n = n[:-11]
                k1 -= 1

            else:
                snils = line[1].replace('-', '').replace(' ', '')

            if len(snils) != 9:
                snils = 'Н' + snils
                k = 0
            else:
                snils = 'С' + snils + line[k1 + 2]
                k = 1

            if snils == 'Нвыделенное':
                continue

            score = line[3 + k] if '?' not in line[3 + k] else 0
            original = 1 if 'Да' in line[-3] else 0
            priority = line[-2]

            rl.append((name, direction, tp, n, snils, score, 0, original, priority))

    univ = [name, direction, tp, place]
    os.remove(file)

    return rl, univ


async def bmstu_parser_moscow():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def foo(dr):
            name = dr['title']
            dr = 'https://priem.bmstu.ru' + dr['file']

            async with session.get(dr) as rsp:
                f = await aiofiles.open(f'{name}.pdf', mode='wb')
                await f.write(await rsp.read())
                await f.close()

            return f'{name}.pdf'

        async with session.get('https://priem.bmstu.ru/lists/upload/enrollees/first/MGTU-1/meta.json') as resp:
            dirs = await resp.json()

        tasks = []

        for direction in dirs['list']:
            tasks.append(asyncio.create_task(foo(direction)))

        for file in await asyncio.gather(*tasks):
            rl, univ = pdf_reader(file)
            ranked_lists.extend(rl)
            universities.append(univ)

        async with session.get('https://priem.bmstu.ru/lists/upload/enrollees/first/MGTU-0/meta.json') as resp:
            dirs = await resp.json()

        tasks = []

        for direction in dirs['list']:
            tasks.append(asyncio.create_task(foo(direction)))

        for file in await asyncio.gather(*tasks):
            rl, univ = pdf_reader(file, 1)
            ranked_lists.extend(rl)
            universities.append(univ)

        return ranked_lists, universities


async def bmstu_parser_mitishi():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def foo(dr):
            name = dr['title']
            dr = 'https://priem.bmstu.ru' + dr['file']

            async with session.get(dr) as rsp:
                f = await aiofiles.open(f'{name}.pdf', mode='wb')
                await f.write(await rsp.read())
                await f.close()

            return f'{name}.pdf'

        async with session.get('https://priem.bmstu.ru/lists/upload/enrollees/first/MF-1/meta.json') as resp:
            dirs = await resp.json()

        tasks = []

        for direction in dirs['list']:
            tasks.append(asyncio.create_task(foo(direction)))

        for file in await asyncio.gather(*tasks):
            rl, univ = pdf_reader(file, name='МГТУ Баумана (Мытищи)')
            ranked_lists.extend(rl)
            universities.append(univ)

        async with session.get('https://priem.bmstu.ru/lists/upload/enrollees/first/MF-0/meta.json') as resp:
            dirs = await resp.json()

        tasks = []

        for direction in dirs['list']:
            tasks.append(asyncio.create_task(foo(direction)))

        for file in await asyncio.gather(*tasks):
            rl, univ = pdf_reader(file, 1, 'МГТУ Баумана (Мытищи)')
            ranked_lists.extend(rl)
            universities.append(univ)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(loop.run_until_complete(bmstu_parser_moscow()), sep='\n')
    print(loop.run_until_complete(bmstu_parser_mitishi()), sep='\n')
