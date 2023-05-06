from aiogram import types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
menu_btn = ['⟡Search Anime⟡', '⟡Search Manga⟡','⟡Search Character⟡', '⟡Trending Anime⟡', '⟡Trending Manga⟡', '⟡Visit web-site⟡',  '⟡About⟡', '⟡Random AniGIF⟡']
menu.add(*menu_btn)
lang = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
lang_btn = ['🇷🇺','🇬🇧']