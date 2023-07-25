import multiprocessing as mp
import os

from aiogram import executor

from loader import dp


async def start(dp):
    await set_default_commands(db)
    logger.info("Bot has been started")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.isdir('data'):
        os.mkdir('data')

    from only_db import update
    from telegram.commands import set_default_commands
    from utils.logger import logger
    from utils.db import DB

    db = DB()

    pr = mp.Process(target=update)
    pr.start()
    logger.info("Task has been started (update)")

    executor.start_polling(dp, on_startup=start, skip_updates=True)
