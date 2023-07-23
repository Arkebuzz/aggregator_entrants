import asyncio

from db import DB
from parsers.mpei import mpei_parser
from parsers.mtuci import mtuci_parser
from parsers.mirea import mirea_parser

loop = asyncio.new_event_loop()
db = DB()

a = input('Выбери действие цифрой:\n'
          '1) Обновление конкурсных списков;\n'
          '2) Определение куда ты поступишь по СНИЛС/Рег. номеру;\n'
          '3) Проходные баллы по абитуриентам, подавшим оригинал;\n'
          '4) Максимальные проходные баллы, считая, что все подали оригинал;\n'
          '5) Справка;\n'
          '0) Выход;\n')

while a != '0':
    if a == '1':
        print('\nПарсим МЭИ.')
        lists, univers = loop.run_until_complete(mpei_parser())
        db.new_university(univers)
        db.new_ranked_lists(lists)

        print('Парсим МТУСИ.')
        lists, univers = loop.run_until_complete(mtuci_parser())
        db.new_university(univers)
        db.new_ranked_lists(lists)

        print('Парсим МИРЭА.')
        lists, univers = loop.run_until_complete(mirea_parser())
        db.new_university(univers)
        db.new_ranked_lists(lists)

        print('\nОбрабатываем конкурсные списки.')
        db.sort()
        print('\nОперация успешно выполнена.\n')

    elif a == '2':
        snils = input('\nТвой СНИЛС/Рег. номер (без пробелов и прочих символов): ')
        print()

        data1 = db.get_data(snils)[0]
        data2 = db.get_data(snils, False)[0]

        print(f'{data1[0]} - {data1[1]}\nТы - {data1[2]} по счёту,\n'
              f'{data2[3]}, по подавшим оригинал,\n'
              f'{data1[3]}, если все перед тобой подадут оригиналы.\n')

    elif a == '3':
        print()
        print(*db.get_prohodnoy(False), sep='\n')
        print()

    elif a == '4':
        print()
        print(*db.get_prohodnoy(), sep='\n')
        print()

    elif a == '5':
        print('\nПеред первым использованием требуется обновить конкурсные списки,\n'
              'после этого можно определять своё место по СНИЛСУ или Регистрационному номеру.\n\n'
              'Для более тщательного анализа текущей ситуации рекомендуется открыть "data.db" в папке\n'
              'с данным скриптом и просмотреть интересуемые направления самостоятельно, это можно\n'
              'сделать, например, при помощи данной программы: https://sqlitebrowser.org/dl/\n\n'
              'Однако стоит учитывать, что база конкурсных списков собирается по ограниченному\n'
              'числу ВУЗов так, что окончательное решение принимайте только по оффициальным\n'
              'конкурсным спискам на оффициальных сайтах ВУЗов.\n\n'
              'Желаю удачи при поступлении!\n')

    else:
        print('\nВыбор не распознан.\n')

    a = input('Выбери действие цифрой:\n'
              '1) Обновление конкурсных списков;\n'
              '2) Определение куда ты поступишь по СНИЛС/Рег. номеру;\n'
              '3) Проходные баллы по абитуриентам подавшим оригинал;\n'
              '4) Максимальные проходные баллы, считая, что все подали оригинал;\n'
              '5) Справка;\n'
              '0) Выход;\n')
