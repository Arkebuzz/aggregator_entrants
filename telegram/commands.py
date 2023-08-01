"""
Задаёт параметры ответа бота
"""

import os

from aiogram import types
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from loader import dp
from .states import UniversityForm, PlaceForm
from utils.logger import logger

db = None


async def set_default_commands(database):
    """
    Задаёт список команд доступных пользователю
    """

    global db
    db = database

    await dp.bot.set_my_commands([
        types.BotCommand('/help', 'Показать справку'),
        types.BotCommand('/get_passing_points', 'Получить проходные баллы'),
        types.BotCommand('/get_your_place', 'Определить, куда вы поступите'),
        types.BotCommand('/help_for_getting_your_place', 'Справка к функции /get_your_place'),
        types.BotCommand('/info', 'Информация о боте')
    ])


@dp.message_handler(text=['/help', '/start'])
async def menu_action(message: Message):
    logger.info(f'{message.from_user.id} call for menu')

    await message.answer('Я могу помочь абитуриентам 2023 года в анализе конкурных списков.\n\n'

                         'Поддерживаемые ВУЗы: \n'
                         'МАИ, МГТУ Баумана (Москва и Мытищи), МИИГАиК, МИРЭА[1], МИСиС, МИФИ[2], МосПолитех[1], МТУСИ,'
                         ' МЭИ, РГУ Губкина, РЭУ Плеханова.\n'
                         '[1] - без учета количества платных мест,\n'
                         '[2] - без учёта количества мест.\n\n'

                         'Для просмотра проходных баллов в ВУЗы используй /get_passing_points\n\n'

                         'Для определения, куда ты поступишь в текущей конкурсной ситуации, используй '
                         '/get_your_place\n\n'

                         'Если результат предыдущей функции непонятен, используй дополнительную справку '
                         '/help_for_getting_your_place\n\n'

                         'Если ты хочешь узнать информацию о боте, вызови /info')


@dp.message_handler(text='/get_passing_points')
async def get_passing_points(message: Message):
    logger.info(f'{message.from_user.id} call get_passing_points')

    await message.answer('Введи название ВУЗа, проходные баллы которого ты хочешь получить: ')
    await UniversityForm.wait_name.set()


@dp.message_handler(state=UniversityForm.wait_name)
async def get_name4passing_points(message: Message, state: FSMContext):
    logger.info(f'{message.from_user.id} call get_name4passing_points')

    if os.path.isfile('is_updating'):
        await message.answer('Производится обновление БД ВУЗов, это может занять несколько минут, '
                             'результат данного запроса может быть неверным.')

    name = message.text

    free = db.get_prohodnoy(name, 0)
    paid = db.get_prohodnoy(name, 1)

    await message.answer('<b>Проходные на бюджетные направления:</b>')
    for i in range(0, len(free), 15):
        await message.answer('\n'.join(free[i: i + 15]))

    await message.answer('<b>Проходные на платные направления:</b>')
    for i in range(0, len(paid), 15):
        await message.answer('\n'.join(paid[i: i + 15]))

    await message.answer('Внимание, данный бот не гарантирует верность всей информации, для принятия важных '
                         'решений обращайтесь к официальным конкурсным спискам на сайте ВУЗа.')

    await state.finish()


@dp.message_handler(text='/get_your_place')
async def get_your_place(message: Message):
    logger.info(f'{message.from_user.id} call get_your_place')

    await message.answer('Введи СНИЛС или уникальный номер (без пробелов и тире): ')
    await PlaceForm.wait_name.set()


@dp.message_handler(state=PlaceForm.wait_name)
async def get_name4your_place(message: Message, state: FSMContext):
    logger.info(f'{message.from_user.id} call get_name4your_place')

    if os.path.isfile('is_updating'):
        await message.answer('Производится обновление БД ВУЗов, это может занять несколько минут, '
                             'результат данного запроса может быть неверным.')

    name = message.text

    data1 = db.get_place(name)
    data2 = db.get_place(name, False)

    text = '<b>Если все перед тобой подадут оригинал, ты поступишь на:</b>\n'
    if data1:
        for data in data1:
            text += f'{data[0]} - {data[1]} {"(договор)" if data[2] else "(бюджет)"}\nТы - {data[3]} по счёту, ' \
                    f'{data[4]}, если все перед тобой подадут оригиналы.\n'

    await message.answer(text)

    text = '<b>Судя по текущим данным о поданных оригиналах, ты поступишь на:</b>\n'
    if data2:
        data2 = data2[0]
        text += f'{data2[0]} - {data2[1]} {"(договор)" if data2[2] else "(бюджет)"}\nТы - {data2[3]} по счёту, ' \
                f'{data2[4]}, по подавшим оригинал, ещё {data2[5]} человек перед тобой могут подать оригинал.\n'

    await message.answer(text)

    await state.finish()


@dp.message_handler(text='/help_for_getting_your_place')
async def help_for_getting_your_place(message: Message):
    logger.info(f'{message.from_user.id} call help_for_getting_your_place')

    await message.answer(
        '<b>Справка к функции "/get_your_place"</b>\n\n'
        '<b>Пояснение к списку направлений "Если все перед тобой подадут оригинал, ты поступишь на":</b>\n'
        'Если ты уже подал аттестат, то в этом списке может быть только 1 направление из ВУЗа с аттестатом.\n'
        'Если аттестат ещё не подан, здесь будут ВУЗы, в которые ты можешь поступить, даже '
        'если все перед тобой подадут аттестат.\n'
        'Отсутствие результатов в этом списке означает, что ты не проходишь ни на одно направление, '
        'если все абитуриенты перед тобой подадут аттестат.\n\n'
        '<b>Пояснение к списку направлений "Судя по текущим данным о поданных оригиналах, ты поступишь на":</b>\n'
        'Здесь может быть максимум 1 направление из ВУЗа с аттестатом.\n'
        'Отсутствие результата в этом списке означает, что ты не проходишь ни на одно направление, '
        'в текущей конкурсной ситуации, либо ещё не подал аттестат ни в один ВУЗ.\n'
    )


@dp.message_handler(text='/info')
async def info(message: Message):
    logger.info(f'{message.from_user.id} call info')

    await message.answer(
        'Данный бот был создан для помощи абитуриентам 2023 года в анализе конкурных списков различных ВУЗов, '
        'на данный момент я умею работать с конкурсными списками МАИ, МГТУ Баумана (Москва и Мытищи), МИИГАиК, '
        'МИРЭА[1], МИСиС, МИФИ[2], МосПолитех[1], МТУСИ, МЭИ, РГУ Губкина, РЭУ Плеханова.\n'
        '[1] - без учета количества платных мест,\n'
        '[2] - без учёта количества мест.\n\n'
        'Код бота можешь увидеть на https://github.com/Arkebuzz/aggregator_entrants\n\n'
        'Если у тебя есть предложения по развитию данного проекта - пиши @Arkebuzz'
    )
