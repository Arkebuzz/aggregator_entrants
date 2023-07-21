import asyncio

from db import DB
from parsers.mpei import mpei_parser

loop = asyncio.new_event_loop()
db = DB()

print('Парсим МЭИ.\n')
mpei = loop.run_until_complete(mpei_parser())

print('Обрабатываем конкурсные списки.')
db.new_university(mpei[1])
db.new_ranked_lists(mpei[0])
db.sort_data('МЭИ')

print('\nПредварительные действия успешно выполнены. Подготовка отчёта.\n')
snils = input('Твой снилс: ')
print()

data = db.get_data('ranked_lists', 'university, direction, number, really_number', snils='С' + snils)
for i in data:
    print(f'{i[0]} - {i[1]}\nТы - {i[2]} по счёту, {i[3]}, если все перед тобой подадут оригиналы.\n')

print('*Значение None означает, что ты не попадаешь.')
