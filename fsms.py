from aiogram.dispatcher.filters.state import StatesGroup, State


class Name(StatesGroup):
    anime = State()


class Manga(StatesGroup):
    manga = State()