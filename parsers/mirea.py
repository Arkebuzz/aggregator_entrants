import asyncio

import aiohttp

from bs4 import BeautifulSoup

urls_ok = [
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748193468849593654',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205351209016630',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205344227597622',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205333570919734',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205461187861814',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205454286134582',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205428624334134',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205422769085750',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205535757344054',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205531612323126',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205591555218742',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205581416537398',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205567742057782',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205685050449206',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205659639258422',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205653593169206',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205718460177718',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205707438595382',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205764814576950',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205377727503670',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205371509447990',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205364832116022',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205448598658358',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205442851413302',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205436693126454',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205527259684150',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205522704670006',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205519868271926',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205515758902582',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205512494685494',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205505111661878',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205498687036726',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205492169088310',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205486659870006',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205604742110518',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205598518811958',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205585424194870',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205574846160182',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205560341208374',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205677892869430',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205671651745078',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205665905548598',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205647265013046',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205626934172982',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205737335594294',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205728456252726',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205722184719670',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205711439961398',
]

urls_pl = [
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748193468851690806',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205377729600822',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205371511545142',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205364834213174',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1764954821715041590',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205351211113782',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205344229694774',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205333573016886',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205461189958966',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205454288231734',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205448600755510',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205442853510454',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205436695223606',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205428626431286',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205422771182902',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205535759441206',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205531614420278',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205527261781302',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205522706767158',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205519870369078',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205515760999734',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205512496782646',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205505113759030',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205498689133878',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205492171185462',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205486661967158',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205604744207670',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205598520909110',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205591557315894',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205585426292022',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205581418634550',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205574848257334',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205567744154934',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205560343305526',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205685052546358',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205677894966582',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205671653842230',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205665907645750',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205659641355574',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205653595266358',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205647267110198',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205626936270134',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205749790580022',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205743833619766',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205737337691446',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205733962325302',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205728458349878',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205722186816822',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205718462274870',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205711442058550',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205707440692534',
    'https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748205764816674102'
]


async def mirea_parser():
    async with aiohttp.ClientSession() as session:
        ranked_lists = []
        universities = []

        async def paid(url):

            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

            direction = page.find('p', {'class': 'namesListPlan'}).contents[2].text.split('/')[0]
            abits = page.find('tr', {'id': True}).find_all('td')
            places = 10_000
            n = 1

            for i in range(0, len(abits), 9):
                abit = abits[i:i + 9]

                snils = abit[1].text.replace('-', '').replace(' ', '')
                snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                score = abit[8].text
                original = 1 if abit[3].text == 'да' else 0
                priority = abit[2].text

                ranked_lists.append(('МИРЭА', direction, 1, n, snils, score, 0, original, priority))

                n += 1

            universities.append(('МИРЭА', direction, 1, places))

        async def free(url):
            async with session.get(url) as rsp:
                page = BeautifulSoup(await rsp.text(), 'html.parser')

            direction = page.find('p', {'class': 'namesListPlan'}).contents[2].text.split('/')[0]
            abits = page.find_all('tr', {'id': True})
            places = page.find('div', {'style': 'text-align: center'}).contents[0].text.split()[-1]

            n = 1

            for abit in abits:
                abit = abit.contents

                snils = abit[1].text.replace('-', '').replace(' ', '')
                snils = ('Н' + snils) if len(snils) != 11 else ('С' + snils)
                score = abit[11].text
                original = 1 if abit[5].text == 'да' else 0
                priority = abit[2].text

                ranked_lists.append(('МИРЭА', direction, 0, n, snils, score, 0, original, priority))

                n += 1

            universities.append(('МИРЭА', direction, 0, places))

        tasks = []

        for url in urls_pl:
            tasks.append(asyncio.create_task(paid(url)))

        for url in urls_ok:
            tasks.append(asyncio.create_task(free(url)))

        await asyncio.gather(*tasks)

        return ranked_lists, universities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    print(loop.run_until_complete(mirea_parser()), sep='\n')
