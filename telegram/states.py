from aiogram.dispatcher.filters.state import StatesGroup, State


class UniversityForm(StatesGroup):
    wait_name = State()


class PlaceForm(StatesGroup):
    wait_name = State()
