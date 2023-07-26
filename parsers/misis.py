import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def misis_parser():

    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def foo(url, tp=0):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

                direction = page.find('direction').text
                places = page.find('contest').text

                abits = page.find('tbody').find_all('tr')
                n = 0

                for abit in abits:
                    abit = abit.find_all('td')

                    if 'ОК' in abit[11] or 'ОТК' in abit[11] or 'ЦП' in abit[11]:
                        continue

                    snils = abit[2].text.replace('-', '').replace(' ', '')
                    if not snils:
                        continue
                    snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                    score = abit[4].text
                    bvi = 1 if 'БВИ' in abit[11].text else 0
                    original = 1 if '+' in abit[12].text else 0
                    priority = abit[10].text

                    ranked_lists.append(('МИСиС', direction, tp, n, snils, score, bvi, original, priority))

                    n += 1

                universities.append(('МИСиС', direction, tp, places))

        async with session.get(
                f'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/'
        ) as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')

            url_ok = [
                'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/list/?' +
                d['href'].split('?')[-1] for d
                in soup.find('div', {'id': 'tab-1-1'}).find('tbody').find_all('a', {'href': True})
            ]

            url_pl = [
                'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/list/?' +
                d['href'].split('?')[-1] for d
                in soup.find('div', {'id': 'tab-1-3'}).find('tbody').find_all('a', {'href': True})
            ]

        tasks = []

        for url in url_ok:
            tasks.append(asyncio.create_task(foo(url)))

        for url in url_pl:
            tasks.append(asyncio.create_task(foo(url, 1)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    loop.run_until_complete(misis_parser())
