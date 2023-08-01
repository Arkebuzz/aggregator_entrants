import asyncio

from ast import literal_eval

import aiohttp

from bs4 import BeautifulSoup


async def miigaik_parser():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def foo(url, direction, place, tp=0):
            async with session.get(url) as resp:
                abits = await resp.json()

            n = 1

            for abit in abits['abiturients']:
                snils = abit['code'].replace('-', '').replace(' ', '')
                snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                score = abit.setdefault('points_all', 0)
                bvi = 0
                original = 1 if abit['doc_type'] else 0
                priority = abit['priority']

                ranked_lists.append(('МИИГАиК', direction, tp, n, snils, score, bvi, original, priority))

                n += 1

            universities.append(('МИИГАиК', direction, tp, place))

        async with session.get('https://www.miigaik.ru/applicants/number/') as rsp:
            drs = BeautifulSoup(await rsp.text(), 'html.parser').find_all('tr')
            places = {}

            for dr in drs[5:18] + drs[19:21]:
                dr = dr.find_all('td')
                places[(dr[0].text.strip() + ' ' + ' '.join(dr[1].text.split()), 0)] = int(dr[-1].text)

            for dr in drs[47:64] + drs[65:67]:
                dr = dr.find_all('td')
                places[(dr[0].text.strip() + ' ' + ' '.join(dr[1].text.split()), 1)] = int(dr[2].text)

        async with session.get('https://abiturient.miigaik.ru/api/v1/specialities') as rsp:
            res = literal_eval(await rsp.text())

            url_ok = []
            url_pl = []

            for direct in res:
                if direct['edu_level_id'] in '12':
                    pl_ok = places.setdefault((direct['spec_code'] + ' ' + direct['speciality'], 0), -1)
                    pl_pl = places.setdefault((direct['spec_code'] + ' ' + direct['speciality'], 1), -1)

                    if pl_ok != -1:
                        url_ok.append(
                            (f'https://abiturient.miigaik.ru/api/v1/abiturient-list?speciality={direct["id"]}&'
                             f'edu_level={direct["edu_level_id"]}&edu_form=1&finance=1',
                             direct['spec_code'] + ' ' + direct['speciality'],
                             pl_ok)
                        )

                    if pl_pl != -1:
                        url_pl.append(
                            (f'https://abiturient.miigaik.ru/api/v1/abiturient-list?speciality={direct["id"]}&'
                             f'edu_level={direct["edu_level_id"]}&edu_form=1&finance=2',
                             direct['spec_code'] + ' ' + direct['speciality'],
                             pl_pl)
                        )

        tasks = []

        for url in url_ok:
            tasks.append(asyncio.create_task(foo(*url)))

        for url in url_pl:
            tasks.append(asyncio.create_task(foo(*url, 1)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(loop.run_until_complete(miigaik_parser()))
