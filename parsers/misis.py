import asyncio

import aiohttp

from bs4 import BeautifulSoup


async def mospolytech_parser():
    """Парсим МосПолитех."""

    connector = aiohttp.TCPConnector(limit=50, force_close=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        ranked_lists = []
        universities = []

        async def foo(url, tp=0):
            async with session.get(url) as rsp:
                print(url)
                page = BeautifulSoup(await rsp.text(), 'html.parser')

                print(page)
                return

                direction = soup.find('a', {'href': "javascript:collapsElement('div4')"}).contents[3].contents[
                    1].text.strip()
                places = 10_000 if tp else soup.find('a', {'href': "javascript:collapsElement('div4')"}).contents[
                    3].contents[3].contents[0].text.split()[-1]
                n = 1

                abits = soup.find('table', {'border': '2', 'cellpadding': '3'}).find_all('tr', {'class': True})

                for abit in abits:
                    abit = abit.contents

                    if '0' in abit[39].text or '5' in abit[39].text:
                        snils = abit[5].text.strip().replace('-', '').replace(' ', '')
                        snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                        score = abit[23].text.strip() if abit[23].text.strip() else 0
                        bvi = 1 if '5' in abit[39].text else 0
                        original = 1 if 'да' in abit[27].text else 0
                        priority = abit[29].text

                        ranked_lists.append(('МосПолитех', direction, tp, n, snils, score, bvi, original, priority))

                        n += 1

                universities.append(('МосПолитех', direction, tp, places))

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
                in soup.find('div', {'id': 'tab-1-1'}).find('tbody').find_all('a', {'href': True})
            ]

        tasks = []

        for url in url_ok:
            tasks.append(asyncio.create_task(foo(url)))
            break

        # for url in url_pl:
        #     tasks.append(asyncio.create_task(foo(url, 1)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    loop.run_until_complete(mospolytech_parser())
