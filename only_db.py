import asyncio
import time
import os

from utils.logger import logger_agr
from parsers import parsers
from utils.db import DB

db = DB()
loop = asyncio.new_event_loop()


def update():
    while True:
        logger_agr.info('Обновление конкурсных списков.')

        with open('is_updating', 'w') as f:
            f.write('1')

        for parser in parsers:
            try:
                logger_agr.info('Runing ' + parser.__name__)
                lists, univers = loop.run_until_complete(parser())
                db.delete_date('ranked_lists', university=univers[0][0])
                db.delete_date('universities', university=univers[0][0])
                db.new_university(univers)
                db.new_ranked_lists(lists)
            except Exception as e:
                logger_agr.warning('Ошибка парсинга:', e)

        logger_agr.info('Обрабатываем конкурсные списки.')
        db.sort()

        os.remove('is_updating')

        logger_agr.info('Операция успешно выполнена.')

        time.sleep(7200)


if __name__ == '__main__':
    if not os.path.isdir('data'):
        os.mkdir('data')

    a = input('Выбери действие цифрой:\n'
              '1) Обновление конкурсных списков;\n'
              '2) Определение куда ты поступишь по СНИЛС/Рег. номеру;\n'
              '3) Проходные баллы по абитуриентам, подавшим оригинал;\n'
              '4) Максимальные проходные баллы, считая, что все подали оригинал;\n'
              '5) Справка;\n'
              '0) Выход;\n')

    while a != '0':
        if a == '1':
            print()

            for parser in parsers:
                try:
                    print('Runing', parser.__name__)
                    lists, univers = loop.run_until_complete(parser())
                    db.delete_date('ranked_lists', university=univers[0][0])
                    db.delete_date('universities', university=univers[0][0])
                    db.new_university(univers)
                    db.new_ranked_lists(lists)
                except Exception as e:
                    print('Ошибка парсинга:', e)

            print('\nОбрабатываем конкурсные списки.')
            db.sort()
            print('\nОперация успешно выполнена.\n')

        elif a == '2':
            snils = input('\nТвой СНИЛС/Рег. номер (без пробелов и прочих символов): ')

            data1 = db.get_data(snils)
            data2 = db.get_data(snils, False)

            print('\nЕсли все перед тобой подадут оригинал, ты поступишь на: ')
            if data1:
                for data in data1:
                    print(f'{data[0]} - {data[1]}\nТы - {data[2]} по счёту, '
                          f'{data[3]}, если все перед тобой подадут оригиналы.\n')

            print(
                '*Если ты уже подал аттестат, то в этом списке может быть только 1 направление из ВУЗа с аттестатом.\n'
                'Если аттестат ещё не подан, здесь будут ВУЗы в которые ты можешь поступить, '
                'если все перед тобой подадут аттестат.\n'
                'Отсутствие результатов в этом списке означает, что ты не проходишь ни на одно направление, '
                'если все абитуриенты перед тобой подадут аттестат.\n'
            )

            print('\nСудя по текущим данным о поданных оригиналах, ты поступишь на: ')
            if data2:
                data2 = data2[0]
                print(f'{data2[0]} - {data2[1]}\nТы - {data2[2]} по счёту, '
                      f'{data2[3]}, по подавшим оригинал,\n')

            print('\n*Здесь может быть максимум 1 направление из ВУЗа с аттестатом.\n'
                  'Отсутствие результата в этом списке означает, что ты не проходишь ни на одно направление, '
                  'в текущей конкурсной ситуации, либо ещё не подал аттестат ни в один ВУЗ.\n')

        elif a == '3':
            print()
            data = input('Название ВУЗа: ')
            print(*db.get_prohodnoy(data, all_original=False), sep='\n')
            print()

        elif a == '4':
            print()
            data = input('Название ВУЗа: ')
            print(*db.get_prohodnoy(data), sep='\n')
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
